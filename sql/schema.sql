-- Enable pgvector extension
create extension if not exists vector;

-- Sources table
create table if not exists sources (
  id serial primary key,
  url text not null,
  created_at timestamptz default now()
);

-- Content table (embeddings stored inline with vector(384))
create table if not exists content (
  id serial primary key,
  title text,
  text text,
  url text,
  embedding vector(384),
  created_at timestamptz default now()
);

-- optional index for approximate search (HNSW). You can create this later.
-- CREATE INDEX if not exists content_embedding_idx ON content USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Progress table (single-user, append-only)
create table if not exists user_progress (
  id serial primary key,
  week int not null,
  topics text,
  created_at timestamptz default now()
);

-- Digests table
create table if not exists digests (
  id serial primary key,
  week int,
  digest text,
  created_at timestamptz default now()
);
