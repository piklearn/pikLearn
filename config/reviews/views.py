from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from blog.models import Blog
from courses.models import Course

from .forms import ReplyForm, ReviewForm
from .models import Review
from .utils import login_url_with_next, save_draft


def _get_target(model_name, object_id):
    if model_name == "course":
        return get_object_or_404(Course, pk=object_id)
    if model_name == "blog":
        return get_object_or_404(
            Blog,
            pk=object_id,
            status=Blog.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
    raise Http404("نوع محتوا نامعتبر است.")


@require_POST
def add_review(request, model_name, object_id):
    """ثبت نظر برای دوره یا مقاله.

    کاربر وارد‌نشده به صفحه‌ی ورود منتقل می‌شود و بعد از ورود به همین بخش
    از صفحه برمی‌گردد (متن نوشته‌شده‌ی او در سشن نگه داشته می‌شود).
    """
    target = _get_target(model_name, object_id)
    back_url = f"{target.get_absolute_url()}#reviews"
    form_url = f"{target.get_absolute_url()}#review-form"

    if not request.user.is_authenticated:
        save_draft(request, model_name, object_id, request.POST)
        return redirect(login_url_with_next(form_url))

    if model_name == "blog" and not target.allow_comments:
        messages.error(request, "ارسال نظر برای این مقاله غیرفعال است.")
        return redirect(back_url)

    content_type = ContentType.objects.get_for_model(target)
    already_reviewed = Review.objects.filter(
        user=request.user,
        content_type=content_type,
        object_id=target.pk,
        parent__isnull=True,          # ← اضافه شد
    ).exists()
    if already_reviewed:
        messages.warning(request, "شما قبلاً برای این محتوا نظر ثبت کرده‌اید.")
        return redirect(back_url)

    # instance از قبل به کاربر و محتوا وصل است تا Review.clean() درست کار کند
    form = ReviewForm(
        request.POST,
        instance=Review(user=request.user, content_object=target, is_approved=False),
        rating_required=(model_name == "course"),
    )
    if not form.is_valid():
        save_draft(request, model_name, object_id, request.POST)
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect(form_url)

    review = form.save(commit=False)  # is_approved=False: بعد از تایید مدیر نمایش داده می‌شود
    try:
        with transaction.atomic():
            review.save()
    except (ValidationError, IntegrityError):
        messages.warning(request, "شما قبلاً برای این محتوا نظر ثبت کرده‌اید.")
        return redirect(back_url)

    messages.success(request, "نظر شما ثبت شد و پس از تایید نمایش داده می‌شود.")
    return redirect(back_url)

@require_POST
def add_reply(request, parent_id):
    """ثبت پاسخ به یک نظر اصلی (تاییدشده). پاسخ بعد از تایید مدیر نمایش داده می‌شود."""
    parent = get_object_or_404(Review.objects.approved(), pk=parent_id, parent__isnull=True)
    target = parent.content_object
    if target is None:
        raise Http404("محتوا پیدا نشد.")
    if isinstance(target, Blog) and (
        target.status != Blog.Status.PUBLISHED or target.published_at > timezone.now()
    ):
        raise Http404("محتوا پیدا نشد.")

    page = request.POST.get("page", "")
    query = f"?page={page}" if page.isdigit() else ""
    back_url = f"{target.get_absolute_url()}{query}#review-{parent.pk}"

    if not request.user.is_authenticated:
        save_draft(request, "reply", parent.pk, request.POST)
        return redirect(login_url_with_next(back_url))

    if isinstance(target, Blog) and not target.allow_comments:
        messages.error(request, "ارسال نظر برای این مقاله غیرفعال است.")
        return redirect(back_url)

    form = ReplyForm(
        request.POST,
        instance=Review(
            user=request.user,
            content_type=parent.content_type,
            object_id=parent.object_id,
            parent=parent,
            is_approved=False,
        ),
    )
    if not form.is_valid():
        save_draft(request, "reply", parent.pk, request.POST)
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect(back_url)

    try:
        with transaction.atomic():
            form.save()
    except (ValidationError, IntegrityError):
        messages.error(request, "ثبت پاسخ انجام نشد. لطفاً دوباره تلاش کنید.")
        return redirect(back_url)

    messages.success(request, "پاسخ شما ثبت شد و پس از تایید نمایش داده می‌شود.")
    return redirect(back_url)
