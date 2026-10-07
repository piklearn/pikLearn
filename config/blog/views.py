from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView

from reviews.utils import build_review_context
from .models import Blog, Category, Tag
import markdown
from django.utils.safestring import mark_safe

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
        published = Q(blogs__status=Blog.Status.PUBLISHED, blogs__published_at__lte=timezone.now())
        return {
            "categories": Category.objects.annotate(
                post_count=Count("blogs", filter=published, distinct=True)
            ).order_by("title"),
            "popular_tags": Tag.objects.annotate(
                post_count=Count("blogs", filter=published, distinct=True)
            ).filter(post_count__gt=0).order_by("-post_count", "title")[:30],
            "featured_blogs": self.get_base_queryset().filter(is_featured=True)[:5],
            "latest_blogs": self.get_base_queryset()[:5],
        }

    ORDER_CHOICES = [
        ("newest", "جدیدترین"),
        ("oldest", "قدیمی‌ترین"),
        ("popular", "پربازدیدترین"),
        ("featured", "ویژه‌ها"),
    ]

    def apply_ordering(self, qs):
        order = self.request.GET.get("order")
        mapping = {
            "oldest": ("published_at", "created_at"),
            "popular": ("-view_count", "-published_at"),
            "featured": ("-is_featured", "-published_at"),
        }
        return qs.order_by(*mapping.get(order, ("-published_at", "-created_at")))

    def get_filter_context(self):
        get = self.request.GET
        return {
            "order_choices": self.ORDER_CHOICES,
            "current": {
                "category": get.get("category", ""),
                "tag": get.get("tag", ""),
                "order": get.get("order", "newest"),
            },
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

        return self.apply_ordering(qs.distinct())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context.update(self.get_filter_context())
        context["total_count"] = context["paginator"].count if context.get("paginator") else 0
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
        return self.apply_ordering(
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
    template_name = "blog/list.html"
    context_object_name = "blogs"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return self.apply_ordering(self.get_base_queryset().filter(category=self.category))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context["querystring"] = self.get_querystring()
        context.update(self.get_filter_context())
        context["total_count"] = context["paginator"].count if context.get("paginator") else 0
        context["current_category"] = self.category
        context["current"]["category"] = self.category.slug
        context["meta_title"] = f"{self.category.title} | وبلاگ"
        context["meta_description"] = self.category.description or self.category.title
        context["canonical_url"] = self.request.build_absolute_uri(self.category.get_absolute_url())
        return context


class TagBlogListView(PublishedBlogQuerysetMixin, ListView):
    model = Blog
    template_name = "blog/list.html"
    context_object_name = "blogs"
    paginate_by = PAGE_SIZE

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return self.apply_ordering(self.get_base_queryset().filter(tags=self.tag))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_sidebar_context())
        context["querystring"] = self.get_querystring()
        context.update(self.get_filter_context())
        context["total_count"] = context["paginator"].count if context.get("paginator") else 0
        context["current_tag"] = self.tag
        context["current"]["tag"] = self.tag.slug
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
        # Atomic increment
        Blog.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        obj.refresh_from_db(fields=["view_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.object

        # رندر Markdown به HTML
        context["content_html"] = mark_safe(
            markdown.markdown(
                blog.content,
                extensions=[
                    "extra",          # جداول، لیست‌ها و ...
                    "fenced_code",    # بلاک‌های کد با ``` 
                    "codehilite",     # هایلایت کد (نیاز به pygments داره)
                    "toc",            # فهرست مطالب
                    "tables",
                    "nl2br",
                ],
                extension_configs={
                    "codehilite": {
                        "linenums": False,
                        "css_class": "highlight",
                    }
                }
            )
        )

        context.update(build_review_context(self.request, blog))

        context["meta_title"] = blog.meta_title
        context["meta_description"] = blog.meta_description
        context["canonical_url"] = self.request.build_absolute_uri(blog.get_absolute_url())
        return context