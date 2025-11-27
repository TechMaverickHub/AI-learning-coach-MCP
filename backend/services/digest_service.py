"""
Digest generation service.
"""
import os
from openai import OpenAI
from .rag_service import RAGService
from .embedding_service import EmbeddingService
from ..utils.prompts import DIGEST_PROMPT
import logging

logger = logging.getLogger(__name__)


class DigestService:
    """Service for generating daily learning digests"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"
        self.rag_service = RAGService()
        self.embedding_service = EmbeddingService()
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DIGEST_PROMPT},
                    {"role": "user", "content": f"Context:\n{context}\n\nGenerate today's learning digest."}
                ],
                response_format={"type": "json_object"}
            )
            
            import json
            digest_content = json.loads(response.choices[0].message.content)
            
            # TODO: Calculate RAGAS score
            ragas_score = None
            
            return {
                'content': digest_content,
                'ragas_score': ragas_score
            }
        except Exception as e:
            logger.error(f"Error generating digest: {e}")
            raise

