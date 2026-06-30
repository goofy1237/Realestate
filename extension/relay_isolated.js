// =============================================================================
//  relay_isolated.js  —  bridge between the page and the extension
// =============================================================================
//  The page-world scripts can't talk to the extension; this one can. It:
//    * relays captured listing data to the background worker (-> local tool)
//    * answers the capture script's request for auto-advance settings
// =============================================================================

window.addEventListener("message", function (ev) {
  if (ev.source !== window) return;
  var d = ev.data;
  if (!d) return;

  // 1) Captured listing data -> send to the local tool.
  if (d.source === "REA_CAPTURE") {
    chrome.runtime.sendMessage({ type: "capture", payload: d }, function () {
      void chrome.runtime.lastError;
    });
    return;
  }

  // 2) Capture script wants the auto-advance settings.
  if (d.source === "REA_NEED_SETTINGS") {
    chrome.storage.local.get(["autoAdvance", "maxPages"], function (cfg) {
      window.postMessage({
        source: "REA_SETTINGS",
        autoAdvance: !!(cfg && cfg.autoAdvance),
        maxPages: (cfg && cfg.maxPages) || 5
      }, "*");
    });
  }
});
