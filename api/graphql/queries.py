from __future__ import annotations

import strawberry

from api.models import Survey, SurveySubmission
from api.services.submission_service import build_question_statistics

from .types import SubmissionType, SurveyType, QuestionStatisticsType, build_statistics_type


@strawberry.type
class Query:
    @strawberry.field(description="Проверка доступности API")
    def health(self) -> str:
        return "ok"

    @strawberry.field(description="Получить список опросов")
    def surveys(self, active_only: bool = True) -> list[SurveyType]:
        queryset = Survey.objects.prefetch_related("questions__choices").all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        return [SurveyType.from_model(obj) for obj in queryset]

    @strawberry.field(description="Получить анкету по slug")
    def survey_by_slug(self, slug: str) -> SurveyType | None:
        survey = Survey.objects.prefetch_related("questions__choices").filter(slug=slug).first()
        if survey is None:
            return None
        return SurveyType.from_model(survey)

    @strawberry.field(description="Получить список прохождений опроса")
    def submissions_by_survey(self, survey_slug: str) -> list[SubmissionType]:
        queryset = (
            SurveySubmission.objects.filter(survey__slug=survey_slug)
            .prefetch_related("answers__selected_choices__choice")
            .order_by("-submitted_at")
        )
        return [SubmissionType.from_model(obj) for obj in queryset]

    @strawberry.field(description="Построить статистику по вопросам")
    def question_statistics(self, survey_slug: str) -> list[QuestionStatisticsType]:
        rows = build_question_statistics(survey_slug=survey_slug)
        return [build_statistics_type(row) for row in rows]
