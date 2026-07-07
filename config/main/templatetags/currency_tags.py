# templatetags/price_tags.py
from django import template

register = template.Library()

@register.filter
def show_price(value, show_toman=True):
    """نمایش قیمت با فرمت کامل - یک filter برای همه کارها"""
    if value is None or value == '':
        return "رایگان"
    
    try:
        # تبدیل به عدد
        if isinstance(value, str):
            cleaned = value.replace(',', '').replace(' ', '').replace('٬', '').strip()
            if not cleaned:
                return "رایگان"
            num = int(float(cleaned))
        else:
            num = int(value)
        
        if num == 0:
            return "رایگان"
        
        # فرمت با کاما
        formatted = f"{num:,}"
        
        # تبدیل به فارسی
        persian_digits = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        for en, fa in persian_digits.items():
            formatted = formatted.replace(en, fa)
        
        formatted = formatted.replace(',', '،')
        
        if show_toman:
            return f"{formatted} تومان"
        return formatted
    except (ValueError, TypeError, AttributeError):
        return str(value)

@register.filter
def price_only(value):
    """فقط قیمت بدون تومان"""
    return show_price(value, False)