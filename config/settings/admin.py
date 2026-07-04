from django.contrib import admin
from django.utils.html import mark_safe
from .models import SiteSettings, NavbarOption
from django.contrib import admin
from django.utils.html import mark_safe
from .models import SiteSettings, NavbarOption


class SiteSettingsInline(admin.TabularInline):
    model = SiteSettings
    extra = 0
    fields = ['setting_name', 'setting_value', 'site_icon_preview']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'site_name', 
        'site_icon_preview', 
        'site_logo_preview',
        'contact_email', 
        'is_active'
    ]
    list_editable = ['is_active']
    search_fields = ['site_name', 'setting_name', 'contact_email']
    list_filter = ['is_active']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                ('site_name', 'setting_name'),
                ('site_description', 'setting_value'),
            )
        }),
        ('ظاهر سایت', {
            'fields': (
                ('site_logo', 'site_logo_preview'),
                ('site_icon', 'site_icon_preview'),
                ('site_favicon', 'site_favicon_preview'),
                ('primary_color', 'secondary_color'),
            )
        }),
        ('سئو و متا', {
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'meta_author',
            ),
            'classes': ('collapse',),
        }),
        ('شبکه‌های اجتماعی', {
            'fields': (
                ('social_instagram', 'social_telegram'),
                ('social_twitter', 'social_linkedin'),
                'social_youtube',
            ),
            'classes': ('collapse',),
        }),
        ('اطلاعات تماس', {
            'fields': (
                ('contact_email', 'contact_phone'),
                'address',
            ),
            'classes': ('collapse',),
        }),
        ('اطلاعات سیستمی', {
            'fields': (
                'is_active',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'site_icon_preview', 'site_logo_preview', 'site_favicon_preview']

    def site_icon_preview(self, obj):
        """پیش‌نمایش آیکون سایت"""
        if obj.site_icon:
            return mark_safe(
                f'<img src="{obj.site_icon.url}" width="32" height="32" '
                f'style="border-radius: 4px; border: 1px solid #ddd; padding: 2px;" />'
            )
        return 'آیکون ثبت نشده'
    site_icon_preview.short_description = 'پیش‌نمایش آیکون'

    def site_logo_preview(self, obj):
        """پیش‌نمایش لوگو"""
        if obj.site_logo:
            return mark_safe(
                f'<img src="{obj.site_logo.url}" width="100" height="auto" '
                f'style="border-radius: 4px; border: 1px solid #ddd; padding: 2px;" />'
            )
        return 'لوگو ثبت نشده'
    site_logo_preview.short_description = 'پیش‌نمایش لوگو'

    def site_favicon_preview(self, obj):
        """پیش‌نمایش favicon"""
        if obj.site_favicon:
            return mark_safe(
                f'<img src="{obj.site_favicon.url}" width="16" height="16" '
                f'style="border-radius: 2px; border: 1px solid #ddd; padding: 1px;" />'
            )
        return 'Favicon ثبت نشده'
    site_favicon_preview.short_description = 'پیش‌نمایش Favicon'

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css',)
        }

@admin.register(NavbarOption)
class NavbarOptionAdmin(admin.ModelAdmin):
    list_display = ['icon_preview', 'name', 'link', 'order', 'is_active', 'open_in_new_tab']
    list_editable = ['order', 'is_active', 'open_in_new_tab']
    list_filter = ['is_active']
    search_fields = ['name', 'link']
    ordering = ['order']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'link', 'icon', 'order')
        }),
        ('تنظیمات نمایش', {
            'fields': ('is_active', 'open_in_new_tab')
        }),
    )

    def icon_preview(self, obj):
        """نمایش پیش‌نمایش آیکون در لیست"""
        return mark_safe(f'<i class="bi {obj.icon}" style="font-size: 1.2rem;"></i>')
    icon_preview.short_description = 'آیکون'
    icon_preview.admin_order_field = 'icon'

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css',)
        }