"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from pages import views as page_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('main.urls'), name='main'),
    path('', include('main.urls'), name='main'),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses'),),
    path('accounts/', include(('users.urls', 'accounts'), namespace='accounts'),),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog'),),
    
    path('<slug:slug>/', page_views.page_detail, name='page_detail'),

] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
