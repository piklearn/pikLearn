from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Load initial/test data for settings, courses, and blog"

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            nargs="*",
            choices=["settings", "courses", "blog", "users"],
            help="Only load specific parts. Example: --only settings blog",
        )

    def handle(self, *args, **options):
        targets = options.get("only") or ["users", "settings", "courses", "blog"]

        self.stdout.write(self.style.WARNING("Starting data load..."))

        if "users" in targets:
            self.load_users()

        if "settings" in targets:
            self.load_fixture("settings")

        if "courses" in targets:
            self.load_fixture("courses")

        if "blog" in targets:
            self.load_fixture("blog")

        self.stdout.write(self.style.SUCCESS("All selected data loaded successfully!"))

    def load_users(self):
        self.stdout.write("Creating base users if needed...")

        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin",
                "first_name": "مدیر",
                "last_name": "سیستم",
                "is_superuser": True,
                "is_staff": True,
            },
            {
                "username": "instructor1",
                "email": "instructor1@example.com",
                "password": "testpass123",
                "first_name": "مدرس",
                "last_name": "اول",
            },
            {
                "username": "instructor2",
                "email": "instructor2@example.com",
                "password": "testpass123",
                "first_name": "مدرس",
                "last_name": "دوم",
            },
            {
                "username": "student1",
                "email": "student1@example.com",
                "password": "testpass123",
                "first_name": "دانشجو",
                "last_name": "اول",
            },
            {
                "username": "student2",
                "email": "student2@example.com",
                "password": "testpass123",
                "first_name": "دانشجو",
                "last_name": "دوم",
            },
        ]

        for user_data in users_data:
            username = user_data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  - skipped existing user: {username}")
                continue

            if user_data.get("is_superuser"):
                User.objects.create_superuser(
                    username=username,
                    email=user_data["email"],
                    password=user_data["password"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                )
            else:
                User.objects.create_user(
                    username=username,
                    email=user_data["email"],
                    password=user_data["password"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                )

            self.stdout.write(self.style.SUCCESS(f"  + created user: {username}"))

    def load_fixture(self, app_label):
        self.stdout.write(f"Loading fixture for: {app_label}")
        try:
            call_command("loaddata", "initial_data", app_label=app_label, verbosity=1)
            self.stdout.write(self.style.SUCCESS(f"  ✓ {app_label} loaded"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ {app_label} failed: {e}"))