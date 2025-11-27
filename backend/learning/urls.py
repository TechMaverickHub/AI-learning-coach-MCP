"""
URLs for learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningProgressViewSet

router = DefaultRouter()
router.register(r'progress', LearningProgressViewSet, basename='learning-progress')

urlpatterns = [
    path('', include(router.urls)),
]

