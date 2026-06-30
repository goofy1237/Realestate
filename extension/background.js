// =============================================================================
//  background.js  —  sends captured data to your local tool (localhost:8765)
// =============================================================================
//  The extension's background worker is allowed to send data to your own
//  computer's local receiver without browser cross-origin restrictions.
//  It records the result so the popup can show you what happened.
// =============================================================================

const RECEIVER_URL = "http://localhost:8765/ingest";

chrome.runtime.onMessage.addListener(function (msg, sender, sendResponse) {
  if (msg && msg.type === "capture") {
    fetch(RECEIVER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(msg.payload)
    })
      .then(function (r) { return r.json(); })
      .then(function (j) {
        chrome.storage.local.set({
          lastCapture: {
            when: Date.now(),
            url: msg.payload.url,
            ok: true,
            result: j
          }
        });
        sendResponse({ ok: true, result: j });
      })
      .catch(function (e) {
        chrome.storage.local.set({
          lastCapture: {
            when: Date.now(),
            url: msg.payload.url,
            ok: false,
            error: String(e)
          }
        });
        sendResponse({ ok: false, error: String(e) });
      });
    return true; // keep the message channel open for the async response
  }
});
