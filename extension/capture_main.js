// =============================================================================
//  capture_main.js  —  runs in the PAGE's own world (so it can see page data)
// =============================================================================
//  Reads the structured data realestate.com.au uses to render listings (not
//  the visible HTML), from several locations + the full page + the background
//  data requests (see net_hook_main.js). Runs on first load, on in-page
//  navigations (paging), and can OPTIONALLY auto-advance through result pages.
// =============================================================================

(function () {
  function safe(fn) { try { return fn(); } catch (e) { return null; } }
  function deepClone(obj) { return safe(function () { return JSON.parse(JSON.stringify(obj)); }); }

  // --- settings (auto-advance) come from the popup via the relay script ---
  var settings = { autoAdvance: false, maxPages: 5 };
  var advancing = false;   // true once we've decided to move to the next page

  window.addEventListener("message", function (ev) {
    if (ev.source !== window) return;
    var d = ev.data;
    if (d && d.source === "REA_SETTINGS") {
      settings.autoAdvance = !!d.autoAdvance;
      settings.maxPages = d.maxPages || 5;
    }
  });

  function collectAndSend() {
    if (advancing) return;             // don't re-capture while leaving the page
    var payload = {
      source: "REA_CAPTURE",
      url: location.href,
      title: document.title,
      nextDataText: safe(function () {
        var el = document.getElementById("__NEXT_DATA__");
        return el ? el.textContent : null;
      }),
      windowNextData: deepClone(safe(function () { return window.__NEXT_DATA__; })),
      argonaut: deepClone(safe(function () { return window.ArgonautExchange; })),
      initialState: deepClone(safe(function () { return window.__INITIAL_STATE__; })),
      reaState: deepClone(safe(function () {
        return window.REA && window.REA.state ? window.REA.state : null;
      })),
      apolloState: deepClone(safe(function () { return window.__APOLLO_STATE__; })),
      outerHTML: safe(function () {
        var h = document.documentElement.outerHTML || "";
        return h.slice(0, 5000000);
      }),
      networkResponses: safe(function () { return window.__REA_CAP_RESP__ || []; }) || []
    };
    window.postMessage(payload, "*");
    try { window.__REA_CAP_RESP__ = []; } catch (e) {}

    maybeAutoAdvance();
  }

  function schedule(delay) { setTimeout(collectAndSend, delay || 4000); }

  // ---- initial page ----
  if (document.readyState === "complete") {
    schedule();
  } else {
    window.addEventListener("load", function () { schedule(); });
  }

  // ---- re-capture when paging WITHOUT a full reload (site's own Next button) --
  var lastUrl = location.href;
  function onNavigation() {
    if (advancing) return;
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      schedule(4000);
    }
  }
  var _push = history.pushState;
  history.pushState = function () {
    var r = _push.apply(this, arguments); setTimeout(onNavigation, 50); return r;
  };
  var _replace = history.replaceState;
  history.replaceState = function () {
    var r = _replace.apply(this, arguments); setTimeout(onNavigation, 50); return r;
  };
  window.addEventListener("popstate", function () { setTimeout(onNavigation, 50); });
  setInterval(onNavigation, 1500);

  // ---- auto-advance through result pages (optional) -------------------------
  function currentPageNum() {
    var m = location.pathname.match(/\/list-(\d+)/);
    return m ? parseInt(m[1], 10) : 1;
  }
  function nextPageUrl() {
    var n = currentPageNum();
    if (/\/list-\d+/.test(location.pathname)) {
      return location.href.replace(/\/list-\d+/, "/list-" + (n + 1));
    }
    var u = new URL(location.href);
    u.pathname = u.pathname.replace(/\/?$/, "") + "/list-2";
    return u.toString();
  }
  function isSearchListPage() {
    return location.pathname.indexOf("/rent/") !== -1 &&
           location.pathname.indexOf("/property-") === -1;
  }
  function hasResults() {
    // A real results page links to individual properties; an empty/last page
    // does not. This stops us one page after the final page of results.
    return document.querySelectorAll('a[href*="/property-"]').length > 0;
  }
  function maybeAutoAdvance() {
    if (!settings.autoAdvance || !isSearchListPage() || !hasResults()) return;
    if (currentPageNum() >= settings.maxPages) return;       // reached the cap
    advancing = true;
    var delay = 3000 + Math.floor(Math.random() * 2000);     // polite 3–5s
    var target = nextPageUrl();
    setTimeout(function () { location.href = target; }, delay);
  }

  // Ask the relay (which can read the extension's settings) for our config.
  window.postMessage({ source: "REA_NEED_SETTINGS" }, "*");
})();
