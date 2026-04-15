from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import strawberry

from api import models


@strawberry.type
class ChoiceType:
    id: strawberry.ID
    text: str
    value: str
    order: int

    @classmethod
    def from_model(cls, obj: models.Choice) -> "ChoiceType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            text=obj.text,
            value=obj.value,
            order=obj.order,
        )


@strawberry.type
class QuestionType:
    id: strawberry.ID
    title: str
    description: str
    question_type: str
    order: int
    is_required: bool
    choices: list[ChoiceType]

    @classmethod
    def from_model(cls, obj: models.Question) -> "QuestionType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            title=obj.title,
            description=obj.description,
            question_type=obj.question_type,
            order=obj.order,
            is_required=obj.is_required,
            choices=[ChoiceType.from_model(choice) for choice in obj.choices.all()],
        )


@strawberry.type
class SurveyType:
    id: strawberry.ID
    title: str
    slug: str
    description: str
    is_active: bool
    created_at: str
    updated_at: str
    questions: list[QuestionType]

    @classmethod
    def from_model(cls, obj: models.Survey) -> "SurveyType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            title=obj.title,
            slug=obj.slug,
            description=obj.description,
            is_active=obj.is_active,
            created_at=obj.created_at.isoformat(),
            updated_at=obj.updated_at.isoformat(),
            questions=[QuestionType.from_model(question) for question in obj.questions.all()],
        )


@strawberry.type
class SelectedChoiceType:
    id: strawberry.ID
    choice: ChoiceType

    @classmethod
    def from_model(cls, obj: models.AnswerChoice) -> "SelectedChoiceType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            choice=ChoiceType.from_model(obj.choice),
        )


@strawberry.type
class AnswerType:
    id: strawberry.ID
    question_id: strawberry.ID
    text_answer: str | None
    number_answer: str | None
    boolean_answer: bool | None
    selected_choices: list[SelectedChoiceType]

    @classmethod
    def from_model(cls, obj: models.Answer) -> "AnswerType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            question_id=strawberry.ID(str(obj.question_id)),
            text_answer=obj.text_answer or None,
            number_answer=str(obj.number_answer) if obj.number_answer is not None else None,
            boolean_answer=obj.boolean_answer,
            selected_choices=[
                SelectedChoiceType.from_model(item) for item in obj.selected_choices.select_related("choice").all()
            ],
        )


@strawberry.type
class SubmissionType:
    id: strawberry.ID
    respondent_name: str | None
    respondent_email: str | None
    score: int | None
    submitted_at: str
    answers: list[AnswerType]

    @classmethod
    def from_model(cls, obj: models.SurveySubmission) -> "SubmissionType":
        return cls(
            id=strawberry.ID(str(obj.id)),
            respondent_name=obj.respondent_name or None,
            respondent_email=obj.respondent_email or None,
            score=obj.score,
            submitted_at=obj.submitted_at.isoformat(),
            answers=[
                AnswerType.from_model(answer)
                for answer in obj.answers.prefetch_related("selected_choices__choice").all()
            ],
        )


@strawberry.type
class MutationResult:
    ok: bool
    message: str


@strawberry.type
class SubmissionPayload:
    ok: bool
    message: str
    submission: SubmissionType | None = None


@strawberry.type
class ChoiceStatType:
    choice_id: strawberry.ID
    label: str
    value: str
    count: int


@strawberry.type
class QuestionStatisticsType:
    question_id: strawberry.ID
    title: str
    question_type: str
    total_answers: int
    choice_stats: list[ChoiceStatType]
    text_answers: list[str]
    average_number: float | None
    true_count: int | None
    false_count: int | None


def build_statistics_type(row: dict) -> QuestionStatisticsType:
    return QuestionStatisticsType(
        question_id=strawberry.ID(str(row["question_id"])),
        title=row["title"],
        question_type=row["question_type"],
        total_answers=row["total_answers"],
        choice_stats=[
            ChoiceStatType(
                choice_id=strawberry.ID(str(item["choice_id"])),
                label=item["label"],
                value=item["value"],
                count=item["count"],
            )
            for item in row["choice_stats"]
        ],
        text_answers=row["text_answers"],
        average_number=row["average_number"],
        true_count=row["true_count"],
        false_count=row["false_count"],
    )
