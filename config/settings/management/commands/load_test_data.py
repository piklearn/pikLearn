import os
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Load initial test data for settings app'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Loading settings test data...'))
        
        # بارگذاری فایل fixture
        fixture_path = os.path.join(
            settings.BASE_DIR, 
            'settings', 
            'fixtures', 
            'initial_data.json'
        )
        
        if os.path.exists(fixture_path):
            try:
                call_command('loaddata', fixture_path)
                self.stdout.write(
                    self.style.SUCCESS('Settings test data loaded successfully!')
                )
                
                # نمایش اطلاعات بارگذاری شده
                from settings.models import SiteSettings, NavbarOption
                
                settings_count = SiteSettings.objects.count()
                navbar_count = NavbarOption.objects.count()
                
                self.stdout.write(f'✅ SiteSettings: {settings_count} record')
                self.stdout.write(f'✅ NavbarOptions: {navbar_count} records')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error loading data: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.ERROR(f'Fixture file not found: {fixture_path}')
            )