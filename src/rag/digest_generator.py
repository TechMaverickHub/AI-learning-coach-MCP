from typing import List, Dict, Any
from langchain.schema import Document
from langchain.llms.base import LLM
import os

# Local imports (your existing DB and groq client)
from utils.db_supabase import get_latest_progress, save_digest, get_all_content  # get_all_content to be added to db_supabase
from utils import groq_client  # existing module that has chat(messages)
from .lc_utils import embed_text, build_faiss_retriever_from_rows

TOP_K = 5  # fixed per assignment requirement

class GroqLangChainLLM(LLM):
    """
    Minimal LangChain LLM wrapper that delegates to groq_client.chat(messages).

    LangChain expects _call and _identifying_params to be defined.
    We keep it lightweight: prompts will be assembled inside digest_generator
    (we preserve the original system/user message structure).
    """
    @property
    def _identifying_params(self):
        return {"model": "groq_llm_wrapper"}

    @property
    def _llm_type(self):
        return "groq"

    def _call(self, prompt: str, stop: List[str] = None) -> str:
        """
        Accepts a single prompt string (we will pass concatenated messages).
        To stay faithful to the original, we will call groq_client.chat with
        structured messages where possible.
        """
        # Micro-protocol: we pass the single prompt string as a user message to groq_client
        # If you want structured messages (system/user) pass them to groq_client.chat directly.
        return groq_client.chat([{"role": "user", "content": prompt}])

# instantiate the LLM wrapper (no API keys required here; groq_client uses env)
llm = GroqLangChainLLM()

def generate_digest() -> str:
    """
    Generate a digest for the latest progress week using LangChain for embeddings + retrieval.
    Preserves output structure: exactly TOP_K insights, saved to digests table.
    """
    # 1) Get latest progress
    prog = get_latest_progress()
    week = prog["week"] if prog else 1

    # 2) Fetch all content rows from DB
    # NOTE: get_all_content() should return rows with keys: id, title, text, url, embedding(optional)
    # If you do not have get_all_content(), add it to utils/db_supabase.py (see helper below).
    rows = get_all_content()

    # 3) Build retriever (FAISS-based in-memory here)
    retriever = build_faiss_retriever_from_rows(rows, k=TOP_K)

    # If no content, return meaningful message
    if retriever is None:
        fallback_text = f"No content found to generate digest for week {week}."
        # Save an empty digest entry (optionally)
        save_digest(week, fallback_text)
        return fallback_text

    # 4) Build the query (same logic as before)
    query_text = f"learning digest for week {week} topics"
    # Optionally create embedding (not required for retriever similarity_search)
    # q_emb = embed_text(query_text)

    # 5) Retrieve top-k documents via LangChain retriever
    # Use retriever.get_relevant_documents(query_text) to get Documents
    docs: List[Document] = retriever.get_relevant_documents(query_text)

    # 6) Create snippets maintaining previous formatting
    snippets = []
    for d in docs[:TOP_K]:
        title = d.metadata.get("title") if d.metadata and d.metadata.get("title") else "Untitled"
        snippet_text = (d.page_content or "")[:200].replace("\n", " ")
        snippets.append(f"- **{title}**: {snippet_text}...")

    # 7) Assemble messages preserving original system/user prompt structure
    system_message = {
        "role": "system",
        "content": "You are an AI learning coach. Generate 5 short learning insights."
    }

    user_message = {
        "role": "user",
        "content": (
            "Here are relevant snippets:\n\n"
            + "\n\n".join(snippets)
            + f"\n\nCreate exactly {TOP_K} concise learning insights tailored to week {week}."
        )
    }

    # 8) Call Groq via groq_client.chat directly (preserve structured messages)
    digest_text = groq_client.chat([system_message, user_message])

    # 9) Save digest to DB (preserve existing DB function)
    save_digest(week, digest_text)

    return digest_text
