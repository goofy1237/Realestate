# =============================================================================
#  location.py  —  Component B (Location, 25 pts) + data for Gates G2/G5
# =============================================================================
#  For each listing we:
#    1. geocode the address (geocode.py, free OpenStreetMap)
#    2. ask OpenStreetMap (Overpass) what's nearby: trains/trams, hotels,
#       hospitals, dining/retail
#    3. award points per the spec:
#         right area for property type  7
#         close to transport (<=500m)   5
#         close to amenities (walkable) 5
#         close to hotels (<=600m)      4
#         close to hospitals (<=1.5km)  4
#       capped at 25; normalized = score/25*100 (feeds Gate G5).
#
#  Networked + slower than the rest, so results are cached on disk. If Overpass
#  is unavailable we still return the right-area points and mark the proximity
#  factors as "needs verify" (confident=False) so nothing is unfairly rejected.
# =============================================================================

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import config
import geocode

CACHE_FILE = Path(__file__).parent / "output" / "overpass_cache.json"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_MIN_INTERVAL = 1.2
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


def _overpass_nearby(lat, lng):
    """One combined query; returns dict of counts by category (or None)."""
    key = f"{lat:.5f},{lng:.5f}"
    if key in _cache:
        return _cache[key]

    query = f"""
    [out:json][timeout:25];
    (
      node(around:500,{lat},{lng})[railway=tram_stop];
      node(around:500,{lat},{lng})[railway=station];
      node(around:600,{lat},{lng})[tourism=hotel];
      node(around:1500,{lat},{lng})[amenity=hospital];
      way(around:1500,{lat},{lng})[amenity=hospital];
      node(around:400,{lat},{lng})[amenity=restaurant];
      node(around:400,{lat},{lng})[amenity=cafe];
      node(around:400,{lat},{lng})[shop];
    );
    out tags center;
    """
    _throttle()
    try:
        data = urllib.parse.urlencode({"data": query}).encode()
        req = urllib.request.Request(
            OVERPASS_URL, data=data,
            headers={"User-Agent": geocode.USER_AGENT})
        with urllib.request.urlopen(req, timeout=40) as r:
            payload = json.loads(r.read().decode())
    except Exception:
        return None

    counts = {"transport": 0, "hotel": 0, "hospital": 0, "food_retail": 0}
    for el in payload.get("elements", []):
        tags = el.get("tags", {})
        if tags.get("railway") in ("tram_stop", "station"):
            counts["transport"] += 1
        elif tags.get("tourism") == "hotel":
            counts["hotel"] += 1
        elif tags.get("amenity") == "hospital":
            counts["hospital"] += 1
        elif tags.get("amenity") in ("restaurant", "cafe") or "shop" in tags:
            counts["food_retail"] += 1

    _cache[key] = counts
    _save_cache()
    return counts


def _right_area_points(rec):
    """7 pts if the listing's standout type suits its suburb (per spec map)."""
    suburb = (rec.get("suburb") or "").strip()
    text = (rec.get("description") or "").lower()
    for hook_type, suburbs in config.RIGHT_AREA_FOR_TYPE.items():
        if hook_type in text and suburb in suburbs:
            return 7, f"{hook_type} suits {suburb}"
    return 0, None


def compute_location(rec):
    """Return location sub-score dict for one listing."""
    parts = {}
    confident = True
    notes = []

    # Right area (needs only suburb/description — always available).
    ra_pts, ra_note = _right_area_points(rec)
    if ra_pts:
        parts["right_area"] = ra_pts
        notes.append(ra_note)

    coords = geocode.geocode(rec.get("address"))
    if not coords:
        # No geocode -> only right-area known; proximity needs verification.
        return {
            "b_score": ra_pts,
            "normalized": (ra_pts / 25) * 100,
            "parts": parts,
            "confident": False,
            "coords": None,
            "notes": notes + ["address could not be geocoded"],
        }

    lat, lng = coords
    nearby = _overpass_nearby(lat, lng)
    if nearby is None:
        # Geocoded but POI lookup failed -> don't penalise; flag to verify.
        return {
            "b_score": ra_pts,
            "normalized": (ra_pts / 25) * 100,
            "parts": parts,
            "confident": False,
            "coords": [lat, lng],
            "notes": notes + ["nearby-amenities lookup unavailable; verify"],
        }

    if nearby["transport"] > 0:
        parts["transport"] = 5
    if nearby["food_retail"] >= 10:
        parts["amenities"] = 5
    elif nearby["food_retail"] >= 3:
        parts["amenities"] = 3
    if nearby["hotel"] > 0:
        parts["hotels"] = 4
    if nearby["hospital"] > 0:
        parts["hospitals"] = 4

    b_score = min(sum(parts.values()), 25)
    return {
        "b_score": b_score,
        "normalized": (b_score / 25) * 100,
        "parts": parts,
        "confident": confident,
        "coords": [lat, lng],
        "notes": notes,
    }


def build_locations(records, progress=False):
    """Compute locations for many listings -> {listing_id: loc_dict}."""
    out = {}
    for i, rec in enumerate(records, 1):
        lid = rec.get("listing_id")
        out[lid] = compute_location(rec)
        if progress:
            loc = out[lid]
            print(f"  [{i}/{len(records)}] {(rec.get('address') or '')[:40]:<40} "
                  f"B={loc['b_score']:>2}/25  "
                  f"{'(verify)' if not loc['confident'] else ''}")
    return out
