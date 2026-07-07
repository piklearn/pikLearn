from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, UpdateView, View

from courses.models import Wishlist
from notifications.models import Notification
from payments.models import Purchase

from .forms import ProfileForm
from .utils import course_progress_percent, get_last_watched_course, get_recent_activity


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        purchases = Purchase.objects.filter(user=user).select_related("course")
        purchased_courses = [p.course for p in purchases]

        progress_by_course = {
            course.id: course_progress_percent(user, course) for course in purchased_courses
        }
        in_progress_count = sum(1 for pct in progress_by_course.values() if 0 < pct < 100)
        completed_count = sum(1 for pct in progress_by_course.values() if pct == 100)
        avg_progress = (
            round(sum(progress_by_course.values()) / len(progress_by_course))
            if progress_by_course else 0
        )

        last_course, last_video = get_last_watched_course(user)

        context.update({
            "purchased_courses_count": len(purchased_courses),
            "in_progress_count": in_progress_count,
            "avg_progress": avg_progress,
            "certificates_count": completed_count,  # real proxy value; certificate issuance itself is not yet implemented
            "continue_course": last_course,
            "continue_video": last_video,
            "continue_progress": progress_by_course.get(last_course.id, 0) if last_course else 0,
            "recent_activity": get_recent_activity(user),
            "unread_notifications": Notification.objects.filter(user=user, status="unread")[:5],
        })
        return context


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = "dashboard/my_courses.html"
    context_object_name = "purchases"
    paginate_by = 9

    def get_queryset(self):
        return (
            Purchase.objects.filter(user=self.request.user)
            .select_related("course", "course__instructor")
            .order_by("-purchase_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["progress_by_course_id"] = {
            purchase.course_id: course_progress_percent(user, purchase.course)
            for purchase in context["purchases"]
        }
        return context


class WishlistView(LoginRequiredMixin, ListView):
    template_name = "dashboard/wishlist.html"
    context_object_name = "wishlist_items"
    paginate_by = 12

    def get_queryset(self):
        return (
            Wishlist.objects.filter(user=self.request.user)
            .select_related("course", "course__instructor")
        )


class WishlistRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Wishlist, pk=pk, user=request.user)
        item.delete()
        messages.success(request, "دوره از لیست علاقه‌مندی‌ها حذف شد.")
        return redirect("dashboard:wishlist")


class OrdersView(LoginRequiredMixin, ListView):
    template_name = "dashboard/orders.html"
    context_object_name = "purchases"
    paginate_by = 15

    def get_queryset(self):
        return (
            Purchase.objects.filter(user=self.request.user)
            .select_related("course")
            .order_by("-purchase_date")
        )


class OrderInvoiceView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = "dashboard/order_invoice.html"
    context_object_name = "purchase"

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user).select_related("course", "user")


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "dashboard/profile.html"
    success_url = reverse_lazy("dashboard:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات پروفایل با موفقیت به‌روزرسانی شد.")
        return super().form_valid(form)