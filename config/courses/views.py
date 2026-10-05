from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from dal import autocomplete
from courses.models import Course,Category, Chapter, Video, CourseFAQ, CourseResource, CourseEnrollment, Wishlist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
import json
from django.contrib.contenttypes.models import ContentType
from reviews.models import Review
from reviews.utils import build_review_context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/detail.html'
    context_object_name = 'course'
    
    def get_object(self, queryset=None):
        # Support both slug and pk
        if 'slug' in self.kwargs:
            # Try to get the course with status published, or get it anyway
            try:
                return Course.objects.get(slug=self.kwargs['slug'])
            except Course.DoesNotExist:
                # If not found by slug, try by ID
                try:
                    return Course.objects.get(id=self.kwargs['slug'])
                except (Course.DoesNotExist, ValueError):
                    raise Http404("Course not found")
        
        # If pk is provided (fallback)
        if 'pk' in self.kwargs:
            try:
                return Course.objects.get(id=self.kwargs['pk'])
            except Course.DoesNotExist:
                raise Http404("Course not found")
        
        return super().get_object(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Increment view count
        course.views += 1
        course.save(update_fields=['views'])
        
        # Get course data
        context['chapters'] = course.get_chapters()
        context['requirements'] = course.get_requirements()
        context['learn_points'] = course.get_learn_points()
        context['faqs'] = course.faqs.all()
        context['resources'] = course.resources.all()
        
        # Reviews: list + submit form (shared with blog)
        context.update(build_review_context(self.request, course))
        
        # Get related courses
        related_courses = Course.objects.filter(
            Q(category=course.category) | 
            Q(instructor=course.instructor)
        ).exclude(id=course.id)[:4]
        context['related_courses'] = related_courses
        
        # Get user enrollment status
         # Get user enrollment and wishlist status
        if self.request.user.is_authenticated:
            context['is_enrolled'] = course.enrollments.filter(
                user=self.request.user, 
                is_active=True
            ).exists()
            context['user_progress'] = course.enrollments.filter(
                user=self.request.user
            ).first()
            # Check if course is in wishlist
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                course=course
            ).exists()
        else:
            context['is_enrolled'] = False
            context['user_progress'] = None
            context['in_wishlist'] = False
        
        # ... rest of the code ...
        
        return context
class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        
        qs = Course.objects.all()  # به دست آوردن همه دوره‌ها


        query = self.request.GET.get('query', '')  # به دست آوردن query از URL
        if query:  
            qs = qs.filter(title__icontains=query)
        # فیلتر براساس ورودی کاربر
        # print("query:",self.q)
        # if self.q:  # اگر ورودی وجود داشته باشد
        #     qs = qs.filter(title__icontains=self.q)  # جستجو در عنوان

        return qs


def _descendant_ids(category):
    """شناسه‌ی دسته به‌همراه تمام زیردسته‌های آن (تا هر عمقی)."""
    ids, frontier = [category.id], [category.id]
    while frontier:
        frontier = list(
            Category.objects.filter(parent_category_id__in=frontier)
            .values_list('id', flat=True)
        )
        ids.extend(frontier)
    return ids


