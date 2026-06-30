# =============================================================================
#  app.py  —  the LuxeBot Portal (one window for everything)
# =============================================================================
#  Runs BOTH the capture receiver and the dashboard in a single process, then
#  opens one app window. From that window you can:
#    * open realestate.com.au to capture (browse -> auto-saved)
#    * click "Score now" to add location scores
#    * view / filter / sort the shortlist, edit verdict/stage/follow-ups
#    * export to Excel
#  Keep the small console window open while you work; close it (or press
#  Ctrl+C) to stop the portal.
# =============================================================================

import socket
import subprocess
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer

import dashboard
import dashboard_app
import db
import receiver
import storage

HOST = "127.0.0.1"   # use the explicit IPv4 address (avoids localhost/IPv6 issues)


def _serve(port, handler):
    """Start a server in a daemon thread. Returns the server, or None if the
    port is already in use (i.e. the portal is already running)."""
    try:
        srv = ThreadingHTTPServer((HOST, port), handler)
    except OSError:
        return None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _wait_ready(port, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _open_window(url):
    browser = dashboard_app.find_browser()
    if browser:
        # Fire-and-forget: do NOT wait on the process (Chrome hands off to a
        # background instance and the launched process exits immediately).
        subprocess.Popen([
            browser, f"--app={url}",
            f"--user-data-dir={dashboard_app.APP_PROFILE}",
            "--window-size=1280,900", "--no-first-run",
            "--no-default-browser-check",
        ])
    else:
        webbrowser.open(url)


def main():
    print("=" * 60)
    print("  LuxeBot Portal")
    print("=" * 60)
    print(f"  Database: {db.backend_name()}")
    try:
        storage.init_db()
    except Exception as e:
        print(f"  WARNING: could not reach the database: {e}")
        print("  Check your .env / internet. Opening anyway.")

    url = f"http://{HOST}:{dashboard.PORT}"

    dsrv = _serve(dashboard.PORT, dashboard.Handler)
    if dsrv is None:
        # Already running — just open the window to the existing portal.
        print("  Portal already running — opening the window.")
        _open_window(url)
        return
    rsrv = _serve(receiver.PORT, receiver.Handler)

    _wait_ready(dashboard.PORT)
    print(f"  Capture receiver: http://{HOST}:{receiver.PORT}")
    print(f"  Portal:           {url}")
    print("=" * 60)
    print("  Opening the portal window...")
    print("  >>> KEEP THIS WINDOW OPEN. Press Ctrl+C here to stop. <<<")
    _open_window(url)

    try:
        threading.Event().wait()        # keep serving until Ctrl+C / window close
    except KeyboardInterrupt:
        print("\n  Stopping portal.")
    finally:
        if rsrv:
            rsrv.shutdown()
        dsrv.shutdown()


if __name__ == "__main__":
    main()
