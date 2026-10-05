from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery, FloatField
from django.db.models import Count, Avg, Q

from reviews.models import Review
from courses.models import Course

def index(req):
    rating_sq = (
                Review.objects.filter(
                    content_type=ContentType.objects.get_for_model(Course),
                    object_id=OuterRef('pk'),
                    parent__isnull=True,
                    is_approved=True,
                    rating__isnull=False,
                )
                .values('object_id')
                .annotate(avg=Avg('rating'))
                .values('avg')
            )
    home_courses = Course.objects.all()[:6].annotate(
                    student_count=Count(
                        'enrollments',
                        filter=Q(enrollments__is_active=True),
                        distinct=True,
                    ),
                    avg_rating=Coalesce(Subquery(rating_sq, output_field=FloatField()), 0.0),
                    final_price=Coalesce('discount_price', 'price'),
                )
    return render(req, 'index.html', context={'home_courses':home_courses})

