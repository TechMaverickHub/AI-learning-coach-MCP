"""
Tests for API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock


class HealthCheckTest(TestCase):
    """Tests for health check endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_health_check(self):
        """Test health check endpoint returns healthy status"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')


class RAGQueryTest(TestCase):
    """Tests for RAG query endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_rag_query_missing_query(self):
        """Test RAG query without query parameter"""
        response = self.client.post('/api/rag/query/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_rag_query_empty_query(self):
        """Test RAG query with empty query string"""
        response = self.client.post('/api/rag/query/', {'query': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.EmbeddingService')
    @patch('api.views.RAGService')
    def test_rag_query_success(self, mock_rag_service, mock_embedding_service):
        """Test successful RAG query"""
        # Mock embedding service
        mock_embedding_instance = Mock()
        mock_embedding_instance.generate_embedding.return_value = [0.1] * 1536
        mock_embedding_service.return_value = mock_embedding_instance
        
        # Mock RAG service
        mock_rag_instance = Mock()
        mock_rag_instance.retrieve.return_value = [
            {
                'content': 'Test content chunk',
                'metadata': {'source': 'test.pdf'},
                'distance': 0.1
            }
        ]
        mock_rag_service.return_value = mock_rag_instance
        
        response = self.client.post('/api/rag/query/', {
            'query': 'test query',
            'max_results': 5
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Test content chunk')
    
    @patch('api.views.EmbeddingService')
    def test_rag_query_service_error(self, mock_embedding_service):
        """Test RAG query with service error"""
        mock_embedding_instance = Mock()
        mock_embedding_instance.generate_embedding.side_effect = Exception("Service error")
        mock_embedding_service.return_value = mock_embedding_instance
        
        response = self.client.post('/api/rag/query/', {
            'query': 'test query',
            'max_results': 5
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class LLMToolsTest(TestCase):
    """Tests for LLM tools endpoints"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_get_llm_tools(self):
        """Test getting available LLM tools"""
        response = self.client.get('/api/llm/tools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tools', response.data)
        self.assertIsInstance(response.data['tools'], list)
    
    def test_execute_llm_tool_missing_parameters(self):
        """Test executing LLM tool without required parameters"""
        response = self.client.post('/api/llm/tools/execute/', {})
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])

