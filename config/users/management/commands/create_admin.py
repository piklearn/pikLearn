from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin user and test users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin',
            help='Admin password'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Admin email'
        )
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Also create test users (instructor and student)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        self.stdout.write('👤 Creating admin user...')
        
        # بررسی وجود کاربر ادمین
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return
        
        try:
            # ایجاد کاربر ادمین
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='مدیر',
                last_name='سیستم',
                role='admin',
                status='active'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!')
            )
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Password: {password}')
            self.stdout.write(f'   Email: {email}')
            
            # ایجاد کاربران تست
            if options['create_test_users']:
                self.create_test_users()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin: {str(e)}')
            )
    
    def create_test_users(self):
        self.stdout.write('📝 Creating test users...')
        
        test_users = [
            {
                'username': 'instructor1',
                'password': 'testpass123',
                'email': 'instructor1@example.com',
                'first_name': 'مدرس',
                'last_name': 'اول',
                'role': 'instructor'
            },
            {
                'username': 'instructor2',
                'password': 'testpass123',
                'email': 'instructor2@example.com',
                'first_name': 'مدرس',
                'last_name': 'دوم',
                'role': 'instructor'
            },
            {
                'username': 'student1',
                'password': 'testpass123',
                'email': 'student1@example.com',
                'first_name': 'دانشجو',
                'last_name': 'اول',
                'role': 'student'
            },
            {
                'username': 'student2',
                'password': 'testpass123',
                'email': 'student2@example.com',
                'first_name': 'دانشجو',
                'last_name': 'دوم',
                'role': 'student'
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            try:
                if not User.objects.filter(username=user_data['username']).exists():
                    user = User.objects.create_user(
                        username=user_data['username'],
                        password=user_data['password'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role'],
                        status='active'
                    )
                    created_count += 1
                    self.stdout.write(f'   ✅ Created: {user_data["username"]}')
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️ Error creating {user_data["username"]}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {created_count} test users!')
        )