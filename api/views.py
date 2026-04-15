from django.http import Http404
from django.shortcuts import render

from api.models import Survey


def home_view(request):
    surveys = (
        Survey.objects.filter(is_active=True)
        .prefetch_related("questions")
        .order_by("title")
    )
    return render(
        request,
        "api/home.html",
        {
            "surveys": surveys,
        },
    )


def survey_take_view(request, slug: str):
    survey = (
        Survey.objects.filter(slug=slug, is_active=True)
        .prefetch_related("questions__choices")
        .first()
    )
    if survey is None:
        raise Http404("Активный опрос не найден.")

    return render(
        request,
        "api/survey_take.html",
        {
            "survey": survey,
        },
    )


def survey_success_view(request, slug: str):
    survey = Survey.objects.filter(slug=slug).first()
    if survey is None:
        raise Http404("Опрос не найден.")

    return render(
        request,
        "api/survey_success.html",
        {
            "survey": survey,
            "submission_id": request.GET.get("submission_id", ""),
        },
    )
