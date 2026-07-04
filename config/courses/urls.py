from django.urls import path, re_path
from . import views

urlpatterns = [
    path('<int:pk>', views.CourseDetailView.as_view(), name='detail'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='detail'),
    re_path(
        r'^course-autocomplete/$',
        views.CourseAutocomplete.as_view(),
        name='course-autocomplete',
    ),
]