from django.contrib import admin
from .models import Course
from .models import Category
from .models import Video
from .models import UserProgress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = (
    "title",
    "slug",
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    pass

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    pass