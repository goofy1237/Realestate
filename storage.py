# =============================================================================
#  storage.py  —  the local SQLite database (one row per listing)
# =============================================================================
#  Stores every captured listing plus its scores and your workflow state.
#  Key rules:
#    * dedupe on listing_id (re-capturing a listing UPDATES it, never duplicates)
#    * scraped + scored fields are refreshed on every capture
#    * YOUR fields (status, verdict_override, follow_up_date, notes) are NEVER
#      overwritten by a re-capture — they belong to you
#  Uses Python's built-in sqlite3 (no installs).
# =============================================================================

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "listings.db"

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


def _conn():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute("""
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
            -- user-owned workflow fields --
            status                TEXT DEFAULT 'new',
            verdict_override      TEXT,
            follow_up_date        TEXT,
            notes                 TEXT,
            date_updated          TEXT
        )""")
    return DB_FILE


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
        "gates_json": json.dumps(score["gates"]),
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
    now = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        exists = c.execute(
            "SELECT 1 FROM listings WHERE listing_id=?", (lid,)).fetchone()
        if exists:
            # On update, refresh everything EXCEPT date_scraped (first-seen).
            upd_fields = [f for f in _SCRAPE_FIELDS if f != "date_scraped"]
            sets = ", ".join(f"{k}=?" for k in upd_fields)
            vals = [row.get(k) for k in upd_fields] + [now, lid]
            c.execute(f"UPDATE listings SET {sets}, date_updated=? "
                      f"WHERE listing_id=?", vals)
            return "updated"
        else:
            cols = ["listing_id"] + _SCRAPE_FIELDS + ["date_updated"]
            vals = [lid] + [row.get(k) for k in _SCRAPE_FIELDS] + [now]
            placeholders = ", ".join("?" for _ in cols)
            c.execute(
                f"INSERT INTO listings ({', '.join(cols)}) "
                f"VALUES ({placeholders})", vals)
            return "new"


def all_listings(include_rejected=True):
    with _conn() as c:
        q = "SELECT * FROM listings"
        if not include_rejected:
            q += " WHERE rejected=0"
        q += " ORDER BY composite DESC"
        return [dict(r) for r in c.execute(q).fetchall()]


def update_user_field(listing_id, field, value):
    """Set one user-owned field (status / verdict_override / follow_up / notes)."""
    if field not in _USER_FIELDS:
        raise ValueError(f"not a user field: {field}")
    with _conn() as c:
        c.execute(f"UPDATE listings SET {field}=? WHERE listing_id=?",
                  (value, listing_id))


def counts():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        alive = c.execute(
            "SELECT COUNT(*) FROM listings WHERE rejected=0").fetchone()[0]
        return {"total": total, "alive": alive}
