# =============================================================================
#  rea_parse.py  —  turn a captured REA page into clean listing records
# =============================================================================
#  realestate.com.au embeds its search results in the page as:
#      window.ArgonautExchange = { "<app>": { "urqlClientCache": "<json str>" } }
#  ...where the cache is JSON encoded inside JSON. This module decodes that
#  chain and pulls out one clean dict per listing, using the field paths in
#  config.py (so any future fixes happen there, not scattered through code).
# =============================================================================

import json
import re

import config


# -- small helpers ------------------------------------------------------------

def dig(obj, path, default=None):
    """Follow a list of keys into nested dicts; return default if missing."""
    cur = obj
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def parse_price_per_week(display):
    """'$880 per week' -> 880 ; '$1,250 pw' -> 1250 ; unclear -> None."""
    if not display:
        return None
    text = display.lower().replace(",", "")
    # Ignore monthly/annual quotes; we want weekly.
    nums = re.findall(r"\$?\s*(\d{2,5})", text)
    if not nums:
        return None
    value = int(nums[0])
    # Sanity: weekly rents are roughly $100–$10,000.
    if 100 <= value <= 10000:
        return value
    return None


def strip_html(text):
    """Turn the description's <br/> etc. into plain readable text."""
    if not text:
        return ""
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


# -- the decode chain ---------------------------------------------------------

def extract_argonaut_object(html):
    """Find `window.ArgonautExchange={...}` and return the parsed object."""
    marker = config.ARGONAUT_MARKER
    i = html.find(marker)
    if i == -1:
        return None
    start = i + len(marker)
    if start >= len(html) or html[start] != "{":
        return None

    # Balanced-brace scan that respects JSON strings and escapes.
    depth, in_str, esc = 0, False, False
    for j in range(start, len(html)):
        c = html[j]
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[start:j + 1])
                except json.JSONDecodeError:
                    return None
    return None


def get_search_data(argonaut):
    """Decode the urql cache and return the rentSearch data dict."""
    app = dig(argonaut, [config.ARGONAUT_APP_KEY], {})
    cache_str = app.get(config.ARGONAUT_CACHE_KEY) if isinstance(app, dict) else None
    if not cache_str:
        return None
    try:
        cache = json.loads(cache_str)
    except json.JSONDecodeError:
        return None

    for entry in cache.values():
        data_str = entry.get("data") if isinstance(entry, dict) else None
        if not data_str:
            continue
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            continue
        for root in config.SEARCH_ROOT_KEYS:
            if root in data:
                return data[root]
    return None


def parse_listing(listing):
    """Map one raw listing object to our clean, flat record."""
    rec = {}
    for field, path in config.LISTING_FIELD_PATHS.items():
        rec[field] = dig(listing, path)

    # Derived / cleaned fields:
    rec["price_per_week"] = parse_price_per_week(rec.get("price_display"))
    rec["description"] = strip_html(rec.get("description"))

    # Agent(s): take the first lister's name + phone, keep all names too.
    listers = listing.get("listers") or []
    names = [l.get("name") for l in listers if isinstance(l, dict) and l.get("name")]
    phone = None
    for l in listers:
        ph = dig(l, ["phoneNumber", "display"])
        if ph:
            phone = ph
            break
    rec["agent_name"] = names[0] if names else None
    rec["agent_names_all"] = "; ".join(names) if names else None
    rec["agent_phone"] = phone

    # Inspections (handy for follow-ups later):
    insp = listing.get("inspections") or []
    rec["inspections"] = "; ".join(
        dig(x, ["display", "longLabel"], "") for x in insp if isinstance(x, dict)
    ) or None

    # Main image (replace the {size} placeholder with a real size):
    img = dig(listing, ["media", "mainImage", "templatedUrl"])
    rec["image_url"] = img.replace("{size}", "640x480") if img else None

    rec["product_depth"] = listing.get("productDepth")
    return rec


