from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from strawberry.django.views import GraphQLView

from api.graphql.schema import schema
from api.views import home_view, survey_success_view, survey_take_view

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("surveys/<slug:slug>/", survey_take_view, name="survey_take"),
    path("surveys/<slug:slug>/success/", survey_success_view, name="survey_success"),
    path(
        "graphql/",
        csrf_exempt(
            GraphQLView.as_view(
                schema=schema,
                graphql_ide="graphiql",
            )
        ),
    ),
]
