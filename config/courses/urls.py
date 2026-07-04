from django.urls import path, re_path
from . import views

app_name = 'courses'

urlpatterns = [
    # Autocomplete
    re_path(
        r'^course-autocomplete/$',
        views.CourseAutocomplete.as_view(),
        name='course-autocomplete',
    ),
    # Course detail with slug
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    # Course detail with pk (fallback)
    path('<int:pk>/', views.CourseDetailView.as_view(), name='detail'),
    # Course list
    path('', views.CourseListView.as_view(), name='list'),
    # API endpoints
    path('api/enroll/<int:course_id>/', views.enroll_course, name='enroll'),
    path('api/review-like/', views.review_like, name='review_like'),
    path('api/review-report/', views.review_report, name='review_report'),
    path('api/wishlist/<int:course_id>/', views.toggle_wishlist, name='wishlist'),
]