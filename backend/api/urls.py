"""
Main API URLs.
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import rag_query


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy'})


urlpatterns = [
    path('health/', health_check, name='health'),
    path('rag/query/', rag_query, name='rag-query'),
]

