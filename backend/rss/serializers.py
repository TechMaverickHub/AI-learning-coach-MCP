"""
Serializers for RSS app.
"""
from rest_framework import serializers
from .models import RSSFeed, RSSArticle


class RSSArticleSerializer(serializers.ModelSerializer):
    """Serializer for RSSArticle model"""
    
    class Meta:
        model = RSSArticle
        fields = ['id', 'feed', 'title', 'url', 'published_at', 'indexed_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class RSSFeedSerializer(serializers.ModelSerializer):
    """Serializer for RSSFeed model"""
    articles = RSSArticleSerializer(many=True, read_only=True)
    
    class Meta:
        model = RSSFeed
        fields = ['id', 'feed_url', 'name', 'last_fetched', 'fetch_interval', 
                  'created_at', 'articles']
        read_only_fields = ['id', 'created_at', 'last_fetched']

