# =============================================================================
#  CONFIG  —  THE ONE PLACE TO CHANGE THINGS
# =============================================================================
#  Everything brittle or tweakable lives here, on purpose. If the website
#  changes or you want to adjust your criteria, you should only ever need to
#  edit THIS file. Each section is labelled in plain English.
#
#  You do NOT need to understand the code in the other files to use this.
# =============================================================================


# -----------------------------------------------------------------------------
#  1. SUBURBS TO SEARCH
# -----------------------------------------------------------------------------
#  Add or remove suburbs here. Format matters for the website's URL, so each
#  entry has the human name, the way the site writes it, and the postcode.
#  During the Step 1 spike we ONLY use the first one (Melbourne CBD).
# -----------------------------------------------------------------------------
SUBURBS = [
    # (display name,        site_slug,            postcode)
    ("Melbourne CBD",       "melbourne+cbd",      "3000"),   # <- spike starts here
    ("Southbank",           "southbank",          "3006"),
    ("Docklands",           "docklands",          "3008"),
    ("East Melbourne",      "east+melbourne",     "3002"),
    ("West Melbourne",      "west+melbourne",     "3003"),
    ("North Melbourne",     "north+melbourne",    "3051"),
    ("Carlton",             "carlton",            "3053"),
    ("Parkville",           "parkville",          "3052"),
    ("Fitzroy",             "fitzroy",            "3065"),
    ("Collingwood",         "collingwood",        "3066"),
    ("Richmond",            "richmond",           "3121"),
    ("Cremorne",            "cremorne",           "3121"),
    ("South Yarra",         "south+yarra",        "3141"),
    ("South Melbourne",     "south+melbourne",    "3205"),
    ("Port Melbourne",      "port+melbourne",     "3207"),
    ("Albert Park",         "albert+park",        "3206"),
    ("St Kilda",            "st+kilda",           "3182"),
    ("Prahran",             "prahran",            "3181"),
]

# How many result pages to fetch per suburb (each page ~20-25 listings).
# Keep this low. We are a polite, low-volume scraper.
MAX_PAGES_PER_SUBURB = 2


# -----------------------------------------------------------------------------
#  2. SEARCH FILTERS
# -----------------------------------------------------------------------------
#  Bedroom counts we care about. 2BR is intentionally excluded (off-target),
#  but the scraper still fetches everything in a suburb and the SCORING step
#  is what flags 2BR — so we keep the data and let the rules decide.
# -----------------------------------------------------------------------------
PROPERTY_TYPES = ["apartment", "unit", "townhouse"]  # site's property categories


# -----------------------------------------------------------------------------
#  3. YOUR ACQUISITION CRITERIA  (the two-layer scoring system)
# -----------------------------------------------------------------------------
#  LAYER 1 = hard gates (pass/fail). LAYER 2 = weighted 0-100 score made of
#  five components (A standout 30, B location 25, C amenities 20, D interior 15,
#  E pricing 10). Verdict: >=70 Pursue, 50-69 Inspect, <50 Pass.
# -----------------------------------------------------------------------------

# Component weights (must sum to 100) — kept here so you can re-balance easily.
COMPONENT_WEIGHTS = {"A_standout": 30, "B_location": 25, "C_amenities": 20,
                     "D_interior": 15, "E_pricing": 10}

# ----- COMPONENT A: STANDOUT / CHARACTER (30 pts, the decisive filter) -----
# Hooks found in description/features. Points per spec; hooks STACK; cap 30.
# A listing scoring 0 here FAILS Gate G3 (no hook = generic = reject).
# Each entry: matched phrases -> points. First matching phrase in a group
# awards that group's points once.
STANDOUT_HOOKS = [
    (["penthouse"],                                              12),
    (["loft"],                                                   11),
    (["two-storey", "two storey", "two-level", "two level",
      "multi-level", "multi level", "split level", "split-level",
      "tri-level", "double storey"],                            10),
    (["sauna", "steam room"],                                    9),
    (["heritage", "warehouse conversion", "warehouse-conversion",
      "character", "architect", "designer", "art deco",
      "period features"],                                        8),
    (["private rooftop", "rooftop terrace", "atrium",
      "mezzanine", "wine cellar"],                               5),
]
STANDOUT_CAP = 30

# ----- COMPONENT C: AMENITIES & EXTRAS (20 pts, guide's priority order) -----
# Car park comes from structured data (parkingSpaces). The rest are scanned
# in the description text (REA has no structured amenity list in the feed).
AMENITY_POINTS = {
    "car_park":  10,   # P1 — highest; absence raises a "NO PARKING" flag
    "pool":       4,   # P2
    "gym":        4,   # P2
    "furnished":  2,   # P3
}
AMENITY_CAP = 20
POOL_KEYWORDS      = ["pool", "lap pool", "swimming"]
GYM_KEYWORDS       = ["gym", "fitness", "fully equipped gym"]
FURNISHED_KEYWORDS = ["furnished", "fully furnished"]

# ----- COMPONENT D: INTERIOR & SPACE (15 pts; mostly human-confirmed) -----
# We infer what we can from text; the rest gets a VERIFY badge for inspection.
INTERIOR_ADD_BEDROOM_KEYWORDS = ["study", "convertible", "flexi", "can add",
                                 "additional bedroom", "extra bedroom",
                                 "potential to", "multi-purpose room"]   # 6
INTERIOR_SPACIOUS_KEYWORDS    = ["spacious", "generous", "large living",
                                 "expansive", "oversized"]               # 4
INTERIOR_LIGHT_KEYWORDS       = ["natural light", "light-filled", "light filled",
                                 "floor-to-ceiling", "floor to ceiling",
                                 "north-facing", "north facing", "sun-drenched"] # 3
