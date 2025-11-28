"""
Embedding generation service using sentence-transformers (free, local).
No API calls needed!
"""
import os
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""
    
    def __init__(self):
        self.use_mock = os.getenv('USE_MOCK_SERVICES', 'False').lower() == 'true'
        self.model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.client = None
        
        if not self.use_mock:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading sentence-transformers model: {self.model_name}")
                self.client = SentenceTransformer(self.model_name)
                logger.info("Initialized sentence-transformers embeddings (free, local)")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                logger.warning("Falling back to mock embeddings")
                self.use_mock = True
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers: {e}")
                logger.warning("Falling back to mock embeddings")
                self.use_mock = True
    
    def generate_embedding(self, text: str) -> list:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list
        """
        if self.use_mock:
            logger.warning("Using mock embedding service. Install sentence-transformers for real embeddings.")
            return self._generate_mock_embedding(text)
        
        try:
            embedding = self.client.encode(text, convert_to_numpy=False)
            # Convert to list if needed
            if hasattr(embedding, 'tolist'):
                return embedding.tolist()
            return list(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            logger.warning("Falling back to mock embedding")
            return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> list:
        """Generate a mock embedding for testing"""
        import hashlib
        import random
        
        # Create deterministic embedding based on text hash
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate 384-dimensional vector (same as all-MiniLM-L6-v2)
        embedding = [random.random() * 2 - 1 for _ in range(384)]
        return embedding

