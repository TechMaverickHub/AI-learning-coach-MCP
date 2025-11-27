"""
Views for content app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ContentSource
from .serializers import ContentSourceSerializer
from ..services.pdf_processor import PDFProcessor
from ..services.embedding_service import EmbeddingService
from ..utils.chunking import chunk_text
import logging

logger = logging.getLogger(__name__)


class ContentSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for ContentSource"""
    queryset = ContentSource.objects.all()
    serializer_class = ContentSourceSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle file upload and indexing"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = serializer.save()
        
        # Process file if uploaded
        if instance.file:
            try:
                # Extract text from PDF
                pdf_processor = PDFProcessor()
                text = pdf_processor.extract_text(instance.file.path)
                
                # Chunk text
                chunks = chunk_text(text)
                instance.chunks_count = len(chunks)
                
                # Generate embeddings and index
                embedding_service = EmbeddingService()
                for i, chunk in enumerate(chunks):
                    embedding = embedding_service.generate_embedding(chunk)
                    # TODO: Store in vector store with metadata
                
                instance.status = 'indexed'
                instance.save()
                
                logger.info(f"Indexed content {instance.id} with {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                instance.status = 'error'
                instance.save()
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

