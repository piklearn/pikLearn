from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="list"),
    path("search/", views.BlogSearchView.as_view(), name="search"),
    path("category/<str:slug>/", views.CategoryBlogListView.as_view(), name="category"),
    path("tag/<str:slug>/", views.TagBlogListView.as_view(), name="tag"),
    path("<str:slug>/", views.BlogDetailView.as_view(), name="detail"),
]