class CourseListView(ListView):
    """لیست دوره‌ها با جست‌وجو و فیلتر.

    پارامترهای GET: q (یا search), category, difficulty, price, language,
    certificate, order
    """
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12

    ORDER_CHOICES = [
        ('newest', 'جدیدترین'),
        ('popular', 'پرمخاطب‌ترین'),
        ('rating', 'بیشترین امتیاز'),
        ('price_asc', 'ارزان‌ترین'),
        ('price_desc', 'گران‌ترین'),
    ]
    PRICE_CHOICES = [
        ('free', 'رایگان'),
        ('paid', 'پولی'),
        ('discount', 'دارای تخفیف'),
    ]

    def get_queryset(self):
        from django.db.models import OuterRef, Subquery, FloatField
        from django.db.models.functions import Coalesce

        get = self.request.GET
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
        qs = (
            Course.objects.filter(status='published')
            .select_related('instructor', 'category')
            .annotate(
                student_count=Count(
                    'enrollments',
                    filter=Q(enrollments__is_active=True),
                    distinct=True,
                ),
                avg_rating=Coalesce(Subquery(rating_sq, output_field=FloatField()), 0.0),
                final_price=Coalesce('discount_price', 'price'),
            )
        )

        search = (get.get('q') or get.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(short_description__icontains=search)
                | Q(description__icontains=search)
                | Q(instructor__username__icontains=search)
            )

        category = get.get('category')
        if category:
            cat = Category.objects.filter(slug=category).first()
            qs = qs.filter(category_id__in=_descendant_ids(cat)) if cat else qs.none()

        difficulty = get.get('difficulty')
        if difficulty in dict(Course.DIFFICULTY_LEVELS):
            qs = qs.filter(difficulty_level=difficulty)

        language = get.get('language')
        if language in dict(Course.LANGUAGE_CHOICES):
            qs = qs.filter(language=language)

        price_type = get.get('price')
        if price_type == 'free':
            qs = qs.filter(final_price=0)
        elif price_type == 'paid':
            qs = qs.filter(final_price__gt=0)
        elif price_type == 'discount':
            qs = qs.filter(discount_price__isnull=False, price__gt=0)

        if get.get('certificate') == '1':
            qs = qs.filter(has_certificate=True)

        ordering = {
            'popular': ('-student_count', '-views'),
            'rating': ('-avg_rating', '-student_count'),
            'price_asc': ('final_price', '-created_date'),
            'price_desc': ('-final_price', '-created_date'),
        }.get(get.get('order'), ('-created_date',))
        return qs.order_by(*ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get = self.request.GET

        # دسته‌ها به‌صورت درخت، همراه با تعداد دوره‌های منتشرشده
        published = Course.objects.filter(status='published')
        counts = dict(
            published.values_list('category_id').annotate(c=Count('id')).values_list('category_id', 'c')
        )
        roots = list(Category.objects.filter(parent_category__isnull=True).order_by('name'))
        for root in roots:
            root.children_list = list(root.subcategories.all().order_by('name'))
            for child in root.children_list:
                child.course_count = counts.get(child.id, 0)
            root.course_count = counts.get(root.id, 0) + sum(c.course_count for c in root.children_list)

        params = get.copy()
        params.pop('page', None)
        encoded = params.urlencode()

        selected_category = Category.objects.filter(slug=get.get('category')).first() if get.get('category') else None
        def chip(label, *keys):
            """چیپ فیلتر فعال + لینکی که همان فیلتر را حذف می‌کند."""
            rest = get.copy()
            rest.pop('page', None)
            for k in keys:
                rest.pop(k, None)
            query = rest.urlencode()
            url = f"?{query}" if query else self.request.path
            return {'label': label, 'url': url}

        active = []
        if get.get('q') or get.get('search'):
            active.append(chip('جست‌وجو: ' + (get.get('q') or get.get('search')), 'q', 'search'))
        if selected_category:
            active.append(chip(selected_category.name, 'category'))
        if get.get('difficulty') in dict(Course.DIFFICULTY_LEVELS):
            active.append(chip(dict(Course.DIFFICULTY_LEVELS)[get.get('difficulty')], 'difficulty'))
        if get.get('language') in dict(Course.LANGUAGE_CHOICES):
            active.append(chip(dict(Course.LANGUAGE_CHOICES)[get.get('language')], 'language'))
        if get.get('price') in dict(self.PRICE_CHOICES):
            active.append(chip(dict(self.PRICE_CHOICES)[get.get('price')], 'price'))
        if get.get('certificate') == '1':
            active.append(chip('دارای گواهینامه', 'certificate'))

        context.update({
            'categories': roots,
            'selected_category': selected_category,
            'querystring': f'{encoded}&' if encoded else '',
            'search_query': get.get('q') or get.get('search') or '',
            'current': {
                'category': get.get('category', ''),
                'difficulty': get.get('difficulty', ''),
                'language': get.get('language', ''),
                'price': get.get('price', ''),
                'certificate': get.get('certificate', ''),
                'order': get.get('order', 'newest'),
            },
            'active_filters': active,
            'difficulty_choices': Course.DIFFICULTY_LEVELS,
            'language_choices': Course.LANGUAGE_CHOICES,
            'price_choices': self.PRICE_CHOICES,
            'order_choices': self.ORDER_CHOICES,
            'total_count': context['paginator'].count if context.get('paginator') else len(context['courses']),
        })
        return context


class CategoryListView(ListView):
    """صفحه‌ی دسته‌بندی‌ها: دسته‌های اصلی، زیردسته‌ها و تعداد دوره‌ها."""
    model = Category
    template_name = 'courses/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent_category__isnull=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published = Course.objects.filter(status='published')
        counts = dict(
            published.values_list('category_id').annotate(c=Count('id')).values_list('category_id', 'c')
        )
        total = 0
        for root in context['categories']:
            root.children_list = list(root.subcategories.all().order_by('name'))
            for child in root.children_list:
                child.course_count = counts.get(child.id, 0)
            root.course_count = counts.get(root.id, 0) + sum(c.course_count for c in root.children_list)
            total += root.course_count
        context['total_courses'] = total
        return context


# API Views for AJAX operations
@require_POST
def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'لطفاً ابتدا وارد شوید.'}, status=401)
    
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'ثبت‌نام با موفقیت انجام شد.'})
    else:
        return JsonResponse({'success': False, 'message': 'شما قبلاً در این دوره ثبت‌نام کرده‌اید.'})


 #============================================
