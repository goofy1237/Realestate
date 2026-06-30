# =============================================================================
#  geocode.py  —  turn an address into map coordinates (free, OpenStreetMap)
# =============================================================================
#  Uses the free Nominatim service. No API key, no cost. We:
#    * cache every result on disk so we never look up the same address twice
#    * rate-limit to <=1 request/second (Nominatim's usage policy)
#    * send a descriptive User-Agent with a contact (also policy)
#  If a lookup fails, we return None and the caller degrades gracefully.
# =============================================================================

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import config

CACHE_FILE = Path(__file__).parent / "output" / "geo_cache.json"
# Nominatim asks for a contact email (politeness). Set yours in config.py.
CONTACT_EMAIL = getattr(config, "NOMINATIM_CONTACT_EMAIL", "you@example.com")
USER_AGENT = f"LiveluxeAcquisitionTool/0.1 ({CONTACT_EMAIL})"

NOMINATIM = "https://nominatim.openstreetmap.org/search"
_MIN_INTERVAL = 1.1          # seconds between calls (politeness)
_last_call = [0.0]


def _load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


_cache = _load_cache()


def _save_cache():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(_cache, indent=2), encoding="utf-8")


def _throttle():
    elapsed = time.time() - _last_call[0]
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_call[0] = time.time()


def _clean_address(address):
    """
    Nominatim struggles with unit-number prefixes ('3905/80 A'Beckett St').
    Drop the bit before the first '/' so we geocode the street address.
    Returns a list of query variants to try, best first.
    """
    variants = []
    if "/" in address:
        variants.append(address.split("/", 1)[1].strip())
    variants.append(address)
    # De-duplicate while preserving order.
    seen, out = set(), []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _query_nominatim(q):
    _throttle()
    params = urllib.parse.urlencode({
        "q": q, "format": "json", "limit": 1, "countrycodes": "au",
    })
    try:
        req = urllib.request.Request(f"{NOMINATIM}?{params}",
                                     headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode())
        if data:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
    return None


def geocode(address):
    """Return (lat, lng) for an address, or None. Cached on disk."""
    if not address:
        return None
    if address in _cache and _cache[address]:
        return tuple(_cache[address])

    result = None
    for q in _clean_address(address):
        result = _query_nominatim(q)
        if result:
            break

    _cache[address] = list(result) if result else None
    _save_cache()
    return result
