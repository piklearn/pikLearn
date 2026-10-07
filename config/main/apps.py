from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    
    def ready(self):
            from django.contrib import admin
    
            original_get_app_list = admin.AdminSite.get_app_list
    
            def get_app_list(self, request, app_label=None):
                app_list = original_get_app_list(self, request, app_label)
    
                # عدد کمتر = بالاتر
                ordering = {
                    "blog": 1,
                    "courses": 2,
                }
                app_list.sort(key=lambda app: ordering.get(app["app_label"], 99))
                return app_list
    
            admin.AdminSite.get_app_list = get_app_list