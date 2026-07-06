from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Load test data for blog app'

    def handle(self, *args, **options):
        # بررسی وجود کاربران
        if User.objects.count() < 3:
            self.stdout.write(self.style.WARNING('Creating test users...'))
            # ایجاد کاربران تست
            users_data = [
                {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin', 
                 'first_name': 'مدیر', 'last_name': 'سیستم', 'is_superuser': True, 'is_staff': True},
                {'username': 'instructor1', 'email': 'instructor1@example.com', 'password': 'testpass123',
                 'first_name': 'مدرس', 'last_name': 'اول'},
                {'username': 'instructor2', 'email': 'instructor2@example.com', 'password': 'testpass123',
                 'first_name': 'مدرس', 'last_name': 'دوم'},
                {'username': 'student1', 'email': 'student1@example.com', 'password': 'testpass123',
                 'first_name': 'دانشجو', 'last_name': 'اول'},
                {'username': 'student2', 'email': 'student2@example.com', 'password': 'testpass123',
                 'first_name': 'دانشجو', 'last_name': 'دوم'},
            ]
            
            for user_data in users_data:
                if not User.objects.filter(username=user_data['username']).exists():
                    if user_data.get('is_superuser'):
                        User.objects.create_superuser(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name']
                        )
                    else:
                        User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password'],
                            first_name=user_data['first_name'],
                            last_name=user_data['last_name']
                        )
                    self.stdout.write(f'  ✅ Created: {user_data["username"]}')
            
            self.stdout.write(self.style.SUCCESS('Test users created!'))

        # بارگذاری دیتا
        self.stdout.write(self.style.WARNING('Loading blog test data...'))
        
        # مسیر فایل fixture
        fixture_path = os.path.join(settings.BASE_DIR, 'blog', 'fixtures', 'initial_data.json')
        
        if os.path.exists(fixture_path):
            try:
                call_command('loaddata', fixture_path, verbosity=0)
                self.stdout.write(self.style.SUCCESS('Blog test data loaded successfully!'))
                
                # نمایش آمار
                from blog.models import Category, Tag, Blog, Comment
                self.stdout.write('\n📊 Statistics:')
                self.stdout.write(f'  📂 Categories: {Category.objects.count()}')
                self.stdout.write(f'  🏷️ Tags: {Tag.objects.count()}')
                self.stdout.write(f'  📝 Blogs: {Blog.objects.count()}')
                self.stdout.write(f'  💬 Comments: {Comment.objects.count()}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
        else:
            self.stdout.write(self.style.ERROR(f'Fixture file not found: {fixture_path}'))
            self.stdout.write(self.style.WARNING('Creating data programmatically...'))
            self.create_data_programmatically()

    def create_data_programmatically(self):
        """ایجاد دیتا به صورت برنامه‌نویسی در صورت نبود فایل fixture"""
        from blog.models import Category, Tag, Blog, Comment
        
        self.stdout.write('📝 Creating categories...')
        categories = self.create_categories()
        
        self.stdout.write('🏷️ Creating tags...')
        tags = self.create_tags()
        
        self.stdout.write('📝 Creating blog posts...')
        self.create_blogs(categories, tags)
        
        self.stdout.write('💬 Creating comments...')
        self.create_comments()
        
        self.stdout.write(self.style.SUCCESS('All data created successfully!'))

    def create_categories(self):
        """ایجاد دسته‌بندی‌ها"""
        from blog.models import Category
        
        categories_data = [
            {'title': 'برنامه‌نویسی', 'description': 'مقالات آموزشی در زمینه برنامه‌نویسی و توسعه نرم‌افزار', 'parent': None},
            {'title': 'طراحی وب', 'description': 'آموزش طراحی رابط کاربری و تجربه کاربری', 'parent': None},
            {'title': 'هوش مصنوعی', 'description': 'مقالات مرتبط با هوش مصنوعی و یادگیری ماشین', 'parent': None},
            {'title': 'پایتون', 'description': 'آموزش برنامه‌نویسی با زبان پایتون', 'parent': 'برنامه‌نویسی'},
            {'title': 'جنگو', 'description': 'آموزش فریمورک جنگو', 'parent': 'برنامه‌نویسی'},
            {'title': 'جاوااسکریپت', 'description': 'آموزش جاوااسکریپت و فریمورک‌های آن', 'parent': 'برنامه‌نویسی'},
            {'title': 'UI/UX Design', 'description': 'اصول طراحی رابط کاربری و تجربه کاربری', 'parent': 'طراحی وب'},
            {'title': 'یادگیری ماشین', 'description': 'مفاهیم و الگوریتم‌های یادگیری ماشین', 'parent': 'هوش مصنوعی'},
            {'title': 'پایگاه داده', 'description': 'آموزش کار با پایگاه‌های داده', 'parent': 'برنامه‌نویسی'},
            {'title': 'DevOps', 'description': 'آموزش مفاهیم DevOps و ابزارهای مرتبط', 'parent': None},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            parent = None
            if cat_data['parent']:
                parent = Category.objects.get(title=cat_data['parent'])
            
            category, created = Category.objects.get_or_create(
                title=cat_data['title'],
                defaults={
                    'description': cat_data['description'],
                    'parent': parent
                }
            )
            created_categories[cat_data['title']] = category
            if created:
                self.stdout.write(f'  ✅ Created category: {category.title}')
        
        return created_categories

    def create_tags(self):
        """ایجاد برچسب‌ها"""
        from blog.models import Tag
        
        tags_data = [
            'پایتون', 'جنگو', 'جاوااسکریپت', 'React', 'Vue.js',
            'هوش مصنوعی', 'یادگیری ماشین', 'طراحی UI', 'UX',
            'پایگاه داده', 'SQL', 'HTML', 'CSS', 'Git',
            'Docker', 'DevOps', 'REST API', 'GraphQL',
            'برنامه‌نویسی', 'آموزش'
        ]
        
        created_tags = {}
        for tag_title in tags_data:
            tag, created = Tag.objects.get_or_create(title=tag_title)
            created_tags[tag_title] = tag
            if created:
                self.stdout.write(f'  ✅ Created tag: {tag.title}')
        
        return created_tags

    def create_blogs(self, categories, tags):
        """ایجاد مقالات"""
        from blog.models import Blog
        
        # دریافت کاربران
        try:
            admin = User.objects.get(username='admin')
            instructor1 = User.objects.get(username='instructor1')
            instructor2 = User.objects.get(username='instructor2')
        except User.DoesNotExist:
            admin = User.objects.first()
            instructor1 = admin
            instructor2 = admin
        
        blogs_data = [
            {
                'author': admin,
                'category_title': 'جنگو',
                'title': 'آموزش جامع جنگو - قسمت اول',
                'short_description': 'در این مقاله با مفاهیم پایه فریمورک جنگو آشنا می‌شوید و اولین پروژه خود را می‌سازید.',
                'content': '<h2>مقدمه</h2><p>جنگو یک فریمورک قدرتمند و محبوب برای توسعه وب با زبان پایتون است.</p>',
                'image': 'blog/posts/2026/01/django-tutorial.jpg',
                'status': 'published',
                'is_featured': True,
                'tags': ['جنگو', 'پایتون', 'برنامه‌نویسی', 'آموزش']
            },
            {
                'author': instructor1,
                'category_title': 'پایتون',
                'title': '۱۰ ترفند پایتون که باید بدانید',
                'short_description': 'با این ۱۰ ترفند، کدهای پایتون خود را حرفه‌ای‌تر و کارآمدتر بنویسید.',
                'content': '<h2>۱۰ ترفند طلایی پایتون</h2><p>با این ترفندها کدهای خود را بهبود دهید.</p>',
                'image': 'blog/posts/2026/01/python-tricks.jpg',
                'status': 'published',
                'is_featured': True,
                'tags': ['پایتون', 'برنامه‌نویسی', 'آموزش']
            },
            {
                'author': instructor2,
                'category_title': 'UI/UX Design',
                'title': 'اصول طراحی رابط کاربری - راهنمای کامل',
                'short_description': 'با اصول کلیدی طراحی رابط کاربری آشنا شوید و تجربه کاربری بهتری ارائه دهید.',
                'content': '<h2>اصول طراحی رابط کاربری (UI Design)</h2><p>سادگی، ثبات، فیدبک، دسترسی و مدیریت خطا.</p>',
                'image': 'blog/posts/2026/02/ui-design.jpg',
                'status': 'published',
                'is_featured': False,
                'tags': ['طراحی UI', 'UX', 'طراحی وب']
            },
            {
                'author': admin,
                'category_title': 'یادگیری ماشین',
                'title': 'مقدمه‌ای بر یادگیری ماشین با پایتون',
                'short_description': 'با مفاهیم پایه یادگیری ماشین و کتابخانه‌های پایتون آشنا شوید.',
                'content': '<h2>مقدمه‌ای بر یادگیری ماشین</h2><p>یادگیری ماشین شاخه‌ای از هوش مصنوعی است.</p>',
                'image': 'blog/posts/2026/02/ml-intro.jpg',
                'status': 'published',
                'is_featured': True,
                'tags': ['هوش مصنوعی', 'یادگیری ماشین', 'پایتون', 'آموزش']
            },
            {
                'author': instructor1,
                'category_title': 'جاوااسکریپت',
                'title': 'جاوااسکریپت مدرن - ES6 و فراتر از آن',
                'short_description': 'با ویژگی‌های جدید جاوااسکریپت ES6 آشنا شوید.',
                'content': '<h2>جاوااسکریپت مدرن (ES6+)</h2><p>ویژگی‌های جدید جاوااسکریپت.</p>',
                'image': 'blog/posts/2026/02/javascript-es6.jpg',
                'status': 'draft',
                'is_featured': False,
                'tags': ['جاوااسکریپت', 'برنامه‌نویسی', 'React']
            },
            {
                'author': admin,
                'category_title': 'DevOps',
                'title': 'مقدمه‌ای بر Docker و Containerization',
                'short_description': 'با Docker و مفهوم Containerization آشنا شوید.',
                'content': '<h2>مقدمه‌ای بر Docker</h2><p>Containerization روشی برای بسته‌بندی برنامه‌ها.</p>',
                'image': 'blog/posts/2026/02/docker-intro.jpg',
                'status': 'published',
                'is_featured': False,
                'tags': ['Docker', 'DevOps', 'Git']
            },
            {
                'author': instructor2,
                'category_title': 'پایگاه داده',
                'title': 'آموزش SQL - دستورات پایه',
                'short_description': 'با دستورات پایه SQL برای کار با پایگاه‌های داده آشنا شوید.',
                'content': '<h2>دستورات پایه SQL</h2><p>SELECT, INSERT, UPDATE, DELETE</p>',
                'image': 'blog/posts/2026/02/sql-basics.jpg',
                'status': 'published',
                'is_featured': True,
                'tags': ['SQL', 'پایگاه داده', 'آموزش']
            }
        ]
        
        for blog_data in blogs_data:
            category = categories.get(blog_data['category_title'])
            if not category:
                continue
            
            blog, created = Blog.objects.get_or_create(
                title=blog_data['title'],
                defaults={
                    'author': blog_data['author'],
                    'category': category,
                    'slug': slugify(blog_data['title']),
                    'short_description': blog_data['short_description'],
                    'content': blog_data['content'],
                    'image': blog_data['image'],
                    'status': blog_data['status'],
                    'is_featured': blog_data['is_featured'],
                    'allow_comments': True,
                    'seo_title': blog_data['title'],
                    'seo_description': blog_data['short_description']
                }
            )
            
            if created:
                # افزودن تگ‌ها
                tag_list = []
                for tag_title in blog_data['tags']:
                    if tag_title in tags:
                        tag_list.append(tags[tag_title])
                blog.tags.set(tag_list)
                self.stdout.write(f'  ✅ Created blog: {blog.title}')

    def create_comments(self):
        """ایجاد نظرات"""
        from blog.models import Blog, Comment
        
        # دریافت کاربران
        try:
            student1 = User.objects.get(username='student1')
            student2 = User.objects.get(username='student2')
            instructor1 = User.objects.get(username='instructor1')
            instructor2 = User.objects.get(username='instructor2')
        except User.DoesNotExist:
            student1 = User.objects.first()
            student2 = student1
            instructor1 = student1
            instructor2 = student1
        
        blogs = Blog.objects.filter(status='published')
        if not blogs:
            return
        
        comments_data = [
            {'blog_title': 'آموزش جامع جنگو - قسمت اول', 'user': student1, 
             'content': 'مقاله خیلی خوبی بود! ممنون از اطلاعات مفیدتون.', 'is_approved': True},
            {'blog_title': 'آموزش جامع جنگو - قسمت اول', 'user': student2,
             'content': 'واقعاً جنگو رو خیلی خوب توضیح دادین.', 'is_approved': True},
            {'blog_title': '۱۰ ترفند پایتون که باید بدانید', 'user': student1,
             'content': 'ترفندهای پایتون عالی بود! ممنون از شما.', 'is_approved': True},
            {'blog_title': '۱۰ ترفند پایتون که باید بدانید', 'user': instructor2,
             'content': 'بسیار کاربردی و مفید بود.', 'is_approved': True},
            {'blog_title': 'اصول طراحی رابط کاربری - راهنمای کامل', 'user': student1,
             'content': 'UI/UX رو خیلی خوب توضیح دادین.', 'is_approved': False},
            {'blog_title': 'مقدمه‌ای بر یادگیری ماشین با پایتون', 'user': student2,
             'content': 'یادگیری ماشین رو خیلی روان توضیح دادین.', 'is_approved': True},
            {'blog_title': 'مقدمه‌ای بر یادگیری ماشین با پایتون', 'user': instructor1,
             'content': 'مطالب عالی بود.', 'is_approved': True},
            {'blog_title': 'آموزش SQL - دستورات پایه', 'user': student1,
             'content': 'دستورات SQL رو خیلی خوب و ساده توضیح دادین.', 'is_approved': True},
        ]
        
        for comment_data in comments_data:
            try:
                blog = Blog.objects.get(title=comment_data['blog_title'])
                comment, created = Comment.objects.get_or_create(
                    blog=blog,
                    user=comment_data['user'],
                    content=comment_data['content'],
                    defaults={
                        'is_approved': comment_data['is_approved']
                    }
                )
                if created:
                    self.stdout.write(f'  ✅ Created comment: {comment.user} → {blog.title}')
            except Blog.DoesNotExist:
                continue