# لایک کردن نظر
# ============================================
@require_POST
def review_like(request):
    """لایک یا آنلایک کردن یک نظر"""
    if not request.user.is_authenticated:
        return JsonResponse(
            {'success': False, 'message': 'لطفاً وارد شوید.'}, 
            status=401
        )
    
    try:
        data = json.loads(request.body)
        review_id = data.get('review_id')
        action = data.get('action')  # 'like' یا 'unlike'
        
        # دریافت نظر
        review = get_object_or_404(Review, id=review_id)
        
        # بررسی دسترسی: کاربر نمی‌تواند به نظر خودش لایک بدهد
        if review.user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'شما نمی‌توانید به نظر خودتان لایک بدهید.'
            }, status=400)
        
        # انجام عملیات لایک/آنلایک
        if action == 'like':
            review.likes.add(request.user)
            is_liked = True
        elif action == 'unlike':
            review.likes.remove(request.user)
            is_liked = False
        else:
            return JsonResponse({
                'success': False,
                'message': 'عملیات نامعتبر.'
            }, status=400)
        
        # تعداد کل لایک‌ها
        like_count = review.likes.count()
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'like_count': like_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'داده‌های ارسال شده نامعتبر هستند.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در انجام عملیات: {str(e)}'
        }, status=500)

    """دریافت نظرات یک محتوا (دوره یا بلاگ)"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'لطفاً وارد شوید.'
        }, status=401)
    
    try:
        content_type = request.GET.get('content_type')  # 'course' یا 'blog'
        object_id = request.GET.get('object_id')
        
        if not content_type or not object_id:
            return JsonResponse({
                'success': False,
                'message': 'پارامترهای مورد نیاز ارسال نشده است.'
            }, status=400)
        
        # دریافت ContentType
        try:
            ct = ContentType.objects.get(app_label='courses', model=content_type)
        except ContentType.DoesNotExist:
            try:
                ct = ContentType.objects.get(app_label='blog', model=content_type)
            except ContentType.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'نوع محتوای نامعتبر.'
                }, status=400)
        
        # دریافت نظرات
        reviews = Review.objects.filter(
            content_type=ct,
            object_id=object_id,
            is_approved=True,
            is_active=True
        ).select_related('user').order_by('-created_at')
        
        # تبدیل به لیست
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user': {
                    'id': review.user.id,
                    'username': review.user.username,
                    'full_name': review.user.get_full_name() or review.user.username,
                    'avatar': getattr(review.user, 'avatar', None)  # اگر فیلد آواتار دارید
                },
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M'),
                'like_count': review.likes.count(),
                'is_liked': request.user in review.likes.all() if request.user.is_authenticated else False,
                'is_owner': review.user == request.user if request.user.is_authenticated else False,
            })
        
        return JsonResponse({
            'success': True,
            'reviews': reviews_data,
            'total': len(reviews_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در دریافت نظرات: {str(e)}'
        }, status=500)


@require_POST
def review_report(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'لطفاً وارد شوید.'}, status=401)
    
    import json
    data = json.loads(request.body)
    review_id = data.get('review_id')
    # Here you would implement report functionality
    # For now, just mark as reported
    review = get_object_or_404(Review, id=review_id)
    # review.is_reported = True
    # review.save()
    
    return JsonResponse({'success': True})


@require_POST
@login_required
def toggle_wishlist(request, course_id):
    """Toggle course in user's wishlist"""
    import json
    data = json.loads(request.body) if request.body else {}
    action = data.get('action')
    
    course = get_object_or_404(Course, id=course_id)
    
    # Get or create wishlist item
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if action == 'remove':
        wishlist_item.delete()
        return JsonResponse({
            'success': True,
            'action': 'removed',
            'message': 'دوره از علاقه‌مندی‌ها حذف شد.'
        })
    else:  # 'add' or default
        return JsonResponse({
            'success': True,
            'action': 'added',
            'message': 'دوره به علاقه‌مندی‌ها اضافه شد.'
        })
    
