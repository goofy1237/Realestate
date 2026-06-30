# =============================================================================
#  db_check.py  —  test your database connection (Supabase or local SQLite)
# =============================================================================
#  Run this (run_db_test.bat) after setting up your .env to confirm the tool
#  can reach your shared Supabase database.
# =============================================================================

import db
import storage

print("=" * 60)
print("  LuxeBot — database check")
print("=" * 60)
print(f"  Backend: {db.backend_name()}")

if not db.IS_POSTGRES:
    print("\n  No Supabase configured — using a LOCAL SQLite file.")
    print("  To share a database with a coworker, copy .env.example to .env")
    print("  and paste your Supabase connection string into it.")

try:
    print("\n  Connecting and ensuring the table exists...")
    storage.init_db()
    c = storage.counts()
    print("  SUCCESS — connected and table is ready.")
    print(f"  Listings currently in this database: {c['total']} "
          f"({c['alive']} alive after gates)")
    if db.IS_POSTGRES:
        print("\n  You and your coworker will now share this same data.")
except Exception as e:
    print("\n  CONNECTION FAILED:")
    print(f"    {type(e).__name__}: {e}")
    print("\n  Checklist:")
    print("    - Is SUPABASE_DB_URL in your .env correct?")
    print("    - Use the 'Session pooler' connection string (port 5432).")
    print("      Avoid 'Transaction pooler' (port 6543), and the plain 'Direct'")
    print("      connection (IPv6-only, often fails on home/office networks).")
    print("    - Did you replace [YOUR-PASSWORD] with your real password?")
print("=" * 60)
