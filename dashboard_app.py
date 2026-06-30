# =============================================================================
#  dashboard_app.py  —  the dashboard as a DESKTOP APP window
# =============================================================================
#  Runs the dashboard server quietly in the background and opens it in a
#  standalone app window (no browser tabs or address bar, its own taskbar
#  icon) using your installed Chrome or Edge in "app mode". Closing the app
#  window stops the dashboard. No fragile dependencies.
# =============================================================================

import os
import subprocess
import threading
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

import dashboard
import storage

APP_PROFILE = Path(__file__).parent / ".dashboard_app_profile"


def find_browser():
    """Return the path to Chrome or Edge, whichever is installed."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def main():
    storage.init_db()

    # Start the dashboard web server in the background (daemon = dies with us).
    server = ThreadingHTTPServer(("127.0.0.1", dashboard.PORT), dashboard.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://localhost:{dashboard.PORT}"

    print("=" * 60)
    print("  LIVELUXE — Dashboard (app window)")
    print("=" * 60)
    print(f"  Running at {url}")

    browser = find_browser()
    if browser:
        print("  Opening the app window. Close it to stop the dashboard.")
        print("=" * 60)
        # --app gives a chromeless standalone window; a dedicated profile
        # keeps it separate from your normal browsing.
        proc = subprocess.Popen([
            browser,
            f"--app={url}",
            f"--user-data-dir={APP_PROFILE}",
            "--window-size=1200,900",
            "--no-first-run",
            "--no-default-browser-check",
        ])
        proc.wait()                      # block until the app window is closed
        print("\n  App window closed. Stopping dashboard.")
    else:
        # No Chrome/Edge found — fall back to the default browser.
        print("  (Chrome/Edge not found — opening in your default browser.)")
        print("=" * 60)
        webbrowser.open(url)
        try:
            input("  Press Enter here to stop the dashboard...\n")
        except EOFError:
            import time
            while True:
                time.sleep(3600)

    server.shutdown()


if __name__ == "__main__":
    main()
