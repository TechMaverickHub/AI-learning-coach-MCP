"""
Digest generation service using Groq LLM (free and fast!).
"""
import os
from .rag_service import RAGService
from .embedding_service import EmbeddingService
from utils.prompts import DIGEST_PROMPT
import logging

logger = logging.getLogger(__name__)


class DigestService:
    """Service for generating daily learning digests"""
    
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'groq').lower()  # Using Groq (free LLM)
        self.use_mock = os.getenv('USE_MOCK_SERVICES', 'False').lower() == 'true'
        self.rag_service = RAGService()
        self.embedding_service = EmbeddingService()
        
        if self.use_mock:
            logger.info("Using mock digest service")
            self.client = None
            self.model = None
        else:
            # Default to Groq
            self._init_groq()
    
    def _init_groq(self):
        """Initialize Groq client (FREE alternative)"""
        try:
            from groq import Groq
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                logger.warning("GROQ_API_KEY not set. Using mock service.")
                self.use_mock = True
                self.client = None
                return
            self.client = Groq(api_key=api_key)
            self.model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
            self.provider = 'groq'
            logger.info(f"Initialized Groq (FREE) with model: {self.model}")
        except ImportError:
            logger.error("groq package not installed. Run: pip install groq")
            logger.warning("Falling back to mock service")
            self.use_mock = True
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            self.use_mock = True
            self.client = None
    
    def generate_digest(self) -> dict:
        """
        Generate daily learning digest.
        
        Returns:
            Dictionary with digest content and RAGAS score
        """
        try:
            # Retrieve relevant content using RAG
            # For now, use a generic query - in production, personalize based on progress
            query = "What should I learn today based on my learning materials?"
            query_embedding = self.embedding_service.generate_embedding(query)
            chunks = self.rag_service.retrieve(query_embedding)
            
            # Prepare context from retrieved chunks
            context = "\n\n".join([chunk['content'] for chunk in chunks])
            
            # Generate digest using LLM
            if self.use_mock:
                logger.warning("Using mock digest service. Set USE_MOCK_SERVICES=False and valid API key for real digests.")
                digest_content = self._generate_mock_digest()
            else:
                try:
                    # Groq uses OpenAI-compatible API format
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": DIGEST_PROMPT},
                            {"role": "user", "content": f"Context:\n{context}\n\nGenerate today's learning digest. Return a JSON object with 'today_focus', 'recommended_content' (array of objects with 'topic' and 'description'), and 'learning_tips' (array of strings)."}
                        ],
                        response_format=None  # Groq doesn't support structured output, but returns JSON in prompt
                    )
                    import json
                    content = response.choices[0].message.content
                    # Groq might return JSON without explicit format, so try to parse
                    if isinstance(content, str):
                        digest_content = json.loads(content)
                    else:
                        digest_content = content
                except Exception as e:
                    error_str = str(e)
                    if 'quota' in error_str.lower() or 'insufficient_quota' in error_str.lower() or '429' in error_str:
                        logger.error(f"{self.provider.upper()} API quota exceeded. Using mock digest.")
                        logger.error(f"Error details: {e}")
                        digest_content = self._generate_mock_digest()
                    else:
                        logger.error(f"Error generating digest with {self.provider}: {e}")
                        raise
            
            # TODO: Calculate RAGAS score
            ragas_score = None
            
            return {
                'content': digest_content,
                'ragas_score': ragas_score
            }
        except Exception as e:
            logger.error(f"Error generating digest: {e}")
            raise
    
    def _generate_mock_digest(self) -> dict:
        """Generate a mock digest for testing"""
        return {
            'today_focus': f'This is a mock digest. Set up {self.provider.upper()} API key to generate real personalized digests.',
            'recommended_content': [
                {
                    'topic': 'Sample Topic 1',
                    'description': f'This is a mock recommendation. Enable {self.provider.upper()} API for real personalized recommendations.'
                },
                {
                    'topic': 'Sample Topic 2',
                    'description': 'Another mock recommendation based on your learning materials.'
                }
            ],
            'learning_tips': [
                'Tip 1: This is a mock learning tip',
                f'Tip 2: Enable {self.provider.upper()} API for personalized tips based on your progress'
            ]
        }

