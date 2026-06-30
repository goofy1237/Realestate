# =============================================================================
#  scoring.py  —  the deterministic acquisition scoring system
# =============================================================================
#  Two layers, exactly per the Acquisition Criteria spec:
#    LAYER 1  hard gates (G1..G5) — pass / reject / flag-to-verify
#    LAYER 2  weighted 0-100 score from 5 components (A..E)
#  Then a verdict (Pursue / Inspect / Pass) that the human can always override.
#
#  All thresholds, point values and keyword lists live in config.py.
#  Component B (location) is supplied by the separate location module; if it
#  isn't available yet, location-dependent gates flag to VERIFY (never reject
#  on missing data), and the composite is marked provisional.
# =============================================================================

import config


def _find_hits(text, keywords):
    """Return the list of keywords present in text (already lowercased)."""
    return [k for k in keywords if k in text]


def _bed_band_key(beds):
    """Map a bedroom count to its rent-band key (4+ -> 4). None if off-band."""
    if beds is None:
        return None
    if beds >= 4:
        return 4
    if beds in config.RENT_BANDS:
        return beds
    return None  # e.g. 2BR / studio have no band (off-target anyway)


# ---------------------------------------------------------------------------
#  LAYER 2 components
# ---------------------------------------------------------------------------

def component_A_standout(text):
    """Standout / character — 30 pts. The decisive filter."""
    score, hooks = 0, []
    for phrases, pts in config.STANDOUT_HOOKS:
        hit = next((p for p in phrases if p in text), None)
        if hit:
            score += pts
            hooks.append((hit, pts))
    return min(score, config.STANDOUT_CAP), hooks


def component_C_amenities(text, parking):
    """Amenities & extras — 20 pts, in the guide's priority order."""
    parts, score = {}, 0
    has_parking = bool(parking and parking > 0)
    if has_parking:
        score += config.AMENITY_POINTS["car_park"]; parts["car_park"] = config.AMENITY_POINTS["car_park"]
    if _find_hits(text, config.POOL_KEYWORDS):
        score += config.AMENITY_POINTS["pool"]; parts["pool"] = config.AMENITY_POINTS["pool"]
    if _find_hits(text, config.GYM_KEYWORDS):
        score += config.AMENITY_POINTS["gym"]; parts["gym"] = config.AMENITY_POINTS["gym"]
    if _find_hits(text, config.FURNISHED_KEYWORDS):
        score += config.AMENITY_POINTS["furnished"]; parts["furnished"] = config.AMENITY_POINTS["furnished"]
    return min(score, config.AMENITY_CAP), parts, has_parking


def component_D_interior(text):
    """Interior & space — 15 pts. Text-inferred; rest is human-confirmed."""
    parts, score = {}, 0
    if _find_hits(text, config.INTERIOR_ADD_BEDROOM_KEYWORDS):
        score += 6; parts["scope_to_add_bedroom"] = 6
    if _find_hits(text, config.INTERIOR_SPACIOUS_KEYWORDS):
        score += 4; parts["spacious"] = 4
    if _find_hits(text, config.INTERIOR_LIGHT_KEYWORDS):
        score += 3; parts["light_flow"] = 3
    if _find_hits(text, config.INTERIOR_OPEN_KEYWORDS):
        score += 2; parts["open_space"] = 2
    return min(score, config.INTERIOR_CAP), parts


def component_E_pricing(beds, rent, a_score, text, has_parking,
                        d_parts, location_norm):
    """Pricing fit — 10 pts. Above-band needs the premium test (>=3 ticks)."""
    key = _bed_band_key(beds)
    if key is None:
        return 0, "no-band", [], None       # off-target bedrooms; G1 handles it
    if rent is None:
        return 0, "rent-unknown", [], None
    low, high = config.RENT_BANDS[key]

    if rent < low:
        return 8, "below-band", [], None
    if high is None or rent <= high:
        return 10, "in-band", [], None

    # Above band -> premium test.
    ticks = []
    if a_score > 0:
        ticks.append("distinctive design")
    if _find_hits(text, config.POOL_KEYWORDS + config.GYM_KEYWORDS) or \
       any(p in text for p in ("sauna", "steam room")):
        ticks.append("premium amenities")
    if location_norm is not None and location_norm >= config.G5_1BR_LOCATION_MIN:
        ticks.append("exceptional location")
    if "scope_to_add_bedroom" in d_parts:
        ticks.append("scope to add bedroom")
    if has_parking:
        ticks.append("car park included")

    if len(ticks) >= config.PREMIUM_TICKS_REQUIRED:
        return 6, "above-band-premium-justified", ticks, True
    return 0, "above-band-not-justified", ticks, False


# ---------------------------------------------------------------------------
#  Main entry: score one listing
# ---------------------------------------------------------------------------

