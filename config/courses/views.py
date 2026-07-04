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
from courses.models import Course, Chapter, Video, CourseReview, CourseFAQ, CourseResource, CourseEnrollment, Wishlist
from courses.forms import CourseReviewForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
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
        
        # Get reviews with pagination
        reviews = course.course_reviews.filter(is_approved=True)
        paginator = Paginator(reviews, 5)
        page_number = self.request.GET.get('page')
        context['reviews'] = paginator.get_page(page_number)
        
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


class CourseListView(ListView):
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        qs = super().get_queryset().filter(status='published')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        
        # Filter by price
        price_type = self.request.GET.get('price')
        if price_type == 'free':
            qs = qs.filter(price=0)
        elif price_type == 'paid':
            qs = qs.filter(price__gt=0)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Ordering
        order = self.request.GET.get('order')
        if order == 'newest':
            qs = qs.order_by('-created_date')
        elif order == 'popular':
            qs = qs.annotate(student_count=Count('enrollments')).order_by('-student_count')
        elif order == 'rating':
            qs = qs.annotate(avg_rating=Avg('course_reviews__rating')).order_by('-avg_rating')
        else:
            qs = qs.order_by('-created_date')
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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


@require_POST
def review_like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'لطفاً وارد شوید.'}, status=401)
    
    import json
    data = json.loads(request.body)
    review_id = data.get('review_id')
    action = data.get('action')
    
    review = get_object_or_404(CourseReview, id=review_id)
    
    if action == 'like':
        review.likes.add(request.user)
    else:
        review.likes.remove(request.user)
    
    return JsonResponse({
        'success': True,
        'like_count': review.get_like_count()
    })


@require_POST
def review_report(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'لطفاً وارد شوید.'}, status=401)
    
    import json
    data = json.loads(request.body)
    review_id = data.get('review_id')
    
    # Here you would implement report functionality
    # For now, just mark as reported
    review = get_object_or_404(CourseReview, id=review_id)
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
    
