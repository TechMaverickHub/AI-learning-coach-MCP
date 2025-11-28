"""
Main API URLs.
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import rag_query
from .llm_tools import get_llm_tools, execute_llm_tool


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy'})


urlpatterns = [
    path('health/', health_check, name='health'),
    path('rag/query/', rag_query, name='rag-query'),
    # LLM Tools/Functions (Alternative to MCP)
    path('llm/tools/', get_llm_tools, name='llm-tools'),
    path('llm/tools/execute/', execute_llm_tool, name='llm-tool-execute'),
]

