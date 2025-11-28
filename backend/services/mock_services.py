"""
Mock services for testing without API calls.
Use these when you want to test without making API requests.
"""
import logging
import random

logger = logging.getLogger(__name__)


class MockEmbeddingService:
    """Mock embedding service that returns fake embeddings"""
    
    def __init__(self):
        self.embedding_dim = 1536  # Same as text-embedding-3-small
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate a mock embedding vector.
        Uses a simple hash-based approach for consistency.
        """
        # Create a deterministic "embedding" based on text hash
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate a vector that's consistent for the same text
        embedding = [random.random() * 2 - 1 for _ in range(self.embedding_dim)]
        return embedding


class MockDigestService:
    """Mock digest service that returns fake digests"""
    
    def generate_digest(self) -> dict:
        """Generate a mock digest"""
        return {
            'content': {
                'today_focus': 'This is a mock digest. Set up Groq API key to generate real digests.',
                'recommended_content': [
                    {
                        'topic': 'Sample Topic 1',
                        'description': 'This is a mock recommendation. Enable Groq API for real recommendations.'
                    },
                    {
                        'topic': 'Sample Topic 2',
                        'description': 'Another mock recommendation.'
                    }
                ],
                'learning_tips': [
                    'Tip 1: This is a mock tip',
                    'Tip 2: Enable Groq API for personalized tips'
                ]
            },
            'ragas_score': None
        }


class MockRAGService:
    """Mock RAG service that returns fake results"""
    
    def retrieve(self, query_embedding: list, top_k: int = 5) -> list:
        """Return mock retrieval results"""
        return [
            {
                'content': 'This is a mock content chunk. Set up embeddings service for real RAG retrieval.',
                'metadata': {'source': 'mock_document.pdf'},
                'distance': 0.1
            },
            {
                'content': 'Another mock content chunk for testing purposes.',
                'metadata': {'source': 'mock_document.pdf'},
                'distance': 0.2
            }
        ][:top_k]

