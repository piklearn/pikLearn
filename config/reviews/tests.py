from datetime import timedelta
from urllib.parse import quote

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Blog, Category as BlogCategory
from courses.models import Category, Course
from users.models import CustomUser

from .models import Review


class ReviewSubmitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = CustomUser.objects.create_user("teacher", password="x")
        cls.user = CustomUser.objects.create_user("student", password="pass12345")
        cat = Category.objects.create(name="c", slug="c")
        cls.course = Course.objects.create(
            title="Django", slug="django", thumbnail="t.jpg", description="d",
            instructor=cls.teacher, category=cat, status="published",
        )
        bcat = BlogCategory.objects.create(title="b")
        cls.blog = Blog.objects.create(
            author=cls.teacher, category=bcat, title="post", slug="post",
            short_description="s", content="c word", image="i.jpg",
            status=Blog.Status.PUBLISHED, published_at=timezone.now() - timedelta(days=1),
        )

    def add_url(self, obj):
        return reverse("reviews:add", args=[obj._meta.model_name, obj.pk])

    def login_redirect(self, obj):
        return f"{reverse('accounts:login')}?next={quote(obj.get_absolute_url() + '#review-form', safe='')}"

    # ---- anonymous ----
    def test_anonymous_course_redirects_to_login(self):
        r = self.client.post(self.add_url(self.course), {"rating": 5, "comment": "عالی بود"})
        self.assertRedirects(r, self.login_redirect(self.course), fetch_redirect_response=False)
        self.assertEqual(Review.objects.count(), 0)

    def test_anonymous_blog_redirects_to_login(self):
        r = self.client.post(self.add_url(self.blog), {"comment": "مقاله خوبی بود"})
        self.assertRedirects(r, self.login_redirect(self.blog), fetch_redirect_response=False)
        self.assertEqual(Review.objects.count(), 0)

    def test_draft_is_restored_after_login(self):
        self.client.post(self.add_url(self.course), {"rating": 4, "comment": "متن پیش‌نویس"})
        self.client.login(username="student", password="pass12345")
        r = self.client.get(self.course.get_absolute_url())
        self.assertContains(r, "متن پیش‌نویس")
        self.assertContains(r, 'value="4"\n                                   checked')

    # ---- logged in ----
    def test_course_review_created_pending(self):
        self.client.force_login(self.user)
        r = self.client.post(self.add_url(self.course), {"rating": 5, "comment": "عالی بود"})
        self.assertRedirects(r, self.course.get_absolute_url() + "#reviews", fetch_redirect_response=False)
        review = Review.objects.get()
        self.assertEqual((review.user, review.content_object, review.rating), (self.user, self.course, 5))
        self.assertFalse(review.is_approved)

    def test_course_requires_rating(self):
        self.client.force_login(self.user)
        r = self.client.post(self.add_url(self.course), {"comment": "بدون امتیاز"})
        self.assertRedirects(r, self.course.get_absolute_url() + "#review-form", fetch_redirect_response=False)
        self.assertEqual(Review.objects.count(), 0)

    def test_blog_rating_optional(self):
        self.client.force_login(self.user)
        self.client.post(self.add_url(self.blog), {"rating": "", "comment": "مقاله خوبی بود"})
        review = Review.objects.get()
        self.assertIsNone(review.rating)
        self.assertEqual(review.content_object, self.blog)

    def test_duplicate_rejected(self):
        self.client.force_login(self.user)
        for _ in range(2):
            self.client.post(self.add_url(self.blog), {"comment": "مقاله خوبی بود"})
        self.assertEqual(Review.objects.count(), 1)

    def test_blog_comments_disabled(self):
        Blog.objects.filter(pk=self.blog.pk).update(allow_comments=False)
        self.client.force_login(self.user)
        self.client.post(self.add_url(self.blog), {"comment": "مقاله خوبی بود"})
        self.assertEqual(Review.objects.count(), 0)

    def test_short_comment_rejected(self):
        self.client.force_login(self.user)
        self.client.post(self.add_url(self.blog), {"comment": "ab"})
        self.assertEqual(Review.objects.count(), 0)

    def test_get_not_allowed_and_bad_model(self):
        self.assertEqual(self.client.get(self.add_url(self.course)).status_code, 405)
        self.client.force_login(self.user)
        r = self.client.post(reverse("reviews:add", args=["user", 1]), {"comment": "x" * 5})
        self.assertEqual(r.status_code, 404)

    # ---- rendering ----
    def test_pages_render_form_and_approved_reviews(self):
        ct = ContentType.objects.get_for_model(Course)
        Review.objects.create(user=self.user, content_type=ct, object_id=self.course.pk,
                              rating=5, comment="نظر تاییدشده", is_approved=True)
        for obj in (self.course, self.blog):
            r = self.client.get(obj.get_absolute_url())
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'id="review-form"')
            self.assertContains(r, self.add_url(obj))
            self.assertContains(r, "ورود و ثبت نظر")
        self.assertContains(self.client.get(self.course.get_absolute_url()), "نظر تاییدشده")

    def test_logged_in_user_with_review_sees_notice_not_form(self):
        self.client.force_login(self.user)
        self.client.post(self.add_url(self.blog), {"comment": "مقاله خوبی بود"})
        r = self.client.get(self.blog.get_absolute_url())
        self.assertContains(r, "پس از تایید مدیر")
        self.assertNotContains(r, 'id="reviewForm"')
