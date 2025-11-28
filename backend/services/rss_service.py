"""
RSS feed fetching and parsing service.
"""
import os
import feedparser
import hashlib
import requests
from datetime import datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class RSSService:
    """Service for fetching and parsing RSS feeds"""
    
    def fetch_feed(self, feed_url: str, max_articles: int = None) -> list:
        """
        Fetch and parse RSS feed.
        
        Args:
            feed_url: URL of RSS feed
            max_articles: Maximum number of articles to return
            
        Returns:
            List of article dictionaries
        """
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing error: {feed.bozo_exception}")
            
            articles = []
            max_articles = max_articles or int(os.getenv('RSS_MAX_ARTICLES_PER_FEED', 50))
            
            for entry in feed.entries[:max_articles]:
                # Generate content hash for duplicate detection
                content = entry.get('summary', '') + entry.get('title', '')
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                articles.append({
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': published,
                    'content_hash': content_hash
                })
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            raise
    
    def fetch_all_feeds(self):
        """Fetch all RSS feeds (for scheduled task)"""
        from rss.models import RSSFeed, RSSArticle
        
        feeds = RSSFeed.objects.all()
        for feed in feeds:
            try:
                articles = self.fetch_feed(feed.feed_url)
                
                created_count = 0
                for article_data in articles:
                    article, created = RSSArticle.objects.get_or_create(
                        url=article_data['url'],
                        defaults={
                            'feed': feed,
                            'title': article_data['title'],
                            'published_at': article_data.get('published'),
                            'content_hash': article_data.get('content_hash'),
                        }
                    )
                    if created:
                        created_count += 1
                        # TODO: Index article content
                
                feed.last_fetched = timezone.now()
                feed.save()
                
                logger.info(f"Fetched {created_count} new articles from {feed.feed_url}")
            except Exception as e:
                logger.error(f"Error processing feed {feed.feed_url}: {e}")

