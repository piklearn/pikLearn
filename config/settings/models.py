from django.db import models
from django.db import models
from django.core.exceptions import ValidationError
import os

class SiteSettings(models.Model):
    # تنظیمات عمومی
    setting_name = models.CharField(max_length=100, unique=True, verbose_name='نام تنظیمات')
    setting_value = models.TextField(verbose_name='مقدار تنظیمات')
    
    # تنظیمات ظاهری
    site_name = models.CharField(max_length=100, default='پیک لرن', verbose_name='نام سایت')
    site_description = models.TextField(blank=True, verbose_name='توضیحات سایت')
    site_logo = models.ImageField(
        upload_to='site_logos/',
        blank=True,
        null=True,
        verbose_name='لوگو سایت',
        help_text='لوگو سایت (فرمت‌های مجاز: PNG, JPG, SVG)'
    )
    site_icon = models.ImageField(
        upload_to='site_icons/',
        blank=True,
        null=True,
        verbose_name='آیکون سایت (Favicon)',
        help_text='آیکون سایت برای مرورگر (اندازه پیشنهادی: 32x32 یا 64x64 پیکسل)'
    )
    site_favicon = models.ImageField(
        upload_to='favicons/',
        blank=True,
        null=True,
        verbose_name='Favicon',
        help_text='آیکون برای تب مرورگر (16x16 یا 32x32 پیکسل)'
    )
    
    # تنظیمات تم
    primary_color = models.CharField(
        max_length=7,
        default='#FFD54A',
        verbose_name='رنگ اصلی',
        help_text='رنگ اصلی سایت (مثلاً #FFD54A)'
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#2563EB',
        verbose_name='رنگ ثانویه',
        help_text='رنگ ثانویه سایت (مثلاً #2563EB)'
    )
    
    # تنظیمات سئو
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان متا')
    meta_description = models.TextField(blank=True, verbose_name='توضیحات متا')
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name='کلمات کلیدی')
    meta_author = models.CharField(max_length=100, blank=True, verbose_name='نویسنده')
    
    # تنظیمات اجتماعی
    social_instagram = models.URLField(blank=True, verbose_name='اینستاگرام')
    social_telegram = models.URLField(blank=True, verbose_name='تلگرام')
    social_twitter = models.URLField(blank=True, verbose_name='توییتر')
    social_linkedin = models.URLField(blank=True, verbose_name='لینکدین')
    social_youtube = models.URLField(blank=True, verbose_name='یوتیوب')
    
    # تنظیمات ارتباطی
    contact_email = models.EmailField(blank=True, verbose_name='ایمیل تماس')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='شماره تماس')
    address = models.TextField(blank=True, verbose_name='آدرس')
    
    # تنظیمات عمومی
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"
        ordering = ['-created_at']

    def __str__(self):
        return self.setting_name or self.site_name

    def clean(self):
        """اعتبارسنجی فایل‌های آپلود شده"""
        if self.site_icon:
            # بررسی سایز آیکون
            if self.site_icon.width > 64 or self.site_icon.height > 64:
                raise ValidationError({
                    'site_icon': 'اندازه آیکون نباید بیشتر از 64x64 پیکسل باشد'
                })
            
            # بررسی فرمت فایل
            valid_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.ico']
            ext = os.path.splitext(self.site_icon.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError({
                    'site_icon': f'فرمت فایل مجاز نیست. فرمت‌های مجاز: {", ".join(valid_extensions)}'
                })

    def get_icon_url(self):
        """دریافت URL آیکون"""
        if self.site_icon:
            return self.site_icon.url
        return None

    def get_favicon_url(self):
        """دریافت URL favicon"""
        if self.site_favicon:
            return self.site_favicon.url
        if self.site_icon:
            return self.site_icon.url
        return None

    def get_logo_url(self):
        """دریافت URL لوگو"""
        if self.site_logo:
            return self.site_logo.url
        return None

class NavbarOption(models.Model):
    # لیست آیکون‌های Bootstrap Icons
    ICON_CHOICES = [
        ('bi-house', 'خانه'),
        ('bi-book', 'کتاب'),
        ('bi-grid', 'دسته‌بندی'),
        ('bi-newspaper', 'مقالات'),
        ('bi-info-circle', 'درباره ما'),
        ('bi-envelope', 'تماس با ما'),
        ('bi-person', 'پروفایل'),
        ('bi-gear', 'تنظیمات'),
        ('bi-search', 'جستجو'),
        ('bi-tag', 'برچسب'),
        ('bi-star', 'ستاره'),
        ('bi-heart', 'قلب'),
        ('bi-clock', 'زمان'),
        ('bi-calendar', 'تقویم'),
        ('bi-chat', 'چت'),
        ('bi-bell', 'زنگ'),
        ('bi-cart', 'سبد خرید'),
        ('bi-credit-card', 'کارت اعتباری'),
        ('bi-gift', 'هدیه'),
        ('bi-rocket', 'موشک'),
        ('bi-lightbulb', 'لامپ'),
        ('bi-camera', 'دوربین'),
        ('bi-music-note', 'موسیقی'),
        ('bi-video', 'ویدیو'),
        ('bi-file-text', 'فایل متنی'),
        ('bi-folder', 'پوشه'),
        ('bi-download', 'دانلود'),
        ('bi-upload', 'آپلود'),
        ('bi-share', 'اشتراک‌گذاری'),
        ('bi-link', 'لینک'),
        ('bi-lock', 'قفل'),
        ('bi-unlock', 'باز کردن قفل'),
        ('bi-key', 'کلید'),
        ('bi-pencil', 'مداد'),
        ('bi-trash', 'سطل زباله'),
        ('bi-plus', 'افزودن'),
        ('bi-minus', 'حذف'),
        ('bi-check', 'تأیید'),
        ('bi-x', 'انصراف'),
        ('bi-arrow-right', 'فلش راست'),
        ('bi-arrow-left', 'فلش چپ'),
        ('bi-arrow-up', 'فلش بالا'),
        ('bi-arrow-down', 'فلش پایین'),
        ('bi-chevron-right', 'چپ‌گرد راست'),
        ('bi-chevron-left', 'چپ‌گرد چپ'),
        ('bi-chevron-up', 'چپ‌گرد بالا'),
        ('bi-chevron-down', 'چپ‌گرد پایین'),
        ('bi-globe', 'جهان'),
        ('bi-map', 'نقشه'),
        ('bi-phone', 'تلفن'),
        ('bi-laptop', 'لپ‌تاپ'),
        ('bi-tablet', 'تبلت'),
        ('bi-phone-landscape', 'تلفن افقی'),
        ('bi-display', 'نمایشگر'),
        ('bi-server', 'سرور'),
        ('bi-cloud', 'ابر'),
        ('bi-database', 'پایگاه داده'),
        ('bi-code', 'کد'),
        ('bi-terminal', 'ترمینال'),
        ('bi-bug', 'بگ'),
        ('bi-shield', 'سپر'),
        ('bi-shield-lock', 'سپر قفل'),
        ('bi-shield-check', 'سپر تأیید'),
        ('bi-eye', 'چشم'),
        ('bi-eye-slash', 'چشم بسته'),
        ('bi-brightness-high', 'روشنایی بالا'),
        ('bi-brightness-low', 'روشنایی پایین'),
        ('bi-moon', 'ماه'),
        ('bi-sun', 'خورشید'),
        ('bi-cloud-sun', 'ابر و خورشید'),
        ('bi-cloud-moon', 'ابر و ماه'),
        ('bi-cloud-rain', 'ابر بارانی'),
        ('bi-cloud-snow', 'ابر برفی'),
        ('bi-wind', 'باد'),
        ('bi-snow', 'برف'),
        ('bi-thermometer', 'دماسنج'),
        ('bi-droplet', 'قطره'),
        ('bi-droplet-half', 'نصف قطره'),
        ('bi-bar-chart', 'نمودار میله‌ای'),
        ('bi-pie-chart', 'نمودار دایره‌ای'),
        ('bi-line-chart', 'نمودار خطی'),
        ('bi-activity', 'فعالیت'),
        ('bi-heart-pulse', 'ضربان قلب'),
        ('bi-cpu', 'پردازنده'),
        ('bi-memory', 'حافظه'),
        ('bi-hdd', 'هارد دیسک'),
        ('bi-sd-card', 'کارت حافظه'),
        ('bi-sim', 'سیم کارت'),
        ('bi-usb', 'یواس‌بی'),
        ('bi-bluetooth', 'بلوتوث'),
        ('bi-wifi', 'وای‌فای'),
        ('bi-headphones', 'هدفون'),
        ('bi-speaker', 'بلندگو'),
        ('bi-mic', 'میکروفون'),
        ('bi-mic-mute', 'میکروفون خاموش'),
        ('bi-play', 'پخش'),
        ('bi-pause', 'مکث'),
        ('bi-stop', 'توقف'),
        ('bi-skip-forward', 'جلو'),
        ('bi-skip-backward', 'عقب'),
        ('bi-shuffle', 'تصادفی'),
        ('bi-repeat', 'تکرار'),
        ('bi-zoom-in', 'بزرگ‌نمایی'),
        ('bi-zoom-out', 'کوچک‌نمایی'),
        ('bi-fullscreen', 'تمام صفحه'),
        ('bi-fullscreen-exit', 'خروج از تمام صفحه'),
        ('bi-crop', 'برش'),
        ('bi-rotate-left', 'چرخش به چپ'),
        ('bi-rotate-right', 'چرخش به راست'),
        ('bi-flip-horizontal', 'چرخش افقی'),
        ('bi-flip-vertical', 'چرخش عمودی'),
        ('bi-align-start', 'تراز شروع'),
        ('bi-align-center', 'تراز وسط'),
        ('bi-align-end', 'تراز پایان'),
        ('bi-align-top', 'تراز بالا'),
        ('bi-align-middle', 'تراز وسط عمودی'),
        ('bi-align-bottom', 'تراز پایین'),
        ('bi-justify', 'هم‌تراز'),
        ('bi-text-left', 'متن چپ'),
        ('bi-text-center', 'متن وسط'),
        ('bi-text-right', 'متن راست'),
        ('bi-bold', 'پررنگ'),
        ('bi-italic', 'کج'),
        ('bi-underline', 'زیرخط'),
        ('bi-strikethrough', 'خط‌خورده'),
        ('bi-fonts', 'فونت‌ها'),
        ('bi-type', 'نوع'),
        ('bi-quote', 'نقل قول'),
        ('bi-list', 'لیست'),
        ('bi-list-ol', 'لیست شماره‌دار'),
        ('bi-list-ul', 'لیست گلوله‌ای'),
        ('bi-check-all', 'تأیید همه'),
        ('bi-check-circle', 'دایره تأیید'),
        ('bi-check-circle-fill', 'دایره تأیید پر'),
        ('bi-check-square', 'مربع تأیید'),
        ('bi-check-square-fill', 'مربع تأیید پر'),
        ('bi-x-circle', 'دایره انصراف'),
        ('bi-x-circle-fill', 'دایره انصراف پر'),
        ('bi-x-square', 'مربع انصراف'),
        ('bi-x-square-fill', 'مربع انصراف پر'),
        ('bi-plus-circle', 'دایره افزودن'),
        ('bi-plus-circle-fill', 'دایره افزودن پر'),
        ('bi-plus-square', 'مربع افزودن'),
        ('bi-plus-square-fill', 'مربع افزودن پر'),
        ('bi-dash-circle', 'دایره حذف'),
        ('bi-dash-circle-fill', 'دایره حذف پر'),
        ('bi-dash-square', 'مربع حذف'),
        ('bi-dash-square-fill', 'مربع حذف پر'),
        ('bi-exclamation-circle', 'دایره هشدار'),
        ('bi-exclamation-circle-fill', 'دایره هشدار پر'),
        ('bi-exclamation-triangle', 'مثلث هشدار'),
        ('bi-exclamation-triangle-fill', 'مثلث هشدار پر'),
        ('bi-question-circle', 'دایره سوال'),
        ('bi-question-circle-fill', 'دایره سوال پر'),
        ('bi-question-square', 'مربع سوال'),
        ('bi-question-square-fill', 'مربع سوال پر'),
        ('bi-info-circle', 'دایره اطلاعات'),
        ('bi-info-circle-fill', 'دایره اطلاعات پر'),
        ('bi-info-square', 'مربع اطلاعات'),
        ('bi-info-square-fill', 'مربع اطلاعات پر'),
    ]

    name = models.CharField(max_length=50, verbose_name='نام')
    link = models.CharField(max_length=200, verbose_name='آدرس')
    icon = models.CharField(
        max_length=50, 
        choices=ICON_CHOICES,
        default='bi-link',
        verbose_name='آیکون',
        help_text='آیکون‌های Bootstrap Icons را انتخاب کنید'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    open_in_new_tab = models.BooleanField(default=False, verbose_name='در تب جدید باز شود')

    class Meta:
        verbose_name = "گزینه نوبار"
        verbose_name_plural = "گزینه‌های نوبار"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_icon_html(self):
        """برگرداندن HTML آیکون"""
        return f'<i class="bi {self.icon}"></i>'