from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .utils import generate_unique_slug


class Category(models.Model):
    title = models.CharField(max_length=120, verbose_name="عنوان")
    slug = models.SlugField(max_length=140, unique=True, blank=True, allow_unicode=True, verbose_name="نامک")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته‌ی مادر",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to="blog/categories/%Y/%m/", blank=True, null=True, verbose_name="تصویر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        ordering = ["title"]
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        indexes = [models.Index(fields=["slug"], name="blog_category_slug_idx")]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    title = models.CharField(max_length=80, verbose_name="عنوان")
    slug = models.SlugField(max_length=100, unique=True, blank=True, allow_unicode=True, verbose_name="نامک")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        ordering = ["title"]
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        indexes = [models.Index(fields=["slug"], name="blog_tag_slug_idx")]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag", kwargs={"slug": self.slug})


class Blog(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشر شده"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        verbose_name="نویسنده",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blogs",
        verbose_name="دسته‌بندی",
    )
    title = models.CharField(max_length=220, verbose_name="عنوان")
    slug = models.SlugField(max_length=240, unique=True, blank=True, allow_unicode=True, verbose_name="نامک")
    short_description = models.CharField(max_length=300, verbose_name="توضیح کوتاه")
    content = models.TextField(verbose_name="محتوا")
    image = models.ImageField(upload_to="blog/posts/%Y/%m/", verbose_name="تصویر شاخص")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT, verbose_name="وضعیت"
    )
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انتشار")
    tags = models.ManyToManyField(Tag, blank=True, related_name="blogs", verbose_name="برچسب‌ها")
    is_featured = models.BooleanField(default=False, verbose_name="ویژه")
    allow_comments = models.BooleanField(default=True, verbose_name="امکان ارسال نظر")
    view_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")
    seo_title = models.CharField(max_length=70, blank=True, verbose_name="عنوان سئو")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="توضیحات سئو")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        indexes = [
            models.Index(fields=["slug"], name="blog_blog_slug_idx"),
            models.Index(fields=["status", "published_at"], name="blog_blog_status_pub_idx"),
            models.Index(fields=["category"], name="blog_blog_category_idx"),
            models.Index(fields=["is_featured"], name="blog_blog_featured_idx"),
        ]

    def __str__(self):
        return self.title
        
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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def meta_title(self):
        return self.seo_title or self.title

    @property
    def meta_description(self):
        return self.seo_description or self.short_description

    @property
    def reading_time_minutes(self):
        words = len(self.content.split())
        return max(1, round(words / 200))

