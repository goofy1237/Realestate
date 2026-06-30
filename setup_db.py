# =============================================================================
#  setup_db.py  —  save your Supabase connection string and test it
# =============================================================================
#  Paste your Supabase connection string here; it gets written to a private
#  .env file (git-ignored) and the connection is tested. Your password stays
#  on this computer.
# =============================================================================

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ENV = ROOT / ".env"

print("=" * 64)
print("  LuxeBot — Supabase setup")
print("=" * 64)
print("Paste your Supabase connection string below.")
print("In Supabase: Connect (top bar)  ->  'Session pooler'  ->  copy the URI.")
print("It looks like:")
print("  postgresql://postgres.xxxx:YOURPASSWORD@aws-0-...pooler.supabase.com:5432/postgres")
print()
print("(Tip: replace [YOUR-PASSWORD] in it with your real database password.)")
print()

url = input("Connection string: ").strip().strip('"').strip("'")

if not (url.startswith("postgres://") or url.startswith("postgresql://")):
    print("\nThat doesn't look like a connection string (it should start with")
    print("'postgresql://'). Nothing was saved. Run setup again.")
    sys.exit(1)

if "[YOUR-PASSWORD]" in url or "YOURPASSWORD" in url:
    print("\nIt still contains a placeholder password. Replace it with your real")
    print("database password, then run setup again.")
    sys.exit(1)

# Write/replace the SUPABASE_DB_URL line, preserving any other lines in .env.
lines = []
if ENV.exists():
    lines = [ln for ln in ENV.read_text(encoding="utf-8").splitlines()
             if not ln.strip().startswith("SUPABASE_DB_URL=")]
lines.append(f"SUPABASE_DB_URL={url}")
ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved to {ENV.name} (private / git-ignored).")

print("\nTesting the connection...\n")
subprocess.call([sys.executable, str(ROOT / "db_check.py")])
