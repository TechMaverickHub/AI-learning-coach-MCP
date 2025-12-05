from fastmcp import FastMCP
from ingestion.content_fetcher import add_source, fetch_and_store, list_all_sources
from rag.digest_generator import generate_digest
from utils.db_supabase import append_progress

mcp = FastMCP("learning-coach-supabase-singleuser")

@mcp.tool()
def add_content_source(url: str):
    return add_source(url)

@mcp.tool()
def list_content_sources():
    return list_all_sources()

@mcp.tool()
def fetch_sources():
    return fetch_and_store()

@mcp.tool()
def update_progress(week: int, topics: str):
    return {"status":"ok", "id": append_progress(week, topics)}

@mcp.tool()
def generate_daily_digest():
    return generate_digest()

if __name__ == "__main__":
    mcp.run()
