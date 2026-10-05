from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """فرم ثبت نظر برای دوره‌ها (امتیاز الزامی) و مقاله‌های بلاگ (امتیاز اختیاری)."""

    RATING_CHOICES = [(i, str(i)) for i in range(5, 0, -1)]
    MIN_LENGTH = 3
    MAX_LENGTH = 2000

    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        empty_value=None,
        required=False,
        label="امتیاز شما",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "maxlength": 2000,
                    "placeholder": "نظر خود را بنویسید...",
                }
            ),
        }
        labels = {"comment": "نظر شما"}

    def __init__(self, *args, rating_required=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.rating_required = rating_required
        self.fields["comment"].required = True

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None and self.rating_required:
            raise forms.ValidationError("امتیاز برای دوره‌ها الزامی است.")
        return rating

    def clean_comment(self):
        comment = (self.cleaned_data.get("comment") or "").strip()
        if len(comment) < self.MIN_LENGTH:
            raise forms.ValidationError("متن نظر خیلی کوتاه است.")
        if len(comment) > self.MAX_LENGTH:
            raise forms.ValidationError(f"متن نظر نباید بیشتر از {self.MAX_LENGTH} کاراکتر باشد.")
        return comment

class ReplyForm(ReviewForm):
    """فرم پاسخ به نظر: فقط متن (بدون امتیاز)."""

    rating = None  # فیلد امتیاز را حذف می‌کند

    class Meta(ReviewForm.Meta):
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "maxlength": 2000,
                    "placeholder": "پاسخ خود را بنویسید...",
                }
            ),
        }
