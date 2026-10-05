from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.urls import reverse
from urllib.parse import urlencode

from .forms import ReviewForm
from .models import Review

REVIEWS_PER_PAGE = 5
DRAFT_SESSION_KEY = "review_drafts"


def target_key(model_name, object_id):
    return f"{model_name}:{object_id}"


def save_draft(request, model_name, object_id, data):
    """نگهداری متن نظر در سشن (مثلاً تا بعد از ورود به حساب یا اصلاح خطاها)."""
    drafts = request.session.get(DRAFT_SESSION_KEY, {})
    drafts[target_key(model_name, object_id)] = {
        "rating": data.get("rating", ""),
        "comment": data.get("comment", ""),
    }
    request.session[DRAFT_SESSION_KEY] = drafts


def pop_draft(request, model_name, object_id):
    drafts = request.session.get(DRAFT_SESSION_KEY)
    if not drafts:
        return None
    draft = drafts.pop(target_key(model_name, object_id), None)
    request.session[DRAFT_SESSION_KEY] = drafts
    return draft


def login_url_with_next(next_url):
    return f"{reverse('accounts:login')}?{urlencode({'next': next_url})}"


def build_review_context(request, target):
    """کانتکست مشترک بخش نظرات برای صفحه‌ی دوره و مقاله.

    target: یک نمونه از Course یا Blog.
    """
    model_name = target._meta.model_name
    is_course = model_name == "course"
    content_type = ContentType.objects.get_for_model(target)

    draft = pop_draft(request, model_name, target.pk)
    review_form = ReviewForm(initial=draft, rating_required=is_course)

    paginator = Paginator(target.get_reviews(), REVIEWS_PER_PAGE)
    reviews = paginator.get_page(request.GET.get("page"))
    # پیش‌نویس پاسخ‌ها (مثلاً بعد از بازگشت از صفحه‌ی ورود) روی هر نظر قرار می‌گیرد
    drafts = request.session.get(DRAFT_SESSION_KEY) or {}
    popped = False
    for review in reviews:
        review.reply_draft = drafts.pop(target_key("reply", review.pk), None)
        popped = popped or review.reply_draft is not None
    if popped:
        request.session[DRAFT_SESSION_KEY] = drafts
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=target.pk,
            parent__isnull=True,
            is_active=True,
        ).first()

    anchor_url = f"{target.get_absolute_url()}#reviews"
    return {
        "reviews": reviews,
        "review_form": review_form,
        "review_rating_required": is_course,
        "review_action_url": reverse("reviews:add", args=[model_name, target.pk]),
        "review_login_url": login_url_with_next(anchor_url),
        "user_review": user_review,
    }
