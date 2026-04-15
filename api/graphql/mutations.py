from __future__ import annotations

from django.db import transaction

import strawberry

from api.models import Choice, Question, Survey
from api.services.submission_service import SurveyValidationError, submit_survey_response

from .inputs import CreateSurveyInput, SubmitSurveyInput
from .types import MutationResult, SubmissionPayload, SubmissionType, SurveyType


def _validate_question_input(question_input) -> None:
    if question_input.question_type in {"single_choice", "multiple_choice"} and not question_input.choices:
        raise SurveyValidationError(
            f"Вопрос '{question_input.title}' должен содержать список вариантов ответа."
        )


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Создать новый опрос")
    def create_survey(self, data: CreateSurveyInput) -> SurveyType:
        with transaction.atomic():
            survey = Survey.objects.create(
                title=data.title,
                slug=data.slug,
                description=data.description,
                is_active=data.is_active,
            )
            for question_input in data.questions or []:
                _validate_question_input(question_input)
                question = Question.objects.create(
                    survey=survey,
                    title=question_input.title,
                    description=question_input.description,
                    question_type=question_input.question_type,
                    order=question_input.order,
                    is_required=question_input.is_required,
                )
                for choice_input in question_input.choices or []:
                    Choice.objects.create(
                        question=question,
                        text=choice_input.text,
                        value=choice_input.value,
                        order=choice_input.order,
                    )

        survey = Survey.objects.prefetch_related("questions__choices").get(pk=survey.pk)
        return SurveyType.from_model(survey)

    @strawberry.mutation(description="Изменить статус активности опроса")
    def set_survey_active(self, survey_id: strawberry.ID, is_active: bool) -> MutationResult:
        updated_count = Survey.objects.filter(pk=int(survey_id)).update(is_active=is_active)
        if updated_count == 0:
            return MutationResult(ok=False, message="Опрос не найден.")
        return MutationResult(ok=True, message="Статус опроса обновлен.")

    @strawberry.mutation(description="Отправить пользовательские ответы")
    def submit_survey(self, data: SubmitSurveyInput) -> SubmissionPayload:
        try:
            submission = submit_survey_response(data)
        except SurveyValidationError as exc:
            return SubmissionPayload(ok=False, message=str(exc), submission=None)

        submission = (
            submission.__class__.objects.filter(pk=submission.pk)
            .prefetch_related("answers__selected_choices__choice")
            .get()
        )
        return SubmissionPayload(
            ok=True,
            message="Ответы успешно сохранены.",
            submission=SubmissionType.from_model(submission),
        )
