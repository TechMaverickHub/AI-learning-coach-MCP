"""
Views for digest app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Digest
from .serializers import DigestSerializer
from ..services.digest_service import DigestService
import logging

logger = logging.getLogger(__name__)


class DigestViewSet(viewsets.ModelViewSet):
    """ViewSet for Digest"""
    queryset = Digest.objects.all()
    serializer_class = DigestSerializer
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Manually generate digest"""
        try:
            digest_service = DigestService()
            digest_data = digest_service.generate_digest()
            
            digest = Digest.objects.create(
                content=digest_data['content'],
                ragas_score=digest_data.get('ragas_score')
            )
            
            serializer = self.get_serializer(digest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error generating digest: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest digest"""
        latest = self.queryset.first()
        if latest:
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        return Response(
            {'message': 'No digests found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get digest history"""
        digests = self.queryset[:10]  # Last 10 digests
        serializer = self.get_serializer(digests, many=True)
        return Response(serializer.data)

