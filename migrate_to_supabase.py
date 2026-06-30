# =============================================================================
#  migrate_to_supabase.py  —  copy your local SQLite listings into Supabase
# =============================================================================
#  One-time (or repeatable) migration: copies every listing from the local
#  listings.db file into the shared Supabase database, preserving everything
#  including your status / verdict / follow-up / notes. Existing rows in
#  Supabase are updated (matched on listing_id), not duplicated.
#
#  Requires .env to point at Supabase (run setup_db first).
# =============================================================================

import sqlite3
from pathlib import Path

import db
import storage

LOCAL = Path(__file__).parent / "listings.db"


def main():
    if not db.IS_POSTGRES:
        print("No Supabase configured (.env). Nothing to migrate into.")
        return
    if not LOCAL.exists():
        print("No local listings.db found — nothing to migrate.")
        return

    storage.init_db()  # ensure the table exists in Supabase

    src = sqlite3.connect(LOCAL)
    src.row_factory = sqlite3.Row
    rows = src.execute("SELECT * FROM listings").fetchall()
    src.close()

    if not rows:
        print("Local database is empty — nothing to migrate.")
        return

    cols = list(rows[0].keys())
    ph = db.PLACEHOLDER
    set_cols = [c for c in cols if c != "listing_id"]

    conn = db.connect()
    new = upd = 0
    try:
        cur = conn.cursor()
        for r in rows:
            lid = r["listing_id"]
            cur.execute(f"SELECT 1 FROM listings WHERE listing_id={ph}", (lid,))
            if cur.fetchone():
                sets = ", ".join(f"{c}={ph}" for c in set_cols)
                cur.execute(f"UPDATE listings SET {sets} WHERE listing_id={ph}",
                            [r[c] for c in set_cols] + [lid])
                upd += 1
            else:
                placeholders = ", ".join(ph for _ in cols)
                cur.execute(
                    f"INSERT INTO listings ({', '.join(cols)}) "
                    f"VALUES ({placeholders})", [r[c] for c in cols])
                new += 1
        conn.commit()
    finally:
        conn.close()

    total = storage.counts()
    print(f"Migration complete: {new} added, {upd} updated.")
    print(f"Supabase now holds {total['total']} listings "
          f"({total['alive']} alive after gates).")


if __name__ == "__main__":
    main()
