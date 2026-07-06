from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.utils.html import format_html

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "content_object_display",
        "content_type",
        "object_id",
        "rating_display",
        "comment_preview",
        "is_approved",
        "is_active",
        "is_reply_display",
        "reply_count_display",
        "like_count_display",
        "created_at",
    )
    
    list_filter = (
        "is_approved",
        "is_active",
        "content_type",
        ("parent", admin.EmptyFieldListFilter),
        "created_at",
    )
    
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "comment",
    )
    
    autocomplete_fields = (
        "user",
        "parent",
    )
    
    readonly_fields = (
        "created_at",
        "updated_at",
        "content_object_display",
    )
    
    date_hierarchy = "created_at"
    list_select_related = ("user", "parent")
    list_per_page = 50
    list_editable = ("is_approved", "is_active")
    
    fieldsets = (
        ("اطلاعات اصلی", {
            "fields": (
                "user",
                "content_type",
                "object_id",
                "parent",
            )
        }),
        ("محتوا", {
            "fields": (
                "rating",
                "comment",
            )
        }),
        ("وضعیت", {
            "fields": (
                "is_approved",
                "is_active",
            )
        }),
        ("تعاملات", {
            "fields": (
                "likes",
            ),
            "classes": ("collapse",),
        }),
        ("زمان", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    
    filter_horizontal = ["likes"]
    raw_id_fields = ["user"]
    
    actions = (
        "approve_reviews",
        "reject_reviews",
        "activate_reviews",
        "deactivate_reviews",
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "user",
            "parent",
            "content_type"
        ).prefetch_related("likes")
    
    # ============================================
    # متدهای نمایشی
    # ============================================
    
    def content_object_display(self, obj):
        """نمایش محتوای مرتبط (دوره یا بلاگ)"""
        if obj.content_object:
            try:
                url = obj.content_object.get_absolute_url()
                return format_html(
                    '<a href="{}" target="_blank">{} ({})</a>',
                    url,
                    str(obj.content_object)[:50],
                    obj.content_type.model
                )
            except:
                return str(obj.content_object)[:50]
        return "-"
    content_object_display.short_description = "محتوای مرتبط"
    
    def comment_preview(self, obj):
        """پیش‌نمایش نظر"""
        if len(obj.comment) > 50:
            return obj.comment[:50] + "..."
        return obj.comment
    comment_preview.short_description = "متن نظر"
    
    def rating_display(self, obj):
        """نمایش امتیاز به صورت ستاره"""
        if obj.rating:
            stars = "⭐" * obj.rating
            return format_html(
                '<span style="font-size: 14px;">{} ({})</span>',
                stars,
                obj.rating
            )
        return "-"
    rating_display.short_description = "امتیاز"
    
    def is_reply_display(self, obj):
        """آیا پاسخ است؟"""
        return obj.parent is not None
    is_reply_display.boolean = True
    is_reply_display.short_description = "پاسخ"
    
    def reply_count_display(self, obj):
        """تعداد پاسخ‌های تایید شده"""
        count = obj.replies.filter(is_approved=True).count()
        if count > 0:
            return format_html(
                '<span style="color: #0d6efd; font-weight: bold;">{}</span>',
                count
            )
        return "0"
    reply_count_display.short_description = "تعداد پاسخ‌ها"
    
    def like_count_display(self, obj):
        """تعداد لایک‌ها"""
        count = obj.likes.count()
        if count > 0:
            return format_html(
                '<span style="color: #dc3545;">❤️ {}</span>',
                count
            )
        return "0"
    like_count_display.short_description = "لایک‌ها"
    
    # ============================================
    # اکشن‌های دسته‌جمعی
    # ============================================
    
    @admin.action(description="تایید نظرات انتخاب‌شده")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر تایید شد.")
    
    @admin.action(description="رد نظرات انتخاب‌شده")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} نظر رد شد.")
    
    @admin.action(description="فعال‌سازی نظرات انتخاب‌شده")
    def activate_reviews(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} نظر فعال شد.")
    
    @admin.action(description="غیرفعال‌سازی نظرات انتخاب‌شده")
    def deactivate_reviews(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} نظر غیرفعال شد.")


# ============================================
# Inline Admin برای نمایش پاسخ‌ها
# ============================================

class ReplyInline(admin.TabularInline):
    """نمایش پاسخ‌های یک نظر در پنل ادمین"""
    model = Review
    fk_name = "parent"
    extra = 0
    fields = (
        "user",
        "comment_preview",
        "is_approved",
        "is_active",
        "created_at",
    )
    readonly_fields = (
        "user",
        "comment_preview",
        "created_at",
    )
    can_delete = True
    show_change_link = True
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "متن نظر"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


# ============================================
# نسخه نهایی با Inline
# ============================================

class ReviewAdminWithInline(ReviewAdmin):
    inlines = [ReplyInline]


# ثبت نهایی
admin.site.unregister(Review)
admin.site.register(Review, ReviewAdminWithInline)