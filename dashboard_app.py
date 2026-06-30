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
    import socket
    import time
    storage.init_db()

    server = ThreadingHTTPServer(("127.0.0.1", dashboard.PORT), dashboard.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{dashboard.PORT}"

    # Wait until the server is actually accepting connections.
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", dashboard.PORT), 1):
                break
        except OSError:
            time.sleep(0.2)

    print("=" * 60)
    print("  LIVELUXE — Dashboard (app window)")
    print(f"  Running at {url}")
    print("  >>> KEEP THIS WINDOW OPEN. Press Ctrl+C to stop. <<<")
    print("=" * 60)

    browser = find_browser()
    if browser:
        # Fire-and-forget — do NOT wait on the process (Chrome hands off to a
        # background instance and the launched process exits immediately).
        subprocess.Popen([
            browser, f"--app={url}", f"--user-data-dir={APP_PROFILE}",
            "--window-size=1200,900", "--no-first-run",
            "--no-default-browser-check",
        ])
    else:
        webbrowser.open(url)

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    server.shutdown()


if __name__ == "__main__":
    main()
