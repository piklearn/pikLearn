from django.contrib import messages
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator

from reviews.models import Review

from .forms import ReviewForm
from .models import Blog, Category, Tag

PAGE_SIZE = 9


class PublishedBlogQuerysetMixin:
    """Shared base queryset + sidebar context for every blog listing page."""

    def get_base_queryset(self):
        return (
            Blog.objects.filter(status=Blog.Status.PUBLISHED, published_at__lte=timezone.now())
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_sidebar_context(self):
        return {
            "categories": Category.objects.all(),
            "popular_tags": Tag.objects.all()[:20],
            "featured_blogs": self.get_base_queryset().filter(is_featured=True)[:5],
            "latest_blogs": self.get_base_queryset()[:5],
        }

    def get_querystring(self):
        """Current GET params (minus `page`) so pagination links keep filters."""
        params = self.request.GET.copy()
        params.pop("page", None)
        encoded = params.urlencode()
        return f"{encoded}&" if encoded else ""


class BlogListView(PublishedBlogQuerysetMixin, ListView):
    model = Blog
    template_name = "blog/list.html"
    context_object_name = "blogs"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        qs = self.get_base_queryset()

        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(content__icontains=query)
            )

        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context["querystring"] = self.get_querystring()
        context["search_query"] = self.request.GET.get("q", "")
        context["meta_title"] = "وبلاگ | پیک لرن"
        context["meta_description"] = "جدیدترین مقالات آموزشی پیک لرن"
        context["canonical_url"] = self.request.build_absolute_uri(reverse("blog:list"))
        return context


class BlogSearchView(BlogListView):
    """Same listing template/sidebar as BlogListView, scoped to a query."""

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        if not self.query:
            return Blog.objects.none()
        return (
            self.get_base_queryset()
            .filter(
                Q(title__icontains=self.query)
                | Q(short_description__icontains=self.query)
                | Q(content__icontains=self.query)
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.query
        context["meta_title"] = f"جستجوی «{self.query}» | وبلاگ"
        context["canonical_url"] = self.request.build_absolute_uri(reverse("blog:search"))
        return context


class CategoryBlogListView(PublishedBlogQuerysetMixin, ListView):
    model = Blog
    template_name = "blog/blog_list.html"
    context_object_name = "blogs"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return self.get_base_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context["querystring"] = self.get_querystring()
        context["current_category"] = self.category
        context["meta_title"] = f"{self.category.title} | وبلاگ"
        context["meta_description"] = self.category.description or self.category.title
        context["canonical_url"] = self.request.build_absolute_uri(self.category.get_absolute_url())
        return context


class TagBlogListView(PublishedBlogQuerysetMixin, ListView):
    model = Blog
    template_name = "blog/blog_list.html"
    context_object_name = "blogs"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return self.get_base_queryset().filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context["querystring"] = self.get_querystring()
        context["current_tag"] = self.tag
        context["meta_title"] = f"برچسب «{self.tag.title}» | وبلاگ"
        context["meta_description"] = f"مقالات مرتبط با برچسب {self.tag.title}"
        context["canonical_url"] = self.request.build_absolute_uri(self.tag.get_absolute_url())
        return context


class BlogDetailView(PublishedBlogQuerysetMixin, DetailView):
    model = Blog
    template_name = "blog/detail.html"
    context_object_name = "blog"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return self.get_base_queryset()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Atomic increment avoids a race condition between concurrent readers.
        Blog.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        obj.refresh_from_db(fields=["view_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.object

        context.setdefault("comment_form", ReviewForm())

        # Get reviews with pagination
        reviews = blog.get_reviews()
        paginator = Paginator(reviews, 5)
        page_number = self.request.GET.get('page')
        context['reviews'] = paginator.get_page(page_number)
        

        context["meta_title"] = blog.meta_title
        context["meta_description"] = blog.meta_description
        context["canonical_url"] = self.request.build_absolute_uri(blog.get_absolute_url())
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.allow_comments:
            messages.error(request, "ارسال نظر برای این مقاله غیرفعال است.")
            return redirect(self.object.get_absolute_url())

        if not request.user.is_authenticated:
            messages.error(request, "برای ارسال نظر ابتدا وارد حساب کاربری خود شوید.")
            login_url = reverse("accounts:login")
            return redirect(f"{login_url}?next={self.object.get_absolute_url()}")

        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = self.object
            comment.user = request.user
            comment.save()
            messages.success(request, "نظر شما ثبت شد و پس از تایید نمایش داده می‌شود.")
            return redirect(self.object.get_absolute_url())

        context = self.get_context_data(comment_form=form)
        return self.render_to_response(context)
