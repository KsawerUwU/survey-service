from django.contrib import admin

from .models import Answer, AnswerChoice, Choice, Question, Survey, SurveySubmission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "title", "question_type", "order", "is_required")
    list_filter = ("question_type", "is_required", "survey")
    search_fields = ("title", "description")
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "text", "value", "order")
    list_filter = ("question__survey",)
    search_fields = ("text", "value")


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 0


@admin.register(SurveySubmission)
class SurveySubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "survey", "respondent_name", "respondent_email", "submitted_at")
    list_filter = ("survey", "submitted_at")
    search_fields = ("respondent_name", "respondent_email")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "question", "number_answer", "boolean_answer", "created_at")
    list_filter = ("question__survey", "question__question_type")
    search_fields = ("text_answer",)
    inlines = [AnswerChoiceInline]
