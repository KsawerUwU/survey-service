from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import Count

from api.models import Answer, AnswerChoice, Choice, Question, Survey, SurveySubmission


class SurveyValidationError(Exception):
    """Ошибка валидации пользовательских ответов."""


@dataclass
class NormalizedAnswerPayload:
    question: Question
    text_value: str | None = None
    number_value: Decimal | None = None
    boolean_value: bool | None = None
    choice_ids: list[int] | None = None


def _normalize_answer(question: Question, raw_answer: Any) -> NormalizedAnswerPayload:
    choice_ids = [int(item) for item in (getattr(raw_answer, "choice_ids", None) or [])]
    text_value = getattr(raw_answer, "text_value", None)
    number_value = getattr(raw_answer, "number_value", None)
    boolean_value = getattr(raw_answer, "boolean_value", None)

    if question.question_type == Question.QuestionType.TEXT:
        if not text_value:
            raise SurveyValidationError(f"Вопрос '{question.title}' требует текстовый ответ.")
        return NormalizedAnswerPayload(question=question, text_value=text_value)

    if question.question_type == Question.QuestionType.NUMBER:
        if number_value is None:
            raise SurveyValidationError(f"Вопрос '{question.title}' требует числовой ответ.")
        return NormalizedAnswerPayload(question=question, number_value=Decimal(str(number_value)))

    if question.question_type == Question.QuestionType.BOOLEAN:
        if boolean_value is None:
            raise SurveyValidationError(f"Вопрос '{question.title}' требует логический ответ.")
        return NormalizedAnswerPayload(question=question, boolean_value=bool(boolean_value))

    if question.question_type == Question.QuestionType.SINGLE_CHOICE:
        if len(choice_ids) != 1:
            raise SurveyValidationError(
                f"Для вопроса '{question.title}' необходимо выбрать ровно один вариант."
            )
        return NormalizedAnswerPayload(question=question, choice_ids=choice_ids)

    if question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
        if not choice_ids:
            raise SurveyValidationError(
                f"Для вопроса '{question.title}' необходимо выбрать хотя бы один вариант."
            )
        return NormalizedAnswerPayload(question=question, choice_ids=choice_ids)

    raise SurveyValidationError(f"Неизвестный тип вопроса: {question.question_type}")


def submit_survey_response(data: Any) -> SurveySubmission:
    survey = (
        Survey.objects.filter(slug=data.survey_slug, is_active=True)
        .prefetch_related("questions__choices")
        .first()
    )
    if not survey:
        raise SurveyValidationError("Активный опрос с указанным slug не найден.")

    question_map = {question.id: question for question in survey.questions.all()}
    submitted_answers = list(getattr(data, "answers", []) or [])

    if not submitted_answers:
        raise SurveyValidationError("Невозможно отправить пустой набор ответов.")

    answered_question_ids = {int(answer.question_id) for answer in submitted_answers}
    required_questions = {q.id for q in survey.questions.filter(is_required=True)}
    missed_required = required_questions - answered_question_ids
    if missed_required:
        titles = ", ".join(
            survey.questions.filter(id__in=missed_required).values_list("title", flat=True)
        )
        raise SurveyValidationError(
            f"Не заполнены обязательные вопросы: {titles}."
        )

    normalized_answers: list[NormalizedAnswerPayload] = []
    for raw_answer in submitted_answers:
        question_id = int(raw_answer.question_id)
        question = question_map.get(question_id)
        if question is None:
            raise SurveyValidationError(f"Вопрос с идентификатором {question_id} не принадлежит опросу.")
        normalized_answers.append(_normalize_answer(question, raw_answer))

    with transaction.atomic():
        submission = SurveySubmission.objects.create(
            survey=survey,
            respondent_name=getattr(data, "respondent_name", "") or "",
            respondent_email=getattr(data, "respondent_email", "") or "",
            metadata=getattr(data, "metadata", None) or {},
            score=getattr(data, "score", None),
        )

        for item in normalized_answers:
            answer = Answer.objects.create(
                submission=submission,
                question=item.question,
                text_answer=item.text_value or "",
                number_answer=item.number_value,
                boolean_answer=item.boolean_value,
            )
            if item.choice_ids:
                valid_choice_ids = set(item.question.choices.values_list("id", flat=True))
                invalid_ids = sorted(set(item.choice_ids) - valid_choice_ids)
                if invalid_ids:
                    raise SurveyValidationError(
                        f"В вопросе '{item.question.title}' выбраны недопустимые варианты: {invalid_ids}"
                    )
                AnswerChoice.objects.bulk_create(
                    [AnswerChoice(answer=answer, choice_id=choice_id) for choice_id in item.choice_ids]
                )

    return submission


def build_question_statistics(survey_slug: str) -> list[dict[str, Any]]:
    survey = (
        Survey.objects.filter(slug=survey_slug)
        .prefetch_related(
            "questions__choices",
            "questions__answers__selected_choices__choice",
        )
        .first()
    )
    if not survey:
        raise SurveyValidationError("Опрос для построения статистики не найден.")

    result: list[dict[str, Any]] = []
    for question in survey.questions.all():
        answers = list(question.answers.all())
        base_row: dict[str, Any] = {
            "question_id": question.id,
            "title": question.title,
            "question_type": question.question_type,
            "total_answers": len(answers),
            "choice_stats": [],
            "text_answers": [],
            "average_number": None,
            "true_count": None,
            "false_count": None,
        }

        if question.question_type in {
            Question.QuestionType.SINGLE_CHOICE,
            Question.QuestionType.MULTIPLE_CHOICE,
        }:
            counter = (
                AnswerChoice.objects.filter(answer__question=question)
                .values("choice_id", "choice__text", "choice__value")
                .annotate(count=Count("id"))
                .order_by("choice__text")
            )
            base_row["choice_stats"] = [
                {
                    "choice_id": row["choice_id"],
                    "label": row["choice__text"],
                    "value": row["choice__value"],
                    "count": row["count"],
                }
                for row in counter
            ]

        elif question.question_type == Question.QuestionType.TEXT:
            base_row["text_answers"] = [
                answer.text_answer for answer in answers if answer.text_answer
            ]

        elif question.question_type == Question.QuestionType.NUMBER:
            values = [float(answer.number_answer) for answer in answers if answer.number_answer is not None]
            base_row["average_number"] = round(sum(values) / len(values), 2) if values else None

        elif question.question_type == Question.QuestionType.BOOLEAN:
            true_count = sum(1 for answer in answers if answer.boolean_answer is True)
            false_count = sum(1 for answer in answers if answer.boolean_answer is False)
            base_row["true_count"] = true_count
            base_row["false_count"] = false_count

        result.append(base_row)

    return result
