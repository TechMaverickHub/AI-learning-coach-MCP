"""
URLs for RSS app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RSSFeedViewSet

router = DefaultRouter()
router.register(r'feeds', RSSFeedViewSet, basename='rss-feed')

urlpatterns = [
    path('', include(router.urls)),
]

