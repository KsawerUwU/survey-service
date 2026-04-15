from django.test import TestCase

from api.models import Choice, Question, Survey
from api.services.submission_service import submit_survey_response


class InputAnswer:
    def __init__(self, question_id, text_value=None, number_value=None, boolean_value=None, choice_ids=None):
        self.question_id = question_id
        self.text_value = text_value
        self.number_value = number_value
        self.boolean_value = boolean_value
        self.choice_ids = choice_ids or []


class SubmitInput:
    def __init__(self, survey_slug, answers, respondent_name="", respondent_email="", metadata=None, score=None):
        self.survey_slug = survey_slug
        self.answers = answers
        self.respondent_name = respondent_name
        self.respondent_email = respondent_email
        self.metadata = metadata or {}
        self.score = score


class SubmissionServiceTests(TestCase):
    def setUp(self):
        self.survey = Survey.objects.create(title="Test", slug="test", is_active=True)
        self.q1 = Question.objects.create(
            survey=self.survey,
            title="Оценка",
            question_type=Question.QuestionType.SINGLE_CHOICE,
            order=1,
            is_required=True,
        )
        self.c1 = Choice.objects.create(question=self.q1, text="Да", value="yes", order=1)

        self.q2 = Question.objects.create(
            survey=self.survey,
            title="Комментарий",
            question_type=Question.QuestionType.TEXT,
            order=2,
            is_required=True,
        )

    def test_submit_valid_answers(self):
        data = SubmitInput(
            survey_slug="test",
            respondent_name="User",
            answers=[
                InputAnswer(question_id=self.q1.id, choice_ids=[self.c1.id]),
                InputAnswer(question_id=self.q2.id, text_value="Все хорошо"),
            ],
        )

        submission = submit_survey_response(data)

        self.assertEqual(submission.respondent_name, "User")
        self.assertEqual(submission.answers.count(), 2)
