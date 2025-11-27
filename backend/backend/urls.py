"""
URL configuration for AI Learning Coach backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/content/', include('content.urls')),
    path('api/rss/', include('rss.urls')),
    path('api/digest/', include('digest.urls')),
    path('api/learning/', include('learning.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

