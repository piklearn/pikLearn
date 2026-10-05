from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path(
        "add/<str:model_name>/<int:object_id>/",
        views.add_review,
        name="add",
    ),
    path(
        "reply/<int:parent_id>/",
        views.add_reply,
        name="reply",
    ),
]
