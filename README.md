# 📚 AI Learning Coach — MCP + Streamlit + Supabase + Groq

A full-stack AI-powered Learning Coach built using:

- **Supabase Postgres + pgvector**
- **Groq LLM (`llama3.1-8b-instant`)**
- **SentenceTransformers (`all-MiniLM-L6-v2`)**
- **FastMCP server**
- **Streamlit Dashboard**
- **Python RAG pipeline**

This project allows users to:

1. Upload documents (PDF/TXT/MD)
2. Extract + Embed content using SentenceTransformers
3. Store content + embeddings inside Supabase
4. Track weekly learning progress
5. Generate daily/weekly learning digests using Groq LLM
6. Expose all functionality through an MCP server (works with Claude Desktop)

---

# 🚀 Features

### ✅ Content Ingestion
- Upload PDF, text, or markdown files
- Extract text
- Generate embeddings with `all-MiniLM-L6-v2`
- Store text + embeddings in Supabase (`content` table)

### ✅ Vector Search (pgvector)
- Cosine similarity using `<=>` operator
- Top-K retrieval for learning digest generation

### ✅ Learning Progress Tracking
- Week-by-week progress stored in Supabase (`user_progress` table)

### ✅ Daily Digest Generation
- Uses RAG + Groq to produce 5-item insights
- Tailored to the learner’s weekly progress
- Stored in Supabase (`digests` table)

### ✅ MCP Server Integration
Exposes tools:
- `add_content_source`
- `list_content_sources`
- `fetch_sources`
- `update_progress`
- `generate_daily_digest`

### ✅ Streamlit Dashboard
- Upload documents
- Update weekly learning plan
- Generate learning digest visually
- View stored content in a clean tabbed UI

---

# 🏗️ Architecture Overview

```
User → Streamlit UI → Backend (Python)
                              ↓
                       SentenceTransformers (Embeddings)
                              ↓
                         Supabase (pgvector)
                              ↓
                          RAG Pipeline
                              ↓
                      Groq LLM (Digest Generation)
                              ↓
                      Supabase → Digests
                              ↓
                  Claude Desktop via MCP Tools
```

---

# 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| Backend | Python 3.11 |
| Vector Search | pgvector on Supabase |
| LLM | Groq `llama3.1-8b-instant` |
| Embeddings | SentenceTransformer (`all-MiniLM-L6-v2`) |
| UI | Streamlit |
| MCP Server | FastMCP |
| RSS Fetching | feedparser |
| File parsing | pdfplumber |

---

# 📦 Installation

### 1. Create virtual environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:6543/postgres
GROQ_API_KEY=your_groq_key
```

### 4. Initialize Supabase tables

Run this in the Supabase SQL Editor:

```sql
create extension if not exists vector;

create table if not exists sources (
  id serial primary key,
  url text not null,
  created_at timestamptz default now()
);

create table if not exists content (
  id serial primary key,
  title text,
  text text,
  url text,
  embedding vector(384),
  created_at timestamptz default now()
);

create table if not exists user_progress (
  id serial primary key,
  week int not null,
  topics text,
  created_at timestamptz default now()
);

create table if not exists digests (
  id serial primary key,
  week int,
  digest text,
  created_at timestamptz default now()
);
```

---

# ▶️ Running the Streamlit Dashboard

```bash
streamlit run dashboard.py
```

---

# 🔧 MCP Server Setup (Claude Desktop)

Add to:

**Windows**
```
%APPDATA%\Claude\claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "LearningCoach": {
      "command": "C:\\Path\\To\\python.exe",
      "args": [
        "D:\\Path\\To\\learning-coach-mcp\\src\\server.py"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:YOUR_PASSWORD@db.PROJECT_REF.supabase.co:6543/postgres",
        "GROQ_API_KEY": "your_groq_key"
      }
    }
  }
}
```

---

# 🧪 MCP Testing Prompts

```
Add this RSS source: https://hnrss.org/frontpage
```

```
Fetch content from all sources.
```

```
Update my progress to week 1 learning Python.
```

```
Generate my daily learning digest.
```

---

# 📐 Project Structure

```
learning-coach-mcp/
├── src/
│   ├── server.py
│   ├── ingestion/
│   ├── rag/
│   ├── utils/
│   └── ...
├── dashboard.py
├── requirements.txt
├── README.md
└── .env
```

---

# 🎯 Assignment Mapping

This project implements all requirements from the assignment document.

| Required | Implemented |
|---------|-------------|
| RAG using pgvector | ✔ |
| Document ingestion | ✔ |
| Semantic search | ✔ |
| Daily digest generation | ✔ |
| Learning progress tracking | ✔ |
| MCP tools | ✔ |
| Streamlit dashboard | ✔ |

---

# 🤝 Contributing

PRs and suggestions welcome!

---

# 📜 License

MIT License – Open Source & Fully Editable
