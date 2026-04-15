from django.test import TestCase

from api.models import Answer, AnswerChoice, Choice, Question, Survey, SurveySubmission
from api.services.submission_service import build_question_statistics


class StatisticsTests(TestCase):
    def setUp(self):
        survey = Survey.objects.create(title="Stats", slug="stats", is_active=True)
        question = Question.objects.create(
            survey=survey,
            title="Выбор",
            question_type=Question.QuestionType.SINGLE_CHOICE,
            order=1,
            is_required=True,
        )
        choice = Choice.objects.create(question=question, text="Вариант 1", value="one", order=1)
        submission = SurveySubmission.objects.create(survey=survey, respondent_name="A")
        answer = Answer.objects.create(submission=submission, question=question)
        AnswerChoice.objects.create(answer=answer, choice=choice)

    def test_statistics_contains_counts(self):
        rows = build_question_statistics("stats")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["choice_stats"][0]["count"], 1)
