# =============================================================================
#  receiver.py  —  the local tool that catches data from the browser extension
# =============================================================================
#  Run this (via run_receiver.bat) and leave it running. As you browse
#  realestate.com.au with the extension installed, each page's data is sent
#  here. This FIRST version simply saves what it receives and tells you how
#  many listings it found — so we can confirm capture works and see the real
#  JSON before building storage/scoring on top of it.
#
#  It uses only Python's built-in tools (no extra installs).
# =============================================================================

import json
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import rea_parse
import scoring
import storage

PORT = 8765
CAPTURE_DIR = Path(__file__).parent / "output" / "captures"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def banner():
    print("=" * 70)
    print("  LIVELUXE — Local Capture Receiver")
    print("=" * 70)
    print(f"  Listening on http://localhost:{PORT}")
    print(f"  Saving captures to: {CAPTURE_DIR}")
    print("")
    print("  Leave this window OPEN. Now browse realestate.com.au with the")
    print("  extension installed. You'll see capture results appear below.")
    print("  Press Ctrl+C here to stop.")
    print("=" * 70)
    print("")


def handle_capture(payload):
    url = payload.get("url", "?")

    # Keep the latest raw page on disk (handy if the site structure changes).
    if payload.get("outerHTML"):
        (CAPTURE_DIR / "latest_page.html").write_text(
            payload["outerHTML"], encoding="utf-8")

    # Parse listings out of the captured page.
    listings, status = rea_parse.extract_listings_from_payload(payload)

    if status != "ok" or not listings:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {url[:70]}")
        print(f"      No listings found here ({status}).")
        print("      (This is normal on non-search pages like a single listing"
              " or the homepage.)")
        print("")
        return {"ok": True, "url": url, "listings_found": 0, "status": status,
                "new": 0, "updated": 0}

    # Score (fast: no location yet) and store each listing. Dedupe on id.
    new_count, upd_count = 0, 0
    for rec in listings:
        score = scoring.score_listing(rec, location=None)  # location added later
        result = storage.upsert_listing(rec, score)
        if result == "new":
            new_count += 1
        elif result == "updated":
            upd_count += 1

    tally = storage.counts()
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {url[:70]}")
    print(f"      listings on page : {len(listings)}")
    print(f"      NEW saved        : {new_count}")
    print(f"      updated (dedupe) : {upd_count}")
    print(f"      database total   : {tally['total']} listings "
          f"({tally['alive']} still alive after gates)")
    print(f"      -> run 'run_score.bat' to add location scores, then open the"
          f" dashboard.")
    print("")

    return {"ok": True, "url": url, "listings_found": len(listings),
            "new": new_count, "updated": upd_count, "db_total": tally["total"]}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def do_POST(self):
        if self.path != "/ingest":
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw)
            result = handle_capture(payload)
            body = json.dumps(result).encode()
            self.send_response(200)
        except Exception as e:
            print(f"  !! Problem handling a capture: {type(e).__name__}: {e}")
            body = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(500)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep the window clean; we print our own clear summaries


def main():
    banner()
    db_path = storage.init_db()
    print(f"  Database ready: {db_path}\n")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Receiver stopped. Bye.")


if __name__ == "__main__":
    main()
