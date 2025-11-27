"""
RAG (Retrieval Augmented Generation) service.
"""
import os
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG retrieval"""
    
    def __init__(self):
        vector_store_path = os.getenv('VECTOR_STORE_PATH', './data/vector_store')
        self.client = chromadb.PersistentClient(
            path=vector_store_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="learning_content",
            metadata={"hnsw:space": "cosine"}
        )
        self.top_k = int(os.getenv('RAG_TOP_K', 5))
    
    def add_to_index(self, content: str, metadata: dict, embedding: list):
        """
        Add content to vector store.
        
        Args:
            content: Text content
            metadata: Metadata dictionary
            embedding: Embedding vector
        """
        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[metadata.get('id', str(metadata))]
            )
        except Exception as e:
            logger.error(f"Error adding to index: {e}")
            raise
    
    def retrieve(self, query_embedding: list, top_k: int = None) -> list:
        """
        Retrieve relevant content from vector store.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            top_k = top_k or self.top_k
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            chunks = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    chunks.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return chunks
        except Exception as e:
            logger.error(f"Error retrieving from index: {e}")
            raise
    
    def retrieve_with_metadata(self, query_embedding: list, filters: dict, top_k: int = None) -> list:
        """
        Retrieve with metadata filtering.
        
        Args:
            query_embedding: Query embedding vector
            filters: Metadata filters
            top_k: Number of results to return
            
        Returns:
            List of relevant chunks
        """
        try:
            top_k = top_k or self.top_k
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters
            )
            
            chunks = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    chunks.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return chunks
        except Exception as e:
            logger.error(f"Error retrieving with filters: {e}")
            raise

