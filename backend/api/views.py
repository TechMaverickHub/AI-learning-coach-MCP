"""
API views for RAG queries.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.rag_service import RAGService
from services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def rag_query(request):
    """Query RAG system"""
    query = request.data.get('query')
    max_results = request.data.get('max_results', 5)
    
    if not query:
        return Response(
            {'error': 'Query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        embedding_service = EmbeddingService()
        rag_service = RAGService()
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        # Retrieve relevant chunks
        chunks = rag_service.retrieve(query_embedding, top_k=max_results)
        
        # Format results
        results = []
        for chunk in chunks:
            results.append({
                'content': chunk['content'],
                'source': chunk['metadata'].get('source', 'Unknown'),
                'relevance_score': 1 - chunk['distance']  # Convert distance to similarity
            })
        
        return Response({'results': results})
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

