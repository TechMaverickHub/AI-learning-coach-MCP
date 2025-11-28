"""
Views for RSS app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RSSFeed, RSSArticle
from .serializers import RSSFeedSerializer, RSSArticleSerializer
from services.rss_service import RSSService
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class RSSFeedViewSet(viewsets.ModelViewSet):
    """ViewSet for RSSFeed"""
    queryset = RSSFeed.objects.all()
    serializer_class = RSSFeedSerializer
    
    @action(detail=True, methods=['post'])
    def fetch(self, request, pk=None):
        """Manually fetch RSS feed"""
        feed = self.get_object()
        try:
            rss_service = RSSService()
            articles = rss_service.fetch_feed(feed.feed_url)
            
            # Create article records
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
            
            feed.last_fetched = timezone.now()
            feed.save()
            
            return Response({
                'message': f'Fetched {created_count} new articles',
                'total_articles': len(articles)
            })
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

