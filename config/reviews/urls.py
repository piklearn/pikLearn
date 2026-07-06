from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<int:course_id>/", views.CreateReviewView.as_view(), name="add"),
    path("edit/<int:pk>/", views.UpdateReviewView.as_view(), name="edit"),
    path("delete/<int:pk>/", views.DeleteReviewView.as_view(), name="delete"),
]
