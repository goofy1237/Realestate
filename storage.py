# =============================================================================
#  storage.py  —  listing storage (one row per listing)
# =============================================================================
#  Works against EITHER a shared Supabase/Postgres database (so you and a
#  coworker share one set of listings) OR a local SQLite file — chosen
#  automatically by db.py based on whether a Supabase URL is configured.
#
#  Key rules (unchanged):
#    * dedupe on listing_id (re-capturing UPDATES, never duplicates)
#    * scraped + scored fields refresh on every capture
#    * YOUR fields (status, verdict_override, follow_up_date, notes) are NEVER
#      overwritten by a re-capture — they belong to you
# =============================================================================

from datetime import datetime

import db

# The seven acquisition stages (status field), in order.
STAGES = ["new", "first-contact", "application", "suitability", "lodge",
          "follow-up", "conduct", "negotiate"]

# Columns refreshed from the scraper/scorer on every capture.
_SCRAPE_FIELDS = [
    "url", "suburb", "address", "postcode", "price_per_week", "price_display",
    "bedrooms", "bathrooms", "parking", "property_type", "description",
    "agency", "agent_name", "agent_names_all", "agent_phone", "inspections",
    "bond_display", "available_date", "image_url", "product_depth",
    "result_bucket", "lat", "lng",
    "score_A", "score_B", "score_C", "score_D", "score_E", "composite",
    "composite_provisional", "verdict", "rejected", "reject_reasons",
    "flags", "verify_reasons", "hooks", "gates_json", "location_confident",
    "date_listed", "date_scraped",
]

# Columns the USER owns — never overwritten by a re-capture.
_USER_FIELDS = ["status", "verdict_override", "follow_up_date", "notes"]

# Types valid in BOTH SQLite and Postgres (TEXT / INTEGER / REAL).
_DDL = """
CREATE TABLE IF NOT EXISTS listings (
    listing_id            TEXT PRIMARY KEY,
    url                   TEXT,
    suburb                TEXT,
    address               TEXT,
    postcode              TEXT,
    price_per_week        INTEGER,
    price_display         TEXT,
    bedrooms              INTEGER,
    bathrooms             INTEGER,
    parking               INTEGER,
    property_type         TEXT,
    description           TEXT,
    agency                TEXT,
    agent_name            TEXT,
    agent_names_all       TEXT,
    agent_phone           TEXT,
    inspections           TEXT,
    bond_display          TEXT,
    available_date        TEXT,
    image_url             TEXT,
    product_depth         TEXT,
    result_bucket         TEXT,
    lat                   REAL,
    lng                   REAL,
    score_A               INTEGER,
    score_B               INTEGER,
    score_C               INTEGER,
    score_D               INTEGER,
    score_E               INTEGER,
    composite             INTEGER,
    composite_provisional INTEGER,
    verdict               TEXT,
    rejected              INTEGER,
    reject_reasons        TEXT,
    flags                 TEXT,
    verify_reasons        TEXT,
    hooks                 TEXT,
    gates_json            TEXT,
    location_confident    INTEGER,
    date_listed           TEXT,
    date_scraped          TEXT,
    status                TEXT DEFAULT 'new',
    verdict_override      TEXT,
    follow_up_date        TEXT,
    notes                 TEXT,
    date_updated          TEXT
)
"""


def init_db():
    db.execute(_DDL)
    return db.backend_name()


