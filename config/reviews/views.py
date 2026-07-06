from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView

from courses.models import Course
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "form-control"}
            ),
            "comment": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("امتیاز باید بین ۱ تا ۵ باشد.")
        return rating


class CreateReviewView(LoginRequiredMixin, CreateView):
    """Create a review for a course. One review per (user, course)."""

    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=kwargs["course_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context

    def form_valid(self, form):
        if Review.objects.filter(user=self.request.user, course=self.course).exists():
            messages.warning(self.request, "شما قبلاً برای این دوره نظر ثبت کرده‌اید.")
            return redirect(self.get_success_url())

        form.instance.user = self.request.user
        form.instance.course = self.course

        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError:
            messages.warning(self.request, "شما قبلاً برای این دوره نظر ثبت کرده‌اید.")
            return redirect(self.get_success_url())

        messages.success(
            self.request, "نظر شما ثبت شد و پس از تایید نمایش داده می‌شود."
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.course.get_absolute_url()


class UpdateReviewView(LoginRequiredMixin, UpdateView):
    """Only the review's owner may edit it, and only before approval."""

    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"

    def get_queryset(self):
        # Scoping to the current user means another user's review 404s
        # instead of leaking its existence via a 403.
        return Review.objects.filter(user=self.request.user, is_active=True)

    def get_object(self, queryset=None):
        review = super().get_object(queryset)
        if review.is_approved:
            raise PermissionDenied("پس از تایید، امکان ویرایش نظر وجود ندارد.")
        return review

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
        messages.success(self.request, "نظر شما به‌روزرسانی شد.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را بررسی کنید.")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    """Soft-delete: only the owner or staff may remove a review."""

    model = Review
    template_name = "reviews/review_confirm_delete.html"

    def get_queryset(self):
        qs = Review.objects.filter(is_active=True)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def form_valid(self, form):
        success_url = self.get_success_url()
        with transaction.atomic():
            self.object.is_active = False
            self.object.save(update_fields=["is_active", "updated_at"])
        messages.success(self.request, "نظر حذف شد.")
        return redirect(success_url)

    def get_success_url(self):
        return self.object.course.get_absolute_url()
