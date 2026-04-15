from django.core.management.base import BaseCommand

from api.models import Choice, Question, Survey


class Command(BaseCommand):
    help = "Заполняет базу демонстрационным опросом"

    def handle(self, *args, **options):
        survey, _ = Survey.objects.get_or_create(
            slug="customer-satisfaction",
            defaults={
                "title": "Оценка качества сервиса",
                "description": "Демонстрационный опрос для проверки GraphQL API.",
                "is_active": True,
            },
        )

        questions_data = [
            {
                "title": "Насколько вам понравился сервис?",
                "question_type": Question.QuestionType.SINGLE_CHOICE,
                "order": 1,
                "choices": [
                    ("Отлично", "excellent"),
                    ("Хорошо", "good"),
                    ("Удовлетворительно", "normal"),
                    ("Плохо", "bad"),
                ],
            },
            {
                "title": "Какие функции вы использовали?",
                "question_type": Question.QuestionType.MULTIPLE_CHOICE,
                "order": 2,
                "choices": [
                    ("Создание анкет", "create_forms"),
                    ("Заполнение опросов", "submit_forms"),
                    ("Просмотр статистики", "stats"),
                ],
            },
            {
                "title": "Что можно улучшить?",
                "question_type": Question.QuestionType.TEXT,
                "order": 3,
                "choices": [],
            },
            {
                "title": "Оцените сервис по шкале от 1 до 10",
                "question_type": Question.QuestionType.NUMBER,
                "order": 4,
                "choices": [],
            },
            {
                "title": "Порекомендуете ли вы сервис знакомым?",
                "question_type": Question.QuestionType.BOOLEAN,
                "order": 5,
                "choices": [],
            },
        ]

        for question_data in questions_data:
            question, _ = Question.objects.get_or_create(
                survey=survey,
                order=question_data["order"],
                defaults={
                    "title": question_data["title"],
                    "question_type": question_data["question_type"],
                    "is_required": True,
                },
            )
            for index, (text, value) in enumerate(question_data["choices"], start=1):
                Choice.objects.get_or_create(
                    question=question,
                    value=value,
                    defaults={
                        "text": text,
                        "order": index,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Демонстрационные данные созданы или уже существуют."))
