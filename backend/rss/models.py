"""
RSS feed and article models.
"""
import uuid
from django.db import models


class RSSFeed(models.Model):
    """Model for RSS feeds"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_url = models.URLField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    fetch_interval = models.IntegerField(default=360)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rss_rssfeed'
        indexes = [
            models.Index(fields=['feed_url']),
        ]
    
    def __str__(self):
        return self.name or self.feed_url


class RSSArticle(models.Model):
    """Model for RSS articles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE, related_name='articles')
    title = models.TextField()
    url = models.URLField(unique=True)
    published_at = models.DateTimeField(null=True, blank=True)
    content_hash = models.CharField(max_length=64, null=True, blank=True)  # SHA256 for duplicate detection
    indexed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rss_rssarticle'
        indexes = [
            models.Index(fields=['feed']),
            models.Index(fields=['url']),
            models.Index(fields=['content_hash']),
        ]
    
    def __str__(self):
        return self.title

