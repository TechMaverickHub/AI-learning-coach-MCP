"""
URLs for content app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentSourceViewSet

router = DefaultRouter()
router.register(r'', ContentSourceViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]