def score_listing(rec, location=None):
    """
    rec      : a parsed listing dict from rea_parse.parse_listing()
    location : optional dict {"b_score": 0-25, "normalized": 0-100, "parts": {...}}
               from the location module. If None, location is treated as pending.
    """
    text = (rec.get("description") or "").lower()
    beds = rec.get("bedrooms")
    rent = rec.get("price_per_week")
    parking = rec.get("parking")
    postcode = str(rec.get("postcode") or "")

    gates, flags, verify = {}, [], []

    # ---- Component A first (it drives Gate G3) ----
    a_score, hooks = component_A_standout(text)

    # ---- Component B (location) ----
    b_confident = True
    if location and location.get("b_score") is not None:
        b_score = location["b_score"]
        b_norm = location.get("normalized")
        b_pending = False
        b_confident = location.get("confident", True)
        if not b_confident:
            verify.append("location proximity needs verification")
    else:
        b_score, b_norm, b_pending = 0, None, True
        b_confident = False
        verify.append("location pending geocode")

    # ---- Components C, D ----
    c_score, c_parts, has_parking = component_C_amenities(text, parking)
    d_score, d_parts = component_D_interior(text)
    verify.append("interior factors need inspection")  # per spec, human top-up

    # ---- Component E (pricing) ----
    # Only let the "exceptional location" premium tick count if we're confident.
    e_loc_norm = b_norm if b_confident else None
    e_score, band_status, ticks, premium_ok = component_E_pricing(
        beds, rent, a_score, text, has_parking, d_parts, e_loc_norm)

    # ===================== LAYER 1 — HARD GATES =====================
    # G1 — bedroom config
    if beds is None:
        gates["G1"] = ("verify", "bedroom count unknown")
        verify.append("bedroom count unknown")
    elif beds in config.OFFTARGET_BEDROOMS or beds == 0:
        gates["G1"] = ("reject", f"{beds}BR / studio is off-target")
    elif beds in config.TARGET_BEDROOMS or beds >= 4:
        gates["G1"] = ("pass", f"{beds}BR")
    else:
        gates["G1"] = ("reject", f"{beds}BR off-target")

    # G2 — location band
    if postcode in [str(p) for p in config.LOCATION_BAND_POSTCODES]:
        gates["G2"] = ("pass", f"postcode {postcode} in band")
    elif b_pending:
        gates["G2"] = ("verify", "location band not yet confirmed")
        verify.append("location band unconfirmed")
    else:
        gates["G2"] = ("reject", f"postcode {postcode} outside band")

    # G3 — standout (the decisive gate)
    if a_score > 0:
        gates["G3"] = ("pass", "; ".join(h for h, _ in hooks))
    else:
        gates["G3"] = ("reject", "generic — no standout hook")

    # G4 — short-stay permission (never in the data -> always flag to verify)
    gates["G4"] = ("verify", "short-stay permission unknown — confirm on call")
    verify.append("short-stay permission unknown")

    # G5 — 1BR premium-location bar
    if beds == 1:
        if b_pending or not b_confident:
            gates["G5"] = ("verify", "1BR location bar pending / low-confidence")
            verify.append("1BR location bar pending")
        elif b_norm is not None and b_norm >= config.G5_1BR_LOCATION_MIN:
            gates["G5"] = ("pass", f"location {b_norm:.0f} >= {config.G5_1BR_LOCATION_MIN}")
        else:
            gates["G5"] = ("reject",
                           f"1BR location {b_norm:.0f} < {config.G5_1BR_LOCATION_MIN}")
    else:
        gates["G5"] = ("na", "not a 1BR")

    # ---- amenity flag ----
    if not has_parking:
        flags.append("NO PARKING")
    if band_status == "above-band-not-justified":
        flags.append("OVER BAND — negotiate down")

    # ===================== COMPOSITE & VERDICT =====================
    composite = a_score + b_score + c_score + d_score + e_score
    provisional = b_pending or not b_confident

    reject_reasons = [note for g, (st, note) in gates.items() if st == "reject"]
    rejected = len(reject_reasons) > 0

    if rejected:
        verdict = "Pass (reject)"
    elif composite >= 70:
        verdict = "Pursue & apply"
    elif composite >= 50:
        verdict = "Inspect first"
    else:
        verdict = "Pass (low priority)"

    return {
        "listing_id": rec.get("listing_id"),
        "address": rec.get("address"),
        "suburb": rec.get("suburb"),
        "bedrooms": beds,
        "rent": rent,
        "composite": composite,
        "composite_provisional": provisional,
        "verdict": verdict,
        "rejected": rejected,
        "reject_reasons": reject_reasons,
        "verify_badge": len(verify) > 0,
        "verify_reasons": sorted(set(verify)),
        "flags": flags,
        "gates": gates,
        "scores": {
            "A_standout": a_score, "B_location": b_score, "C_amenities": c_score,
            "D_interior": d_score, "E_pricing": e_score,
        },
        "detail": {
            "hooks": hooks, "amenities": c_parts, "interior": d_parts,
            "band_status": band_status, "premium_ticks": ticks,
            "location_pending": b_pending,
        },
    }


def score_many(records, locations=None):
    """Score a list of parsed listings; return sorted by composite desc."""
    out = []
    for rec in records:
        loc = (locations or {}).get(rec.get("listing_id"))
        out.append(score_listing(rec, loc))
    out.sort(key=lambda r: r["composite"], reverse=True)
    return out
