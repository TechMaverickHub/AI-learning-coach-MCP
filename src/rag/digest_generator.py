from utils.db_supabase import query_top_k_by_cosine, get_latest_progress, save_digest
from utils.embedder import embed
from utils.groq_client import chat

TOP_K = 5  # fixed per your choice

def generate_digest():
    prog = get_latest_progress()
    week = prog["week"] if prog else 1

    # Create a query embedding for the current week context
    query_text = f"learning digest for week {week} topics"
    q_emb = embed(query_text)

    rows = query_top_k_by_cosine(q_emb, k=TOP_K)

    snippets = []
    for r in rows:
        title = r.get("title") or "Untitled"
        text = (r.get("text") or "").replace("\n"," ")
        snippet = text[:200]
        snippets.append(f"- **{title}**: {snippet}")

    system_msg = {
        "role":"system",
        "content":"You are an expert AI learning coach. Produce 5 short learning insights. Each insight should have a title, difficulty (Beginner/Intermediate/Advanced), and 1-2 actionable bullets."
    }
    user_msg = {
        "role":"user",
        "content": f"Week: {week}\nHere are relevant snippets:\n\n" + "\n\n".join(snippets) + f"\n\nCreate exactly {TOP_K} concise learning insights tailored to week {week}."
    }

    digest_text = chat([system_msg, user_msg])

    save_digest(week, digest_text)
    return digest_text
