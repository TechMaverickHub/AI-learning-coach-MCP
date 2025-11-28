"""
LLM Tools/Functions definitions for OpenAI and other LLMs.
This replaces the need for Claude Desktop MCP.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_rss_feed",
            "description": "Fetch and index articles from an RSS feed URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "feed_url": {
                        "type": "string",
                        "description": "URL of the RSS feed to fetch"
                    },
                    "max_articles": {
                        "type": "integer",
                        "description": "Maximum number of articles to fetch (optional)",
                        "default": 50
                    }
                },
                "required": ["feed_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_learning_context",
            "description": "Query the learning context using RAG to get relevant content from uploaded materials",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query about learning content"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_learning_progress",
            "description": "Update learning progress for a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic name"
                    },
                    "progress": {
                        "type": "number",
                        "description": "Progress value between 0 and 1",
                        "minimum": 0,
                        "maximum": 1
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes about progress"
                    }
                },
                "required": ["topic", "progress"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_digest",
            "description": "Get the latest daily learning digest",
            "parameters": {
                "type": "object",
                "properties": {}
            },
            "required": []
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_digest",
            "description": "Generate a new daily learning digest",
            "parameters": {
                "type": "object",
                "properties": {}
            },
            "required": []
        }
    }
]


@api_view(['GET'])
def get_llm_tools(request):
    """
    Get LLM function/tool definitions.
    Compatible with OpenAI, Anthropic, and other LLM providers.
    """
    format_type = request.query_params.get('format', 'openai')
    
    # Return OpenAI format (can be used by any LLM that supports function calling)
    return Response({
        'tools': OPENAI_FUNCTIONS,
        'format': 'openai'
    })


@api_view(['POST'])
def execute_llm_tool(request):
    """
    Execute an LLM tool/function call.
    This endpoint is called by LLMs when they want to use a tool.
    """
    tool_name = request.data.get('name')
    arguments = request.data.get('arguments', {})
    
    if not tool_name:
        return Response(
            {'error': 'Tool name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if tool_name == 'fetch_rss_feed':
            return _execute_fetch_rss_feed(arguments)
        elif tool_name == 'query_learning_context':
            return _execute_query_learning_context(arguments)
        elif tool_name == 'update_learning_progress':
            return _execute_update_progress(arguments)
        elif tool_name == 'get_latest_digest':
            return _execute_get_latest_digest()
        elif tool_name == 'generate_digest':
            return _execute_generate_digest()
        else:
            return Response(
                {'error': f'Unknown tool: {tool_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _execute_fetch_rss_feed(arguments):
    """Execute fetch_rss_feed tool"""
    from rss.models import RSSFeed, RSSArticle
    from services.rss_service import RSSService
    from django.utils import timezone
    
    feed_url = arguments.get('feed_url')
    max_articles = arguments.get('max_articles', 50)
    
    # Get or create feed
    feed, created = RSSFeed.objects.get_or_create(feed_url=feed_url)
    
    # Fetch articles
    rss_service = RSSService()
    articles = rss_service.fetch_feed(feed_url, max_articles)
    
    # Store articles
    created_count = 0
    for article_data in articles:
        article, created = RSSArticle.objects.get_or_create(
            url=article_data['url'],
            defaults={
                'feed': feed,
                'title': article_data['title'],
                'published_at': article_data.get('published'),
                'content_hash': article_data.get('content_hash'),
            }
        )
        if created:
            created_count += 1
    
    feed.last_fetched = timezone.now()
    feed.save()
    
    return Response({
        'result': f'Successfully fetched {created_count} new articles from {feed_url}',
        'total_articles': len(articles),
        'new_articles': created_count
    })


def _execute_query_learning_context(arguments):
    """Execute query_learning_context tool"""
    from services.rag_service import RAGService
    from services.embedding_service import EmbeddingService
    
    query = arguments.get('query')
    max_results = arguments.get('max_results', 5)
    
    embedding_service = EmbeddingService()
    rag_service = RAGService()
    
    query_embedding = embedding_service.generate_embedding(query)
    chunks = rag_service.retrieve(query_embedding, top_k=max_results)
    
    results = []
    for chunk in chunks:
        results.append({
            'content': chunk['content'],
            'source': chunk['metadata'].get('source', 'Unknown'),
            'relevance_score': 1 - chunk['distance']
        })
    
    return Response({
        'result': 'Query executed successfully',
        'results': results
    })


def _execute_update_progress(arguments):
    """Execute update_learning_progress tool"""
    from learning.models import LearningProgress
    
    topic = arguments.get('topic')
    progress = arguments.get('progress')
    notes = arguments.get('notes', '')
    
    progress_obj, created = LearningProgress.objects.update_or_create(
        topic=topic,
        defaults={
            'progress': progress,
            'notes': notes
        }
    )
    
    return Response({
        'result': f'Successfully updated progress for {topic}: {progress * 100:.1f}%',
        'created': created
    })


def _execute_get_latest_digest():
    """Execute get_latest_digest tool"""
    from digest.models import Digest
    
    latest = Digest.objects.first()
    if latest:
        return Response({
            'result': 'Latest digest retrieved',
            'digest': {
                'id': str(latest.id),
                'generated_at': latest.generated_at.isoformat(),
                'content': latest.content,
                'ragas_score': latest.ragas_score
            }
        })
    else:
        return Response({
            'result': 'No digests available yet',
            'digest': None
        })


def _execute_generate_digest():
    """Execute generate_digest tool"""
    from services.digest_service import DigestService
    from digest.models import Digest
    
    digest_service = DigestService()
    digest_data = digest_service.generate_digest()
    
    digest = Digest.objects.create(
        content=digest_data['content'],
        ragas_score=digest_data.get('ragas_score')
    )
    
    return Response({
        'result': 'Digest generated successfully',
        'digest_id': str(digest.id),
        'generated_at': digest.generated_at.isoformat()
    })