INTERIOR_OPEN_KEYWORDS        = ["open plan", "open-plan", "open space",
                                 "free-flowing", "seamless flow"]        # 2
INTERIOR_CAP = 15

# ----- COMPONENT E: PRICING FIT (10 pts) -----
# Bands: (low, high). high=None means "floor only" (4+BR). Above-band needs
# the premium test (>= PREMIUM_TICKS_REQUIRED ticks) to score 6, else 0+flag.
RENT_BANDS = {
    1: (500, 750),     # widened from 400-500 to reflect real CBD 1BR pricing
    3: (1100, 1400),
    4: (1750, None),
}
PREMIUM_TICKS_REQUIRED = 3   # of: distinctive design, premium amenities,
                             # exceptional location, scope to add bedroom, car park

# ----- GATES -----
TARGET_BEDROOMS    = [1, 3, 4]   # 4 means 4+
OFFTARGET_BEDROOMS = [2]         # 2BR / studio -> Reject (G1)
G5_1BR_LOCATION_MIN = 70         # 1BR must score >= 70/100 on location (G5)

# ----- COMPONENT B: LOCATION (25 pts; built in sub-step 3b with geocoding) -----
# "Right area for property type" mapping (suburb suits these hook types).
RIGHT_AREA_FOR_TYPE = {
    "loft":      ["Richmond", "St Kilda", "North Melbourne", "Cremorne",
                  "Collingwood", "Fitzroy"],
    "penthouse": ["Melbourne", "Southbank", "South Yarra", "Docklands"],
    "heritage":  ["St Kilda", "South Yarra", "Fitzroy", "East Melbourne",
                  "Carlton"],
}
# Suburbs considered within the inner->outer Melbourne band for Gate G2.
# (Defaults to the configured SUBURBS list; edit if you widen the net.)
LOCATION_BAND_POSTCODES = [pc for (_n, _s, pc) in SUBURBS]


# -----------------------------------------------------------------------------
#  4. POLITE SCRAPER SETTINGS  (do not make these aggressive)
# -----------------------------------------------------------------------------
#  We deliberately keep volume LOW to avoid being blocked.
# -----------------------------------------------------------------------------
DELAY_MIN_SECONDS = 3      # random wait between requests: low end
DELAY_MAX_SECONDS = 5      # random wait between requests: high end
MAX_RETRIES       = 2      # gentle. NEVER a retry storm.
PAGE_TIMEOUT_MS   = 45000  # how long to wait for a page before giving up

# A realistic, current desktop browser identity.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Respect the site's robots.txt rules.
RESPECT_ROBOTS_TXT = True

# Contact email sent to the free OpenStreetMap geocoder (politeness, not
# required). Put your own email here so they can reach you if needed.
NOMINATIM_CONTACT_EMAIL = "you@example.com"


# -----------------------------------------------------------------------------
#  5. WEBSITE STRUCTURE  (the brittle bits — fix here if the site changes)
# -----------------------------------------------------------------------------
#  These are the parts most likely to break if realestate.com.au changes.
#  We read the page's EMBEDDED JSON, not the visible HTML, because the JSON
#  is far more stable. The exact JSON location is confirmed during Step 1 and
#  filled in here once we've seen it.
# -----------------------------------------------------------------------------
BASE_URL = "https://www.realestate.com.au"

# Rent search URL template. {slug}, {postcode}, {page} get filled in.
# Confirmed/adjusted during the Step 1 spike.
SEARCH_URL_TEMPLATE = (
    "https://www.realestate.com.au/rent/in-{slug},+vic+{postcode}/list-{page}"
)

# The <script> tags that hold the embedded JSON. We try these in order.
# (Legacy from the spike; REA actually uses ArgonautExchange below.)
JSON_SCRIPT_IDS = [
    "__NEXT_DATA__",          # Next.js standard location
    "__INITIAL_STATE__",      # common alternative
]

# -- How realestate.com.au actually stores its listing data (confirmed live) --
# The page contains an inline script:  window.ArgonautExchange = { ... }
# Inside it, a urql GraphQL cache holds the search results. The data is
# JSON-encoded inside JSON (strings within strings), so we decode in stages.
# If REA changes their structure, these are the knobs to turn.
ARGONAUT_MARKER     = "window.ArgonautExchange="
ARGONAUT_APP_KEY    = "resi-property_listing-experience-web"
ARGONAUT_CACHE_KEY  = "urqlClientCache"
SEARCH_ROOT_KEYS    = ["rentSearch", "buySearch"]   # we use rentSearch
RESULT_BUCKETS      = ["exact", "surrounding"]       # "exact" = in-suburb

# Where each field sits INSIDE one listing object. Each value is a path;
# lists mean "dig through these nested keys". This is the brittle bit —
# if a field stops importing, fix its path here.
LISTING_FIELD_PATHS = {
    "listing_id":     ["id"],
    "url":            ["_links", "canonical", "href"],
    "suburb":         ["address", "suburb"],
    "address":        ["address", "display", "fullAddress"],
    "postcode":       ["address", "postcode"],
    "price_display":  ["price", "display"],            # "$880 per week"
    "bedrooms":       ["generalFeatures", "bedrooms", "value"],
    "bathrooms":      ["generalFeatures", "bathrooms", "value"],
    "parking":        ["generalFeatures", "parkingSpaces", "value"],
    "property_type":  ["propertyType", "display"],
    "description":    ["description"],
    "agency":         ["listingCompany", "name"],
    "bond_display":   ["bond", "display"],
    "available_date": ["availableDate", "display"],
}
