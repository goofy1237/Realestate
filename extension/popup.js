// Shows last-capture status, and lets you toggle auto-advance + page limit.

function render(last) {
  var status = document.getElementById("status");
  var detail = document.getElementById("detail");
  if (!last) {
    status.textContent = "No captures yet. Open a realestate.com.au page.";
    return;
  }
  var when = new Date(last.when).toLocaleTimeString();
  if (last.ok) {
    var r = last.result || {};
    status.innerHTML = '<span class="ok">Captured OK</span> at ' + when;
    detail.innerHTML =
      "Listings found on that page: <b>" +
      (r.listings_found != null ? r.listings_found : "?") + "</b>" +
      "<br><span class='muted'>" + (last.url || "").slice(0, 60) + "…</span>";
  } else {
    status.innerHTML = '<span class="bad">Could not reach the local tool</span> at ' + when;
    detail.innerHTML =
      "<span class='muted'>Is the receiver running? Error: " +
      (last.error || "") + "</span>";
  }
}

// --- load current state ---
chrome.storage.local.get(["lastCapture", "autoAdvance", "maxPages"], function (data) {
  render(data ? data.lastCapture : null);
  document.getElementById("autoAdvance").checked = !!(data && data.autoAdvance);
  document.getElementById("maxPages").value = (data && data.maxPages) || 5;
});

// --- save settings on change ---
document.getElementById("autoAdvance").addEventListener("change", function () {
  chrome.storage.local.set({ autoAdvance: this.checked });
});
document.getElementById("maxPages").addEventListener("change", function () {
  var n = parseInt(this.value, 10);
  if (isNaN(n) || n < 1) n = 1;
  if (n > 50) n = 50;
  this.value = n;
  chrome.storage.local.set({ maxPages: n });
});

document.getElementById("recapture").addEventListener("click", function () {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    if (tabs && tabs[0]) { chrome.tabs.reload(tabs[0].id); window.close(); }
  });
});
