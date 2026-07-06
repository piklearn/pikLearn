from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="کاربر",
    )
    
    # Generic Foreign Key برای اتصال به هر مدلی (Course یا Blog)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="نوع محتوا",
        limit_choices_to={
            'model__in': ['course', 'blog']  # فقط به این دو مدل محدود می‌شود
        }
    )

    # پدر (برای ریپلای)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="پاسخ به",
    )
    
    object_id = models.PositiveIntegerField(verbose_name="شناسه محتوا")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # فیلدهای نظر
    rating = models.PositiveSmallIntegerField(
        verbose_name="امتیاز",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="عددی بین ۱ تا ۵",
        null=True,  # برای بلاگ می‌تواند null باشد
        blank=True
    )
    # فیلدهای تعامل
    likes = models.ManyToManyField( 
        settings.AUTH_USER_MODEL,
        related_name="liked_reviews",
        blank=True,
        verbose_name="لایک‌ها"
    )
    comment = models.TextField(blank=True, verbose_name="نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تایید شده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        indexes = [
            models.Index(fields=["content_type", "object_id"], name="reviews_content_idx"),
            models.Index(fields=["is_approved"], name="reviews_approved_idx"),
            models.Index(fields=["created_at"], name="reviews_created_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="reviews_unique_user_content",
            ),
        ]

    @property
    def is_reply(self):
        """آیا این نظر یک پاسخ است؟"""
        return self.parent is not None
    
    @property
    def reply_count(self):
        """تعداد پاسخ‌های این نظر"""
        return self.replies.filter(is_approved=True, is_active=True).count()
    
    def get_replies(self):
        """دریافت پاسخ‌های تایید شده"""
        return self.replies.filter(is_approved=True, is_active=True).order_by('created_at')

    def __str__(self):
        return f"{self.user} → {self.content_object} ({self.rating or 'بدون امتیاز'})"

    def get_reviews(self):
        """دریافت نظرات اصلی (غیر پاسخ)"""
        from django.contrib.contenttypes.models import ContentType
        from reviews.models import Review
        
        content_type = ContentType.objects.get_for_model(self)
        return Review.objects.filter(
            content_type=content_type,
            object_id=self.id,
            parent__isnull=True,
            is_approved=True,
            is_active=True
        ).order_by('-created_at')
    
    def get_all_reviews(self):
        """دریافت تمام نظرات (شامل پاسخ‌ها)"""
        from django.contrib.contenttypes.models import ContentType
        from reviews.models import Review
        
        content_type = ContentType.objects.get_for_model(self)
        return Review.objects.filter(
            content_type=content_type,
            object_id=self.id,
            is_approved=True,
            is_active=True
        ).order_by('created_at')
    def clean(self):
        # برای دوره‌ها، امتیاز الزامی است
        if self.content_type and self.content_type.model == 'course' and self.rating is None:
            raise ValidationError({"rating": "امتیاز برای دوره‌ها الزامی است."})
        
        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValidationError({"rating": "امتیاز باید بین ۱ تا ۵ باشد."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)