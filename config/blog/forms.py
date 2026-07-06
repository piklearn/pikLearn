from django import forms
from django.contrib.contenttypes.models import ContentType
from reviews.models import Review


class ReviewForm(forms.ModelForm):
    """فرم عمومی برای ثبت نظر در دوره‌ها و بلاگ"""
    
    content_type = forms.CharField(
        max_length=50,
        widget=forms.HiddenInput(),
        required=True
    )
    object_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'content_type', 'object_id']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-select'},
                choices=[(i, i) for i in range(1, 6)]
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'نظر خود را بنویسید...'
                }
            ),
        }
        labels = {
            'rating': 'امتیاز شما',
            'comment': 'نظر شما',
        }
        help_texts = {
            'rating': 'لطفاً امتیاز خود را از ۱ تا ۵ انتخاب کنید',
        }
    
    def __init__(self, *args, **kwargs):
        self.content_object = kwargs.pop('content_object', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # اگر content_object مشخص شده باشد، فیلدهای مخفی را مقداردهی می‌کنیم
        if self.content_object:
            content_type = ContentType.objects.get_for_model(self.content_object)
            self.initial['content_type'] = f"{content_type.app_label}.{content_type.model}"
            self.initial['object_id'] = self.content_object.id
        
        # برای بلاگ، امتیاز اختیاری است
        if self.content_object and self.content_object._meta.model_name == 'blog':
            self.fields['rating'].required = False
            self.fields['rating'].widget = forms.Select(
                attrs={'class': 'form-select'},
                choices=[('', 'بدون امتیاز')] + [(i, i) for i in range(1, 6)]
            )
            self.fields['rating'].help_text = 'امتیازدهی اختیاری است'
    
    def clean(self):
        cleaned_data = super().clean()
        content_type_str = cleaned_data.get('content_type')
        object_id = cleaned_data.get('object_id')
        rating = cleaned_data.get('rating')
        comment = cleaned_data.get('comment', '').strip()
        
        # اعتبارسنجی متن نظر
        if comment and len(comment) < 3:
            self.add_error('comment', 'متن نظر خیلی کوتاه است.')
        
        # اعتبارسنجی content_type
        if content_type_str:
            try:
                app_label, model = content_type_str.split('.')
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                cleaned_data['content_type'] = content_type
            except (ValueError, ContentType.DoesNotExist):
                raise forms.ValidationError('نوع محتوای نامعتبر است.')
        
        # برای دوره‌ها، امتیاز الزامی است
        if content_type_str and 'course' in content_type_str:
            if rating is None or rating == '':
                self.add_error('rating', 'امتیاز برای دوره‌ها الزامی است.')
        
        # بررسی نظر تکراری (فقط برای نظرات اصلی)
        if self.user and content_type_str and object_id:
            content_type = cleaned_data.get('content_type')
            if Review.objects.filter(
                user=self.user,
                content_type=content_type,
                object_id=object_id,
                parent__isnull=True
            ).exists():
                raise forms.ValidationError('شما قبلاً برای این محتوا نظر داده‌اید.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # تنظیم کاربر
        if self.user:
            instance.user = self.user
        
        # تنظیم content_object
        if self.content_object:
            instance.content_object = self.content_object
        
        if commit:
            instance.save()
        
        return instance