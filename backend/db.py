"""Local SQLite storage for the MVP. Swap for Supabase/PostgreSQL later (see docs/schema.sql)."""
import sqlite3, os, uuid, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")

def conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init():
    with conn() as c:
        c.executescript("""
        create table if not exists farmers(id text primary key, name text, location text, language text, farm_size real, created_at text);
        create table if not exists crops(id text primary key, farmer_id text, crop_name text, sowing_date text, crop_stage text);
        create table if not exists predictions(id text primary key, farmer_id text, crop text, label text,
            confidence real, risk text, reasons text, recommendation text, demo integer, prediction_date text);
        """)

def new_id(): return str(uuid.uuid4())
def now(): return datetime.datetime.utcnow().isoformat()
