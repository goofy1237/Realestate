# =============================================================================
#  app.py  —  the LuxeBot Portal (one window for everything)
# =============================================================================
#  Runs BOTH the capture receiver and the dashboard in a single process, then
#  opens one app window. From that window you can:
#    * open realestate.com.au to capture (browse -> auto-saved)
#    * click "Score now" to add location scores
#    * view / filter / sort the shortlist, edit verdict/stage/follow-ups
#    * export to Excel
#  Close the window to stop everything.
# =============================================================================

import threading
from http.server import ThreadingHTTPServer

import dashboard
import dashboard_app
import db
import receiver
import storage


def main():
    print("=" * 60)
    print("  LuxeBot Portal")
    print("=" * 60)
    print(f"  Database: {db.backend_name()}")
    storage.init_db()

    # Capture receiver (the browser extension posts here).
    rsrv = ThreadingHTTPServer(("127.0.0.1", receiver.PORT), receiver.Handler)
    threading.Thread(target=rsrv.serve_forever, daemon=True).start()
    print(f"  Capture receiver: http://localhost:{receiver.PORT}")

    # Dashboard / control panel.
    dsrv = ThreadingHTTPServer(("127.0.0.1", dashboard.PORT), dashboard.Handler)
    threading.Thread(target=dsrv.serve_forever, daemon=True).start()
    url = f"http://localhost:{dashboard.PORT}"
    print(f"  Portal: {url}")
    print("=" * 60)

    # Open the portal as a desktop app window (Chrome/Edge --app), or fall
    # back to the default browser. Closing the window stops the app.
    browser = dashboard_app.find_browser()
    if browser:
        import subprocess
        proc = subprocess.Popen([
            browser, f"--app={url}",
            f"--user-data-dir={dashboard_app.APP_PROFILE}",
            "--window-size=1280,900", "--no-first-run",
            "--no-default-browser-check",
        ])
        proc.wait()
        print("\n  Portal window closed. Stopping.")
    else:
        import webbrowser
        webbrowser.open(url)
        try:
            input("  Press Enter here to stop the portal...\n")
        except EOFError:
            import time
            while True:
                time.sleep(3600)

    rsrv.shutdown()
    dsrv.shutdown()


if __name__ == "__main__":
    main()
