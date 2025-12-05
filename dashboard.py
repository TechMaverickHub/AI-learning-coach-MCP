import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pdfplumber
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
import tempfile

# -----------------------------
# Load Environment Variables
# -----------------------------
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# Database Connection
# -----------------------------
def db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# -----------------------------
# Insert Content Into Supabase
# -----------------------------
def insert_content(title, text, embedding, url="uploaded_document"):
    emb_vec = "[" + ",".join(f"{float(x):.6f}" for x in embedding) + "]"

    sql = """
    INSERT INTO content (title, text, url, embedding)
    VALUES (%s, %s, %s, %s::vector)
    RETURNING id;
    """

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (title, text, url, emb_vec))
            return cur.fetchone()["id"]

# -----------------------------
# Search Top-K Relevant Content
# -----------------------------
def search_similar(query, k=5):
    query_emb = embedder.encode(query).tolist()
    emb_vec = "[" + ",".join(f"{float(x):.6f}" for x in query_emb) + "]"

    sql = f"""
    SELECT id, title, text, embedding <=> %s::vector AS distance
    FROM content
    ORDER BY embedding <=> %s::vector
    LIMIT {k};
    """

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (emb_vec, emb_vec))
            return cur.fetchall()

# -----------------------------
# Generate Digest using Groq
# -----------------------------
def generate_digest_snippets(rows):
    snippets = []
    for r in rows:
        snippet = (r["text"] or "").replace("\n", " ")[:200]
        snippets.append(f"**{r['title']}** — {snippet}")
    return "\n".join(snippets)

def generate_digest(week, rows):
    system = {
        "role": "system",
        "content": (
            "You are an expert AI learning coach. Generate 5 short learning insights. "
            "Each insight should have a title, difficulty level, and 1–2 actionable bullets."
        )
    }
    user = {
        "role": "user",
        "content": f"Week {week} insights based on the following content:\n\n{generate_digest_snippets(rows)}"
    }

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[system, user]
    )
    return res.choices[0].message.content

# -----------------------------
# Streamlit UI Starts Here
# -----------------------------
st.set_page_config(page_title="AI Learning Coach Dashboard", layout="wide")
st.title("📚 AI Learning Coach — Streamlit Dashboard")

tabs = st.tabs(["Upload Document", "Update Progress", "Generate Digest", "View Stored Content"])

# -----------------------------
# TAB 1 — Upload Document
# -----------------------------
with tabs[0]:
    st.header("Upload Document")

    uploaded = st.file_uploader("Upload PDF or Text File", type=["pdf", "txt", "md"])
    if uploaded:
        st.success("File uploaded successfully!")

        if uploaded.type == "application/pdf":
            with pdfplumber.open(uploaded) as pdf:
                text = "\n".join([p.extract_text() or "" for p in pdf.pages])
        else:
            text = uploaded.read().decode("utf-8")

        st.subheader("Extracted Text Preview")
        st.write(text[:500] + "…")

        if st.button("Store in Supabase"):
            emb = embedder.encode(text).tolist()
            doc_id = insert_content(uploaded.name, text, emb)
            st.success(f"Document stored with ID: {doc_id}")

# -----------------------------
# TAB 2 — Update Progress
# -----------------------------
with tabs[1]:
    st.header("Update Learning Progress")

    week = st.number_input("Week Number", min_value=1, max_value=52, step=1)
    topics = st.text_area("Topics you're learning this week")

    if st.button("Save Progress"):
        sql = "INSERT INTO user_progress (week, topics) VALUES (%s, %s)"
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (week, topics))
                st.success("Progress updated successfully!")

# -----------------------------
# TAB 3 — Generate Digest
# -----------------------------
with tabs[2]:
    st.header("Generate Daily Digest")

    query = st.text_input("Query (e.g., 'Python basics', 'Machine Learning Week 2')")
    week_input = st.number_input("Which week is this digest for?", min_value=1, step=1)

    if st.button("Generate Digest"):
        rows = search_similar(query)
        if not rows:
            st.error("No content found!")
        else:
            digest = generate_digest(week_input, rows)

            sql = "INSERT INTO digests (week, digest) VALUES (%s, %s)"
            with db() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (week_input, digest))

            st.success("Digest generated and stored!")
            st.subheader("Your Personalized Digest")
            st.write(digest)

# -----------------------------
# TAB 4 — View Stored Content
# -----------------------------
with tabs[3]:
    st.header("Stored Content in Database")

    sql = "SELECT id, title, created_at FROM content ORDER BY id DESC LIMIT 20;"
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            data = cur.fetchall()

    st.write(data)
