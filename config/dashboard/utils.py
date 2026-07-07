from itertools import chain

from courses.models import UserProgress, Wishlist
from payments.models import Purchase
from reviews.models import Review


def course_progress_percent(user, course):
    """Percentage of a course's videos the user has watched."""
    total = course.videos.count()
    if not total:
        return 0
    watched = (
        UserProgress.objects.filter(user=user, course=course, completion_status="watched")
        .values("video").distinct().count()
    )
    return round((watched / total) * 100)


def get_last_watched_course(user):
    """Most recently-touched course, for the "Continue Learning" section."""
    progress = (
        UserProgress.objects.filter(user=user)
        .select_related("course", "video")
        .order_by("-last_watched")
        .first()
    )
    if progress:
        return progress.course, progress.video
    return None, None


def get_recent_activity(user, limit=8):
    """
    Merge a few different tables into one timeline.

    There's no dedicated activity-log model in the project, so this stitches
    together the events that already exist. If a real audit-log model is
    ever added, this function is the only place that needs to change.
    """
    events = []

    for purchase in Purchase.objects.filter(user=user).select_related("course")[:limit]:
        events.append({
            "type": "purchase",
            "icon": "bi-bag-check",
            "text": f"دوره «{purchase.course.title}» را خریداری کردید",
            "timestamp": purchase.purchase_date,
        })

    watched_videos = (
        UserProgress.objects.filter(user=user, completion_status="watched")
        .select_related("video", "course")
        .order_by("-last_watched")[:limit]
    )
    for progress in watched_videos:
        events.append({
            "type": "lesson",
            "icon": "bi-play-circle",
            "text": f"درس «{progress.video.title}» از دوره «{progress.course.title}» را تماشا کردید",
            "timestamp": progress.last_watched,
        })

    for wish in Wishlist.objects.filter(user=user).select_related("course")[:limit]:
        events.append({
            "type": "wishlist",
            "icon": "bi-heart",
            "text": f"دوره «{wish.course.title}» را به علاقه‌مندی‌ها اضافه کردید",
            "timestamp": wish.added_at,
        })

    for review in Review.objects.filter(user=user, is_active=True).select_related('user', 'content_type', 'parent')[:limit]:
        # بررسی می‌کنیم که نظر مربوط به دوره است
        if review.content_type.model == 'course':
            course = review.content_object  # دریافت شیء دوره
            events.append({
                "type": "review",
                "icon": "bi-star",
                "text": f"برای دوره «{course.title}» نظر ثبت کردید",
                "timestamp": review.created_at,
            })

    events.sort(key=lambda e: e["timestamp"], reverse=True)
    return events[:limit]