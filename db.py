# =============================================================================
#  db.py  —  database connection layer (shared Supabase, or local SQLite)
# =============================================================================
#  If a Supabase/Postgres connection string is configured, the whole tool uses
#  that ONE shared database (so you and a coworker see the same listings).
#  If not, it falls back to a local SQLite file — so the tool still works solo
#  with zero setup.
#
#  Configure Supabase by putting your connection string in a local `.env` file
#  (copy `.env.example`):
#
#      SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres
#
#  That file is git-ignored — your password never goes into the repo.
# =============================================================================

import os
from pathlib import Path

_ROOT = Path(__file__).parent
SQLITE_FILE = _ROOT / "listings.db"


def _load_dotenv():
    """Load simple KEY=VALUE lines from a local .env into the environment."""
    env_path = _ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)


_load_dotenv()

SUPABASE_DB_URL = (os.environ.get("SUPABASE_DB_URL")
                   or os.environ.get("DATABASE_URL") or "").strip()
IS_POSTGRES = bool(SUPABASE_DB_URL)

# Query placeholder differs between the two engines.
PLACEHOLDER = "%s" if IS_POSTGRES else "?"


def backend_name():
    return "Supabase (Postgres)" if IS_POSTGRES else "local SQLite"


if IS_POSTGRES:
    import ssl
    from urllib.parse import urlparse, unquote
    import pg8000.dbapi

    def connect():
        u = urlparse(SUPABASE_DB_URL)
        # Encrypt the connection (TLS) but skip CA-chain verification — this is
        # the standard "sslmode=require" behaviour for Supabase's pooler, whose
        # certificate isn't in Python's default trust store.
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return pg8000.dbapi.connect(
            user=unquote(u.username or "postgres"),
            password=unquote(u.password or ""),
            host=u.hostname,
            port=u.port or 5432,
            database=(u.path or "/postgres").lstrip("/") or "postgres",
            ssl_context=ctx,
            timeout=20,
        )
else:
    import sqlite3

    def connect():
        c = sqlite3.connect(SQLITE_FILE)
        c.row_factory = sqlite3.Row
        return c


def rows_to_dicts(cursor):
    """
    Return all rows from a cursor as a list of plain dicts (both engines).
    Column names are lowercased so SQLite (case-preserving) and Postgres
    (case-folding) behave identically — e.g. both give 'score_a'.
    """
    cols = [d[0].lower() for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def query(sql, params=()):
    """Run a SELECT and return list of dict rows."""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return rows_to_dicts(cur)
    finally:
        conn.close()


def execute(sql, params=()):
    """Run a write statement and commit."""
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