def _row_from(rec, score):
    """Flatten a parsed listing + its score result into DB column values."""
    now = datetime.now().isoformat(timespec="seconds")
    s = score["scores"]
    return {
        "listing_id": rec.get("listing_id"),
        "url": rec.get("url"),
        "suburb": rec.get("suburb"),
        "address": rec.get("address"),
        "postcode": rec.get("postcode"),
        "price_per_week": rec.get("price_per_week"),
        "price_display": rec.get("price_display"),
        "bedrooms": rec.get("bedrooms"),
        "bathrooms": rec.get("bathrooms"),
        "parking": rec.get("parking"),
        "property_type": rec.get("property_type"),
        "description": rec.get("description"),
        "agency": rec.get("agency"),
        "agent_name": rec.get("agent_name"),
        "agent_names_all": rec.get("agent_names_all"),
        "agent_phone": rec.get("agent_phone"),
        "inspections": rec.get("inspections"),
        "bond_display": rec.get("bond_display"),
        "available_date": rec.get("available_date"),
        "image_url": rec.get("image_url"),
        "product_depth": rec.get("product_depth"),
        "result_bucket": rec.get("result_bucket"),
        "lat": (rec.get("_coords") or [None, None])[0],
        "lng": (rec.get("_coords") or [None, None])[1],
        "score_A": s["A_standout"], "score_B": s["B_location"],
        "score_C": s["C_amenities"], "score_D": s["D_interior"],
        "score_E": s["E_pricing"], "composite": score["composite"],
        "composite_provisional": int(bool(score["composite_provisional"])),
        "verdict": score["verdict"],
        "rejected": int(bool(score["rejected"])),
        "reject_reasons": "; ".join(score["reject_reasons"]),
        "flags": "; ".join(score["flags"]),
        "verify_reasons": "; ".join(score["verify_reasons"]),
        "hooks": ", ".join(h for h, _ in score["detail"]["hooks"]),
        "gates_json": __import__("json").dumps(score["gates"]),
        "location_confident": int(not score["detail"]["location_pending"]),
        "date_listed": rec.get("date_listed"),
        "date_scraped": now,
    }


def upsert_listing(rec, score):
    """Insert or update one listing. Returns 'new' or 'updated'."""
    row = _row_from(rec, score)
    lid = row["listing_id"]
    if not lid:
        return "skipped"
    ph = db.PLACEHOLDER
    now = datetime.now().isoformat(timespec="seconds")
    conn = db.connect()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM listings WHERE listing_id={ph}", (lid,))
        exists = cur.fetchone()
        if exists:
            # Refresh everything EXCEPT date_scraped (first-seen) + user fields.
            upd = [f for f in _SCRAPE_FIELDS if f != "date_scraped"]
            sets = ", ".join(f"{k}={ph}" for k in upd)
            cur.execute(
                f"UPDATE listings SET {sets}, date_updated={ph} "
                f"WHERE listing_id={ph}",
                [row.get(k) for k in upd] + [now, lid])
            result = "updated"
        else:
            cols = ["listing_id"] + _SCRAPE_FIELDS + ["date_updated"]
            vals = [lid] + [row.get(k) for k in _SCRAPE_FIELDS] + [now]
            placeholders = ", ".join(ph for _ in cols)
            cur.execute(
                f"INSERT INTO listings ({', '.join(cols)}) "
                f"VALUES ({placeholders})", vals)
            result = "new"
        conn.commit()
        return result
    finally:
        conn.close()


def all_listings(include_rejected=True, added_from=None, added_to=None,
                 order="composite"):
    """
    List listings, newest-scored-first by default.
    added_from / added_to are 'YYYY-MM-DD' strings that filter on the date the
    listing was first added (date_scraped). order='date' sorts by date added.
    """
    ph = db.PLACEHOLDER
    clauses, params = [], []
    if not include_rejected:
        clauses.append("rejected=0")
    if added_from:
        clauses.append(f"date_scraped >= {ph}")
        params.append(f"{added_from}T00:00:00")
    if added_to:
        clauses.append(f"date_scraped <= {ph}")
        params.append(f"{added_to}T23:59:59")
    sql = "SELECT * FROM listings"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    if order == "date":
        sql += " ORDER BY date_scraped DESC, composite DESC"
    else:
        sql += " ORDER BY composite DESC"
    return db.query(sql, params)


def update_user_field(listing_id, field, value):
    """Set one user-owned field (status / verdict_override / follow_up / notes)."""
    if field not in _USER_FIELDS:
        raise ValueError(f"not a user field: {field}")
    ph = db.PLACEHOLDER
    db.execute(f"UPDATE listings SET {field}={ph} WHERE listing_id={ph}",
               (value, listing_id))


def counts():
    rows = db.query("SELECT rejected, date_scraped FROM listings")
    total = len(rows)
    alive = sum(1 for r in rows if not r.get("rejected"))
    today = datetime.now().date().isoformat()
    new_today = sum(1 for r in rows
                    if (r.get("date_scraped") or "").startswith(today))
    return {"total": total, "alive": alive, "new_today": new_today}