def _decoded_cache_objects(argonaut):
    """Decode every urql cache entry's 'data' string into objects."""
    objs = []
    app = dig(argonaut, [config.ARGONAUT_APP_KEY], {})
    cache_str = app.get(config.ARGONAUT_CACHE_KEY) if isinstance(app, dict) else None
    if not cache_str:
        return objs
    try:
        cache = json.loads(cache_str)
    except json.JSONDecodeError:
        return objs
    for entry in cache.values():
        data_str = entry.get("data") if isinstance(entry, dict) else None
        if data_str:
            try:
                objs.append(json.loads(data_str))
            except json.JSONDecodeError:
                pass
    return objs


def extract_listings_from_html(html):
    """Top-level: page HTML -> list of clean listing records."""
    argonaut = extract_argonaut_object(html)
    if not argonaut:
        return [], "no_argonaut"

    out = []

    # 1) Preferred: the search-results path (keeps exact/surrounding buckets).
    search = get_search_data(argonaut)
    if search:
        results = search.get("results") or {}
        for bucket in config.RESULT_BUCKETS:
            b = results.get(bucket) or {}
            items = b.get("items") if isinstance(b, dict) else None
            if not items:
                continue
            for item in items:
                listing = item.get("listing") if isinstance(item, dict) else None
                if listing:
                    rec = parse_listing(listing)
                    rec["result_bucket"] = bucket  # "exact" or "surrounding"
                    out.append(rec)

    # 2) Fallback: scan the whole decoded cache for any listing-shaped objects
    #    (covers single-listing detail pages and any structure we don't map).
    if not out:
        seen = set()
        for obj in _decoded_cache_objects(argonaut):
            for listing in find_listings_anywhere(obj):
                rec = parse_listing(listing)
                lid = rec.get("listing_id")
                if lid and lid not in seen:
                    seen.add(lid)
                    rec["result_bucket"] = "other"
                    out.append(rec)

    if out:
        return out, "ok"
    return [], "no_search_data"


def _looks_like_listing(d):
    """True if a dict looks like one REA listing object."""
    if not isinstance(d, dict):
        return False
    if d.get("__typename") == "RentResidentialListing":
        return True
    return ("generalFeatures" in d and "address" in d
            and "price" in d and "id" in d)


def find_listings_anywhere(obj, found=None, depth=0):
    """
    Recursively collect listing-shaped objects from ANY JSON structure.
    Used for the data REA fetches when you page through results (page 2, 3...),
    which arrives via a background request rather than the initial HTML.
    """
    if found is None:
        found = []
    if depth > 16:
        return found
    if isinstance(obj, dict):
        if _looks_like_listing(obj):
            found.append(obj)            # don't recurse into a found listing
        else:
            for v in obj.values():
                find_listings_anywhere(v, found, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            find_listings_anywhere(v, found, depth + 1)
    return found


def extract_listings_from_responses(responses):
    """Parse listings out of captured background data requests (pagination)."""
    out = []
    for r in responses or []:
        text = r.get("text")
        if not text:
            continue
        try:
            obj = json.loads(text)
        except Exception:
            continue
        for listing in find_listings_anywhere(obj):
            rec = parse_listing(listing)
            rec["result_bucket"] = "paginated"
            out.append(rec)
    return out


def extract_listings_from_payload(payload):
    """
    Parse a capture payload from the extension. Combines:
      * the initial page's embedded data (ArgonautExchange in the HTML)
      * any background data requests (later pages: list-2, list-3, ...)
    Merged and de-duplicated on listing_id.
    """
    html = payload.get("outerHTML") or ""
    ssr, status = extract_listings_from_html(html)
    net = extract_listings_from_responses(payload.get("networkResponses"))

    merged = {}
    for rec in ssr + net:           # SSR first so it wins ties
        lid = rec.get("listing_id")
        if lid and lid not in merged:
            merged[lid] = rec

    result = list(merged.values())
    if result:
        return result, "ok"
    return result, status
