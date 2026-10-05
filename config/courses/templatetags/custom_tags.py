from django import template
from courses.models import Course, Category

register = template.Library()

@register.inclusion_tag('courses/latest_courses.html')
def show_latest_courses(count=5):
    latest_courses = Course.objects.order_by('-created_date')[:count]
    return {'latest_courses': latest_courses}

@register.inclusion_tag('courses/categories.html')
def category_tree():
    categories = Category.objects.filter(parent_category__isnull=True)  # فقط دسته‌های اصلی
    return {'categories': categories}

@register.filter
def persian_intcomma(value):
        str_value = str(value)[::-1]
        new_value = ''
        for i in range(len(str_value)):
            new_value += str_value[i]
            if (i+1) % 3 == 0 and i != len(str_value) - 1:
                new_value += ','
        return new_value[::-1]
