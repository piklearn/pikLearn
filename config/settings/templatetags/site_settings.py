from django import template
from django.core.cache import cache
from django.db.models import Count
from ..models import NavbarOption, SiteSettings
from courses.models import Course, Category

register = template.Library()

# ===== تنظیمات سایت =====
@register.simple_tag
def get_site_settings():
    """دریافت تنظیمات سایت از کش یا دیتابیس"""
    settings = cache.get('site_settings')
    if not settings:
        try:
            settings = SiteSettings.objects.first()
            cache.set('site_settings', settings, 3600)  # کش برای 1 ساعت
        except SiteSettings.DoesNotExist:
            settings = None
    return settings

@register.simple_tag
def get_site_name():
    """دریافت نام سایت"""
    settings = get_site_settings()
    return settings.site_name if settings else 'پیک لرن'

@register.simple_tag
def get_site_logo():
    """دریافت لوگو سایت"""
    settings = get_site_settings()
    return settings.site_logo.url if settings and settings.site_logo else None

# ===== گزینه‌های نوبار =====
@register.simple_tag
def get_navbar_options():
    """دریافت گزینه‌های نوبار فعال"""
    return NavbarOption.objects.filter(is_active=True)

# ===== نمایش آخرین دوره‌ها =====
@register.inclusion_tag('partials/latest_courses.html')
def show_latest_courses(count=3):
    courses = Course.objects.order_by('-created_at')[:count]
    return {'courses': courses}

# ===== نمایش درخت دسته‌بندی =====
@register.inclusion_tag('partials/category_tree.html')
def category_tree():
    categories = Category.objects.annotate(
        course_count=Count('courses')
    ).filter(course_count__gt=0)
    return {'categories': categories}

# ===== فیلترهای سفارشی =====
@register.filter
def persian_numbers(value):
    """تبدیل اعداد انگلیسی به فارسی"""
    if value is None:
        return ''
    persian_map = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    return ''.join(persian_map.get(char, char) for char in str(value))

@register.filter
def currency(value):
    """نمایش قیمت به صورت تومان"""
    if value is None:
        return 'رایگان'
    return f'{persian_numbers(value):,} تومان'