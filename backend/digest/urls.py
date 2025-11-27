"""
URLs for digest app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DigestViewSet

router = DefaultRouter()
router.register(r'', DigestViewSet, basename='digest')

urlpatterns = [
    path('', include(router.urls)),
]

