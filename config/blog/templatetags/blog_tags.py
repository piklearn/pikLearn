from django import template
from django.db.models import Count, Q
from blog.models import Blog, Category, Tag

register = template.Library()

@register.inclusion_tag('blog/partials/_blog_card.html')
def blog_card(blog):
    """نمایش یک کارت مقاله"""
    return {
        'blog': blog,
    }

@register.inclusion_tag('blog/partials/_blog_list.html')
def blog_list(limit=6, category_slug=None, tag_slug=None):
    """نمایش لیست مقالات - خودش از دیتابیس می‌خواند"""
    blogs = Blog.objects.filter(status=Blog.Status.PUBLISHED)
    
    if category_slug:
        blogs = blogs.filter(category__slug=category_slug)
    
    if tag_slug:
        blogs = blogs.filter(tags__slug=tag_slug)
    
    blogs = blogs.order_by('-published_at')[:limit]
    
    return {
        'blogs': blogs,
    }

# ============================================
# 1. دریافت و نمایش جدیدترین مقالات
# ============================================
@register.inclusion_tag('blog/partials/_recent_blogs.html')
def recent_blogs(limit=5):
    """نمایش جدیدترین مقالات - بدون نیاز به ارسال داده از ویو"""
    blogs = Blog.objects.filter(
        status=Blog.Status.PUBLISHED
    ).order_by('-published_at')[:limit]
    
    return {
        'blogs': blogs,
        'title': 'جدیدترین مقالات'
    }


# ============================================
# 2. دریافت و نمایش مقالات ویژه
# ============================================
@register.inclusion_tag('blog/partials/_featured_blogs.html')
def featured_blogs(limit=3):
    """نمایش مقالات ویژه - بدون نیاز به ارسال داده از ویو"""
    blogs = Blog.objects.filter(
        status=Blog.Status.PUBLISHED,
        is_featured=True
    ).order_by('-published_at')[:limit]
    
    return {
        'blogs': blogs,
        'title': 'مقالات ویژه'
    }


# ============================================
# 3. دریافت و نمایش مقالات یک دسته‌بندی خاص
# ============================================
@register.inclusion_tag('blog/partials/_category_blogs.html')
def category_blogs(category_slug, limit=5):
    """نمایش مقالات یک دسته‌بندی خاص"""
    blogs = Blog.objects.filter(
        status=Blog.Status.PUBLISHED,
        category__slug=category_slug
    ).order_by('-published_at')[:limit]
    
    return {
        'blogs': blogs,
        'category_slug': category_slug
    }


# ============================================
# 4. دریافت و نمایش مقالات مرتبط با یک مقاله
# ============================================
@register.inclusion_tag('blog/partials/_related_blogs.html')
def related_blogs(blog, limit=4):
    """نمایش مقالات مرتبط با یک مقاله (بر اساس دسته‌بندی و برچسب‌ها)"""
    # مقالات هم‌دسته
    related = Blog.objects.filter(
        status=Blog.Status.PUBLISHED,
        category=blog.category
    ).exclude(id=blog.id)[:limit]
    
    if related.count() < limit:
        extra = Blog.objects.filter(
            status=Blog.Status.PUBLISHED
        ).exclude(
            id__in=related.values_list('id', flat=True)
        ).exclude(
            id=blog.id
        ).order_by('-published_at')[:limit - related.count()]
        
        related = list(related) + list(extra)
    
    return {
        'blogs': related,
        'title': 'مقالات مرتبط'
    }


# ============================================
# 5. دریافت و نمایش دسته‌بندی‌ها با تعداد مقالات
# ============================================
@register.inclusion_tag('blog/partials/_categories_sidebar.html')
def categories_sidebar():
    """نمایش دسته‌بندی‌ها در سایدبار - بدون نیاز به ارسال داده از ویو"""
    categories = Category.objects.annotate(
        post_count=Count('blogs', filter=Q(blogs__status=Blog.Status.PUBLISHED))
    ).filter(post_count__gt=0).order_by('-post_count')
    
    return {
        'categories': categories,
        'title': 'دسته‌بندی‌ها'
    }


# ============================================
# 6. دریافت و نمایش برچسب‌ها با تعداد مقالات
# ============================================
@register.inclusion_tag('blog/partials/_tags_sidebar.html')
def tags_sidebar():
    """نمایش برچسب‌ها در سایدبار - بدون نیاز به ارسال داده از ویو"""
    tags = Tag.objects.annotate(
        post_count=Count('blogs', filter=Q(blogs__status=Blog.Status.PUBLISHED))
    ).filter(post_count__gt=0).order_by('-post_count')
    
    return {
        'tags': tags,
        'title': 'برچسب‌ها'
    }


# ============================================
# 7. دریافت و نمایش آرشیو ماهانه
# ============================================
@register.inclusion_tag('blog/partials/_archive_sidebar.html')
def archive_sidebar():
    """نمایش آرشیو ماهانه مقالات"""
    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    
    archive = Blog.objects.filter(
        status=Blog.Status.PUBLISHED
    ).annotate(
        month=TruncMonth('published_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')
    
    return {
        'archive': archive,
        'title': 'آرشیو مطالب'
    }


# ============================================
# 8. دریافت و نمایش محبوب‌ترین مقالات (بر اساس بازدید)
# ============================================
@register.inclusion_tag('blog/partials/_popular_blogs.html')
def popular_blogs(limit=5):
    """نمایش محبوب‌ترین مقالات بر اساس تعداد بازدید"""
    blogs = Blog.objects.filter(
        status=Blog.Status.PUBLISHED
    ).order_by('-view_count')[:limit]
    
    return {
        'blogs': blogs,
        'title': 'محبوب‌ترین مقالات'
    }