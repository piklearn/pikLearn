from django.db import models
from users.models import CustomUser
from django.urls import reverse
from django.utils.text import slugify
from datetime import timedelta
from reviews.models import Review
from django.contrib.contenttypes.models import ContentType

# ============================================
# Category Model
# ============================================
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories', verbose_name='دسته ی مادر')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='آیکون')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True, verbose_name='اسلاگ')
    
    def __str__(self):
        return self.name

    def get_children(self):
        return self.subcategories.all()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'دسته بندی ها'
        verbose_name = 'دسته بندی'


# ============================================
# Course Model
# ============================================
class Course(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', 'مبتدی'),
        ('intermediate', 'متوسط'),
        ('advanced', 'پیشرفته'),
    ]
    
    LANGUAGE_CHOICES = [
        ('fa', 'فارسی'),
        ('en', 'انگلیسی'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='اسلاگ')
    thumbnail = models.FileField(upload_to='course_thumbnails', max_length=100, verbose_name='تصویر دوره')
    cover_image = models.ImageField(upload_to='course_covers', blank=True, null=True, verbose_name='تصویر کاور')
    description = models.TextField(verbose_name='توضیحات کامل')
    short_description = models.TextField(max_length=300, default='', verbose_name='توضیحات کوتاه')
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught', verbose_name='مدرس')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses', verbose_name='دسته بندی')
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='قیمت')
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name='قیمت تخفیف')
    duration = models.DurationField(default=timedelta(hours=1), verbose_name='مدت زمان')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner', verbose_name='سطح دشواری')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='fa', verbose_name='زبان')
    has_certificate = models.BooleanField(default=False, verbose_name='گواهینامه دارد')
    certificate_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='متن گواهینامه')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    status = models.CharField(max_length=10, choices=[('published', 'منتشر شده'), ('draft', 'پیش نویس')], default='draft', verbose_name='وضعیت')
    views = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:detail', args=[self.slug or self.id])
    
    def get_student_count(self):
        return self.enrollments.filter(is_active=True).count()
    
    def get_reviews(self):
        """دریافت نظرات اصلی (غیر پاسخ)"""
        from django.contrib.contenttypes.models import ContentType
        from reviews.models import Review
        
        content_type = ContentType.objects.get_for_model(self)
        return Review.objects.filter(
            content_type=content_type,
            object_id=self.id,
            parent__isnull=True,  # فقط نظرات اصلی
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
    
    def get_average_rating(self):
        reviews = Review.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            parent__isnull=True,  # فقط نظرات اصلی
            is_approved=True,
            rating__isnull=False
        )
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0
    
    def get_review_count(self):
        """تعداد نظرات دوره"""
        return self.get_reviews().count()
    
    def get_duration_display(self):
        total_seconds = self.duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"
    
    def get_discounted_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def get_discount_percentage(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    def get_requirements(self):
        return self.requirements.all()
    
    def get_learn_points(self):
        return self.learn_points.all()
    
    def get_chapters(self):
        return self.chapters.all().order_by('order')
    
    def get_total_videos(self):
        return Video.objects.filter(chapter__course=self).count()
    
    def get_total_duration(self):
        videos = Video.objects.filter(chapter__course=self)
        total = sum(v.duration.total_seconds() for v in videos)
        hours = int(total // 3600)
        minutes = int((total % 3600) // 60)
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"
        
    def get_comment_count(self):
        """تعداد نظرات بلاگ"""
        return self.get_reviews().count()
    class Meta:
        verbose_name_plural = 'دوره ها'
        verbose_name = 'دوره'
        ordering = ['-created_date']


# ============================================
# Course Requirement Model
# ============================================
class CourseRequirement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='requirements', verbose_name='دوره')
    text = models.CharField(max_length=300, verbose_name='متن')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name_plural = 'پیش‌نیازها'
        verbose_name = 'پیش‌نیاز'
        ordering = ['order']


# ============================================
# Learn Point Model
# ============================================
class LearnPoint(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learn_points', verbose_name='دوره')
    text = models.CharField(max_length=300, verbose_name='متن')
    icon = models.CharField(max_length=50, default='bi-check-circle-fill', verbose_name='آیکون')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name_plural = 'نکات آموزشی'
        verbose_name = 'نکته آموزشی'
        ordering = ['order']


# ============================================
# Chapter Model
# ============================================
class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name='دوره')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_free = models.BooleanField(default=False, verbose_name='رایگان')
    
    def __str__(self):
        return f"{self.title} - {self.course.title}"
    
    def get_videos(self):
        return self.videos.all().order_by('order')
    
    def get_total_duration(self):
        videos = self.videos.all()
        total = sum(v.duration.total_seconds() for v in videos)
        hours = int(total // 3600)
        minutes = int((total % 3600) // 60)
        if hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"
    
    class Meta:
        verbose_name_plural = 'فصل‌ها'
        verbose_name = 'فصل'
        ordering = ['order']


# ============================================
# Video Model
# ============================================
class Video(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos', verbose_name='فصل')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    url = models.URLField(verbose_name='آدرس ویدیو')
    duration = models.DurationField(default=timedelta(minutes=5), verbose_name='مدت زمان')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_free_preview = models.BooleanField(default=False, verbose_name='پیش‌نمایش رایگان')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    attachment = models.FileField(upload_to='video_attachments', blank=True, null=True, verbose_name='فایل پیوست')
    attachment_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام فایل پیوست')
    is_downloadable = models.BooleanField(default=False, verbose_name='قابل دانلود')
    
    def __str__(self):
        return self.title
    
    def get_duration_display(self):
        total_seconds = self.duration.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        if minutes > 0:
            return f"{minutes}:{seconds:02d}"
        return f"{seconds} ثانیه"
    
    class Meta:
        verbose_name_plural = 'ویدئوها'
        verbose_name = 'ویدئو'
        ordering = ['order']


# ============================================
# Course FAQ Model
# ============================================
class CourseFAQ(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faqs', verbose_name='دوره')
    question = models.CharField(max_length=300, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name_plural = 'سوالات متداول'
        verbose_name = 'سوال متداول'
        ordering = ['order']


# ============================================
# Course Resource Model
# ============================================
class CourseResource(models.Model):
    RESOURCE_TYPES = [
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('zip', 'ZIP'),
        ('link', 'لینک'),
        ('other', 'سایر'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources', verbose_name='دوره')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    file = models.FileField(upload_to='course_resources', blank=True, null=True, verbose_name='فایل')
    link = models.URLField(blank=True, null=True, verbose_name='لینک')
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, default='pdf', verbose_name='نوع منبع')
    is_free = models.BooleanField(default=False, verbose_name='رایگان')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'منابع'
        verbose_name = 'منبع'
        ordering = ['order']


# ============================================
# Course Enrollment Model
# ============================================
class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='دوره')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrolled_courses', verbose_name='کاربر')
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='پیشرفت')
    completed_date = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ اتمام')
    
    class Meta:
        unique_together = ['course', 'user']
        verbose_name_plural = 'ثبت‌نام‌ها'
        verbose_name = 'ثبت‌نام'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


# ============================================
# User Progress Model
# ============================================
class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_progress', verbose_name='کاربر')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress', verbose_name='دوره')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_progress', verbose_name='ویدئو')
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل شده')
    last_watched = models.DateTimeField(auto_now=True, verbose_name='آخرین بازدید')
    watch_time = models.DurationField(default=timedelta(), verbose_name='زمان تماشا')
    completion_status = models.CharField(max_length=11, choices=[('watched', 'Watched'), ('not_watched', 'Not Watched')], default='not_watched', verbose_name='وضعیت')
    
    def __str__(self):
        return f"{self.user.username} - {self.video.title}"
    
    class Meta:
        unique_together = ['user', 'video']
        verbose_name_plural = 'پیشرفت کاربران'
        verbose_name = 'پیشرفت کاربر'

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
        verbose_name_plural = 'علاقه‌مندی‌ها'
        verbose_name = 'علاقه‌مندی'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"