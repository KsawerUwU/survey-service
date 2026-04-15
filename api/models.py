from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Краткий идентификатор")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = "single_choice", "Один вариант"
        MULTIPLE_CHOICE = "multiple_choice", "Несколько вариантов"
        TEXT = "text", "Текст"
        NUMBER = "number", "Число"
        BOOLEAN = "boolean", "Логический"

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Опрос",
    )
    title = models.CharField(max_length=255, verbose_name="Текст вопроса")
    description = models.TextField(blank=True, verbose_name="Подсказка")
    question_type = models.CharField(
        max_length=32,
        choices=QuestionType.choices,
        verbose_name="Тип вопроса",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_required = models.BooleanField(default=True, verbose_name="Обязательный")

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("survey", "order")
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self) -> str:
        return f"{self.survey.title}: {self.title}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Вопрос",
    )
    text = models.CharField(max_length=255, verbose_name="Отображаемый текст")
    value = models.CharField(max_length=100, verbose_name="Значение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("question", "value")
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

    def __str__(self) -> str:
        return f"{self.question.title}: {self.text}"


class SurveySubmission(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Опрос",
    )
    respondent_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Имя респондента",
    )
    respondent_email = models.EmailField(
        blank=True,
        verbose_name="Email респондента",
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Дополнительные метаданные")
    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Интегральный показатель",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Отправлено")

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Прохождение опроса"
        verbose_name_plural = "Прохождения опросов"

    def __str__(self) -> str:
        return f"{self.survey.title} / {self.respondent_name or 'Анонимно'}"


class Answer(models.Model):
    submission = models.ForeignKey(
        SurveySubmission,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Прохождение",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    text_answer = models.TextField(blank=True, verbose_name="Текстовый ответ")
    number_answer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Числовой ответ",
    )
    boolean_answer = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Логический ответ",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        unique_together = ("submission", "question")

    def __str__(self) -> str:
        return f"{self.submission_id} / {self.question_id}"


class AnswerChoice(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="selected_choices",
        verbose_name="Ответ",
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name="answer_links",
        verbose_name="Вариант",
    )

    class Meta:
        unique_together = ("answer", "choice")
        verbose_name = "Выбранный вариант"
        verbose_name_plural = "Выбранные варианты"

    def __str__(self) -> str:
        return f"Ответ {self.answer_id} -> вариант {self.choice_id}"
