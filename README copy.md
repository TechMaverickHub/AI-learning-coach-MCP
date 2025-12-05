# Learning Coach MCP — Supabase + pgvector (single-user, 5-item digest)

## Overview
Single-user FastMCP server that:
- Stores content & embeddings in Supabase Postgres with pgvector (embedding column inside `content` table)
- Uses SentenceTransformer `all-MiniLM-L6-v2` for embeddings
- Uses Groq LLM (llama3-8b-8192) for digest generation
- Always returns exactly 5 digest items

This implements the assignment's required tables and RAG flow. See the original assignment PDF for details. :contentReference[oaicite:1]{index=1}

## Setup

1. Create a Supabase project and enable pgvector (create extension `vector`).
2. Run `sql/schema.sql` in the Supabase SQL editor.
3. Create a `.env` file from `.env.sample` and fill:
   - `DATABASE_URL` with the Supabase **service-role** connection string or Direct DB URL.
   - `GROQ_API_KEY`
4. Install Python deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
