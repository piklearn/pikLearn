
from django import forms
from courses.models import CourseReview


class CourseReviewForm(forms.ModelForm):
    class Meta:
        model = CourseReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'نظر خود را بنویسید...'}),
        }
        labels = {
            'rating': 'امتیاز شما',
            'comment': 'نظر شما',
        }