from django.contrib import admin
from django.utils import timezone

from .models import Blog, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("parent",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "is_featured",
        "view_count",
        "published_at",
    )
    list_filter = ("status", "is_featured", "allow_comments", "category", "created_at")
    search_fields = ("title", "short_description", "content", "author__username")
    autocomplete_fields = ("author", "category", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("view_count", "created_at", "updated_at")
    date_hierarchy = "published_at"
    list_select_related = ("author", "category")
    actions = ("publish_posts", "unpublish_posts", "mark_featured", "unmark_featured")

    fieldsets = (
        ("محتوا", {"fields": ("author", "category", "title", "slug", "short_description", "content", "image", "tags")}),
        ("انتشار", {"fields": ("status", "published_at", "is_featured", "allow_comments")}),
        ("سئو", {"fields": ("seo_title", "seo_description")}),
        ("آمار", {"fields": ("view_count", "created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    @admin.action(description="انتشار مقالات انتخاب‌شده")
    def publish_posts(self, request, queryset):
        updated = 0
        for blog in queryset:
            blog.status = Blog.Status.PUBLISHED
            if blog.published_at is None:
                blog.published_at = timezone.now()
            blog.save(update_fields=["status", "published_at"])
            updated += 1
        self.message_user(request, f"{updated} مقاله منتشر شد.")

    @admin.action(description="بازگرداندن به پیش‌نویس")
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status=Blog.Status.DRAFT)
        self.message_user(request, f"{updated} مقاله به پیش‌نویس بازگشت.")

    @admin.action(description="علامت‌گذاری به‌عنوان ویژه")
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} مقاله ویژه شد.")

    @admin.action(description="حذف علامت ویژه")
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} مقاله از حالت ویژه خارج شد.")
