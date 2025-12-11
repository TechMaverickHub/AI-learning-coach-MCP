import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment")

def _conn():
    print(DATABASE_URL)
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        print(e)
        raise e

def insert_source(url: str):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into sources (url) values (%s) returning id;", (url,))
            return cur.fetchone()["id"]

def list_sources():
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("select id, url from sources order by id;")
            return cur.fetchall()

def upsert_content(title: str, text: str, url: str, embedding: list):
    """
    Insert content row. embedding must be a python list of floats.
    We'll store as pgvector literal like '[0.1, 0.2, ...]'::vector
    """
    emb_text = "[" + ",".join(f"{float(x):.18f}" for x in embedding) + "]"
    sql = """
    insert into content (title, text, url, embedding)
    values (%s, %s, %s, %s::vector)
    returning id;
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (title, text, url, emb_text))
            return cur.fetchone()["id"]

def query_top_k_by_cosine(query_embedding: list, k: int = 5):
    """
    Uses pgvector cosine distance operator `<=>` (lower distance = more similar).
    Returns list of rows with id, title, text, url, distance.
    """
    emb_text = "[" + ",".join(f"{float(x):.18f}" for x in query_embedding) + "]"
    sql = f"""
    select id, title, text, url, embedding <=> %s::vector as distance
    from content
    where embedding is not null
    order by embedding <=> %s::vector
    limit %s;
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (emb_text, emb_text, k))
            return cur.fetchall()

def append_progress(week: int, topics: str):
    sql = "insert into user_progress (week, topics) values (%s, %s) returning id;"
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (week, topics))
            return cur.fetchone()["id"]

def get_latest_progress():
    sql = "select * from user_progress order by created_at desc limit 1;"
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchone()

def save_digest(week: int, digest_text: str):
    sql = "insert into digests (week, digest) values (%s, %s) returning id;"
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (week, digest_text))
            return cur.fetchone()["id"]


def get_all_content():
    """
    Return all content rows used to build the vectorstore.
    Each row dict must contain: id, title, text, url (optional), embedding (optional)
    """
    sql = "select id, title, text, url from content order by id;"
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            # cur is RealDictCursor so rows are dict-like
            return rows
