// =============================================================================
//  net_hook_main.js  —  records the background data requests the page makes
// =============================================================================
//  realestate.com.au may load its listing data via a background request
//  (fetch/XHR) rather than embedding it in the HTML. This runs EARLY (before
//  the page's own code) and quietly keeps a copy of any JSON-looking responses,
//  so the capture script can include them. Read-only; changes nothing on screen.
// =============================================================================

(function () {
  window.__REA_CAP_RESP__ = window.__REA_CAP_RESP__ || [];

  function record(url, text) {
    try {
      if (!text || text.length < 80) return;
      var c = text.charAt(0);
      if (c !== "{" && c !== "[") return;             // keep only JSON-ish
      if (window.__REA_CAP_RESP__.length >= 50) return;
      window.__REA_CAP_RESP__.push({
        url: String(url || ""),
        len: text.length,
        text: text.slice(0, 3000000)
      });
    } catch (e) { /* ignore */ }
  }

  // --- hook fetch ---
  var origFetch = window.fetch;
  if (origFetch) {
    window.fetch = function () {
      var args = arguments;
      return origFetch.apply(this, args).then(function (resp) {
        try {
          var u = (resp && resp.url) ||
                  (args[0] && args[0].url) || String(args[0]);
          resp.clone().text().then(function (t) { record(u, t); })
                              .catch(function () {});
        } catch (e) {}
        return resp;
      });
    };
  }

  // --- hook XMLHttpRequest ---
  var origOpen = XMLHttpRequest.prototype.open;
  var origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url) {
    this.__rea_url = url;
    return origOpen.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function () {
    var xhr = this;
    xhr.addEventListener("load", function () {
      try { record(xhr.__rea_url, xhr.responseText); } catch (e) {}
    });
    return origSend.apply(this, arguments);
  };
})();
