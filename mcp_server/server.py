"""
Simple standalone MCP server that can run as HTTP server or stdio server.
"""
import asyncio
import os
import sys
from mcp import Server, types
from mcp.server.stdio import stdio_server
import httpx
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API base URL
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')

# Create MCP server
app = Server("ai-learning-coach")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="fetch_rss_feed",
            description="Fetch and index articles from an RSS feed URL",
            inputSchema={
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
        ),
        types.Tool(
            name="query_learning_context",
            description="Query the learning context using RAG to get relevant content",
            inputSchema={
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
        ),
        types.Tool(
            name="update_learning_progress",
            description="Update learning progress for a topic",
            inputSchema={
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
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "fetch_rss_feed":
            return await fetch_rss_feed(arguments)
        elif name == "query_learning_context":
            return await query_learning_context(arguments)
        elif name == "update_learning_progress":
            return await update_learning_progress(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def fetch_rss_feed(arguments: dict) -> list[types.TextContent]:
    """Fetch RSS feed"""
    feed_url = arguments.get("feed_url")
    max_articles = arguments.get("max_articles", 50)
    
    async with httpx.AsyncClient() as client:
        # First, add the feed if it doesn't exist
        feed_data = {"feed_url": feed_url}
        feed_response = await client.post(
            f"{API_BASE_URL}/rss/feeds/",
            json=feed_data
        )
        
        if feed_response.status_code == 201:
            feed_id = feed_response.json()["id"]
        elif feed_response.status_code == 400:
            # Feed might already exist, try to fetch it
            feeds_response = await client.get(f"{API_BASE_URL}/rss/feeds/")
            feeds = feeds_response.json()
            feed_id = next((f["id"] for f in feeds if f["feed_url"] == feed_url), None)
        else:
            raise Exception(f"Failed to add feed: {feed_response.text}")
        
        # Fetch the feed
        fetch_response = await client.post(
            f"{API_BASE_URL}/rss/feeds/{feed_id}/fetch/"
        )
        
        if fetch_response.status_code == 200:
            result = fetch_response.json()
            return [types.TextContent(
                type="text",
                text=f"Successfully fetched {result.get('total_articles', 0)} articles from {feed_url}"
            )]
        else:
            raise Exception(f"Failed to fetch feed: {fetch_response.text}")


async def query_learning_context(arguments: dict) -> list[types.TextContent]:
    """Query learning context"""
    query = arguments.get("query")
    max_results = arguments.get("max_results", 5)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/rag/query/",
            json={"query": query, "max_results": max_results}
        )
        
        if response.status_code == 200:
            results = response.json()
            content = "Relevant learning content:\n\n"
            for i, result in enumerate(results.get("results", []), 1):
                content += f"{i}. {result.get('content', '')}\n"
                content += f"   Source: {result.get('source', 'Unknown')}\n"
                content += f"   Relevance: {result.get('relevance_score', 0):.2f}\n\n"
            return [types.TextContent(type="text", text=content)]
        else:
            raise Exception(f"Failed to query context: {response.text}")


async def update_learning_progress(arguments: dict) -> list[types.TextContent]:
    """Update learning progress"""
    topic = arguments.get("topic")
    progress = arguments.get("progress")
    notes = arguments.get("notes", "")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/learning/progress/",
            json={
                "topic": topic,
                "progress": progress,
                "notes": notes
            }
        )
        
        if response.status_code == 201:
            return [types.TextContent(
                type="text",
                text=f"Successfully updated progress for {topic}: {progress * 100:.1f}%"
            )]
        else:
            raise Exception(f"Failed to update progress: {response.text}")


async def main():
    """Run MCP server in stdio mode"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


