from __future__ import annotations

import strawberry
from strawberry.scalars import JSON


@strawberry.input
class ChoiceInput:
    text: str
    value: str
    order: int = 0


@strawberry.input
class QuestionInput:
    title: str
    description: str = ""
    question_type: str = "text"
    order: int = 0
    is_required: bool = True
    choices: list[ChoiceInput] | None = None


@strawberry.input
class CreateSurveyInput:
    title: str
    slug: str
    description: str = ""
    is_active: bool = True
    questions: list[QuestionInput] | None = None


@strawberry.input
class AnswerInput:
    question_id: strawberry.ID
    text_value: str | None = None
    number_value: float | None = None
    boolean_value: bool | None = None
    choice_ids: list[strawberry.ID] | None = None


@strawberry.input
class SubmitSurveyInput:
    survey_slug: str
    respondent_name: str | None = None
    respondent_email: str | None = None
    metadata: JSON | None = None
    score: int | None = None
    answers: list[AnswerInput]
