from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Load test data for courses app'

    def handle(self, *args, **options):
        # بررسی وجود کاربران
        if User.objects.count() < 3:
            self.stdout.write(self.style.WARNING('Creating test users...'))
            # ایجاد کاربران تست
            for i in range(1, 4):
                User.objects.create_user(
                    username=f'instructor{i}',
                    email=f'instructor{i}@example.com',
                    password='testpass123',
                    first_name=f'مدرس',
                    last_name=f'{i}'
                )
            self.stdout.write(self.style.SUCCESS('Test users created!'))

        # بارگذاری دیتا
        self.stdout.write(self.style.WARNING('Loading test data...'))
        
        # مسیر فایل fixture
        fixture_path = os.path.join(settings.BASE_DIR, 'courses', 'fixtures', 'initial_data.json')
        
        if os.path.exists(fixture_path):
            call_command('loaddata', fixture_path)
            self.stdout.write(self.style.SUCCESS('Test data loaded successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Fixture file not found!'))