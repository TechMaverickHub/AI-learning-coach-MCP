import feedparser
from rag.lc_utils import embed_text
from utils.embedder import embed
from utils.db_supabase import insert_source, list_sources, upsert_content

def add_source(url: str):
    return {"status": "ok", "id": insert_source(url)}

def list_all_sources():
    return list_sources()

def fetch_and_store():
    sources = list_sources()
    total = 0
    for s in sources:
        url = s["url"]
        feed = feedparser.parse(url)
        for entry in feed.entries:
            text = entry.get("summary") or entry.get("content", [{"value": ""}])[0].get("value","") or entry.get("title","")
            title = entry.get("title") or text[:100]
            link = entry.get("link")
            embedding = embed_text(text)
            try:
                upsert_content(title, text, link, embedding)
                total += 1
            except Exception as e:
                # duplicate or error -> skip
                continue
    return {"status":"ok", "fetched": total}
