# src/rag/lc_utils.py
"""
LangChain utilities for embeddings and vector search.

This module:
- Uses HuggingFaceEmbeddings (SentenceTransformers all-MiniLM-L6-v2) via LangChain.
- Builds a local FAISS index from the content rows pulled from the DB.
- Provides a simple retriever interface that returns top-k Document objects.

Notes:
- This example uses FAISS for simplicity and local testing.
- If you prefer server-side search using pgvector (Supabase), see the commented block
  below showing how to switch to PGVector via LangChain.
"""

from typing import List, Dict, Any
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS
import numpy as np

# Initialize huggingface embedding model (wraps sentence-transformers)
# This uses model "sentence-transformers/all-MiniLM-L6-v2" (dim = 384)
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Create the embeddings object once (reused across calls)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

def embed_text(text: str):
    """
    Return embedding vector (list[float]) for a given text using LangChain embeddings wrapper.
    Replaces the old `embed()` function.
    """
    vec = embeddings.embed_query(text)
    # HuggingFaceEmbeddings returns a list[float] or np.ndarray-like; ensure Python list
    if isinstance(vec, np.ndarray):
        vec = vec.tolist()
    return vec

def build_faiss_retriever_from_rows(rows: List[Dict[str, Any]], k: int = 5):
    """
    Build a FAISS vectorstore from DB rows and return a retriever.
    rows: list of dicts with keys: 'id', 'title', 'text', optionally 'url'
    This function recreates the FAISS index in-memory on each call; for production,
    persist the FAISS index to disk or use PGVector for server-side retrieval.

    Returns:
        retriever: a LangChain retriever with .get_relevant_documents(query) or .similarity_search_by_vector(...)
    """
    # Convert DB rows to LangChain Document objects (text + metadata)
    docs = []
    for r in rows:
        metadata = {"id": r.get("id"), "title": r.get("title"), "url": r.get("url")}
        # Use the 'text' field as the document text
        docs.append(Document(page_content=(r.get("text") or ""), metadata=metadata))

    # If there are no docs, return None
    if not docs:
        return None

    # Create a FAISS index from documents using the same embeddings object
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)

    # Build a retriever that returns top k docs
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})
    return retriever

# -------------------------
# Optional: PGVector (Supabase) usage notes
# -------------------------
# If you'd prefer to use PGVector (pgvector) in Supabase via LangChain:
#
# from langchain.vectorstores import PGVector
# pg_vector_store = PGVector.from_existing_index(
#     embedding=embeddings,
#     table_name="content",
#     connection_string=DATABASE_URL,  # e.g., os.getenv("DATABASE_URL")
#     # The column storing vectors in `content` should be named `embedding` and be of type vector(384)
# )
# retriever = pg_vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
#
# NOTE: Using PGVector requires the content table to exist with a vector column and proper access.
# See LangChain docs for PGVector integration details.
