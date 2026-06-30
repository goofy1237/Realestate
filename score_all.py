# =============================================================================
#  score_all.py  —  add location scores + finalise verdicts for the database
# =============================================================================
#  The receiver stores listings fast, WITHOUT the (slow, networked) location
#  step. Run this after browsing to:
#    * geocode each listing (free OpenStreetMap, cached)
#    * look up nearby transport/hotels/hospitals/dining
#    * compute Component B + Gates G2/G5
#    * re-score and write final verdicts back to the database
#  Your workflow fields (status, verdict, follow-ups, notes) are preserved.
#
#  Run it via run_score.bat. Safe to run repeatedly; caching makes re-runs fast.
# =============================================================================

import location
import scoring
import storage

# These are the listing fields the scorer/location need, read back from the DB.
_REC_FIELDS = [
    "listing_id", "url", "suburb", "address", "postcode", "price_per_week",
    "price_display", "bedrooms", "bathrooms", "parking", "property_type",
    "description", "agency", "agent_name", "agent_names_all", "agent_phone",
    "inspections", "bond_display", "available_date", "image_url",
    "product_depth", "result_bucket", "date_listed",
]


def main():
    storage.init_db()
    rows = storage.all_listings()
    if not rows:
        print("No listings in the database yet. Browse some pages first "
              "(the receiver stores them), then run this.")
        return

    print(f"Scoring {len(rows)} listings with location data "
          f"(free OpenStreetMap, rate-limited)...\n")

    geocoded = 0
    for i, row in enumerate(rows, 1):
        rec = {k: row.get(k) for k in _REC_FIELDS}
        loc = location.compute_location(rec)
        if loc.get("coords"):
            geocoded += 1
        rec["_coords"] = loc.get("coords")
        score = scoring.score_listing(rec, loc)
        storage.upsert_listing(rec, score)
        if i % 5 == 0 or i == len(rows):
            print(f"  ...{i}/{len(rows)} done")

    tally = storage.counts()
    print()
    print("=" * 60)
    print(f"  Done. Geocoded {geocoded}/{len(rows)}.")
    print(f"  Database: {tally['total']} listings, "
          f"{tally['alive']} alive after gates.")
    print("  Open the dashboard to see your ranked shortlist.")
    print("=" * 60)


if __name__ == "__main__":
    main()
