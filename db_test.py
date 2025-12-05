import os
import psycopg2
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv
load_dotenv()

print("🔍 Testing Supabase DATABASE_URL...\n")

PASSWORD = os.getenv("PASSWORD")
DATABASE_URL=f"postgresql://postgres.ktxarfxljrttnuuwrwhx:{PASSWORD}@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

print(DATABASE_URL)


# DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ DATABASE_URL is NOT set in environment.")
    print("Set it before running:\n")
    print('   set DATABASE_URL="postgresql://postgres:password@db.projectref.supabase.co:5432/postgres"\n')
    exit(1)

print("📌 DATABASE_URL found.")
print(f"URL: {DATABASE_URL}\n")


def connect():
    """Try connecting to Supabase Postgres."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        print("✅ Successfully connected to Supabase Postgres!\n")
        return conn
    except Exception as e:
        print("❌ Failed to connect to Supabase Postgres.\n")
        print("Error:", e)
        exit(1)


# 2. Test DB connection
conn = connect()
cur = conn.cursor()

# 3. Check pgvector extension
print("🔍 Checking pgvector extension...")
try:
    cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
    row = cur.fetchone()
    if row:
        print("✅ pgvector extension is installed.\n")
    else:
        print("❌ pgvector extension is NOT installed.")
        print("Run this in Supabase SQL editor:\n  CREATE EXTENSION IF NOT EXISTS vector;\n")
except Exception as e:
    print("❌ Error checking pgvector:", e)

# 4. Check required tables
required_tables = ["sources", "content", "user_progress", "digests"]

print("🔍 Checking required tables...")
for table in required_tables:
    try:
        cur.execute(f"SELECT to_regclass('{table}');")
        result = cur.fetchone()
        if result["to_regclass"] is not None:
            print(f"✅ Table exists: {table}")
        else:
            print(f"❌ Missing table: {table}")
    except Exception as e:
        print(f"❌ Error checking table {table}: {e}")

print("\n🎉 Database test completed.\n")

cur.close()
conn.close()
