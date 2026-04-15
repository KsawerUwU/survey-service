from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Survey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("slug", models.SlugField(max_length=255, unique=True, verbose_name="Краткий идентификатор")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлен")),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Опрос",
                "verbose_name_plural": "Опросы",
            },
        ),
        migrations.CreateModel(
            name="SurveySubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("respondent_name", models.CharField(blank=True, max_length=255, verbose_name="Имя респондента")),
                ("respondent_email", models.EmailField(blank=True, max_length=254, verbose_name="Email респондента")),
                ("metadata", models.JSONField(blank=True, default=dict, verbose_name="Дополнительные метаданные")),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Интегральный показатель",
                    ),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True, verbose_name="Отправлено")),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="api.survey",
                        verbose_name="Опрос",
                    ),
                ),
            ],
            options={
                "ordering": ["-submitted_at"],
                "verbose_name": "Прохождение опроса",
                "verbose_name_plural": "Прохождения опросов",
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Текст вопроса")),
                ("description", models.TextField(blank=True, verbose_name="Подсказка")),
                (
                    "question_type",
                    models.CharField(
                        choices=[
                            ("single_choice", "Один вариант"),
                            ("multiple_choice", "Несколько вариантов"),
                            ("text", "Текст"),
                            ("number", "Число"),
                            ("boolean", "Логический"),
                        ],
                        max_length=32,
                        verbose_name="Тип вопроса",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_required", models.BooleanField(default=True, verbose_name="Обязательный")),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="api.survey",
                        verbose_name="Опрос",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "id"],
                "verbose_name": "Вопрос",
                "verbose_name_plural": "Вопросы",
                "unique_together": {("survey", "order")},
            },
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(max_length=255, verbose_name="Отображаемый текст")),
                ("value", models.CharField(max_length=100, verbose_name="Значение")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="api.question",
                        verbose_name="Вопрос",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "id"],
                "verbose_name": "Вариант ответа",
                "verbose_name_plural": "Варианты ответов",
                "unique_together": {("question", "value")},
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text_answer", models.TextField(blank=True, verbose_name="Текстовый ответ")),
                (
                    "number_answer",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        verbose_name="Числовой ответ",
                    ),
                ),
                ("boolean_answer", models.BooleanField(blank=True, null=True, verbose_name="Логический ответ")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="api.question",
                        verbose_name="Вопрос",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="api.surveysubmission",
                        verbose_name="Прохождение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ",
                "verbose_name_plural": "Ответы",
                "unique_together": {("submission", "question")},
            },
        ),
        migrations.CreateModel(
            name="AnswerChoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "answer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="selected_choices",
                        to="api.answer",
                        verbose_name="Ответ",
                    ),
                ),
                (
                    "choice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answer_links",
                        to="api.choice",
                        verbose_name="Вариант",
                    ),
                ),
            ],
            options={
                "verbose_name": "Выбранный вариант",
                "verbose_name_plural": "Выбранные варианты",
                "unique_together": {("answer", "choice")},
            },
        ),
    ]
