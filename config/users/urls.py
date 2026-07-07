from django.urls import path
from . import views
from django.contrib.auth.urls import urlpatterns as auth_urls

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    ] + auth_urls