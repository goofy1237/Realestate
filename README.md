# LuxeBot

A local, self-hosted tool that turns Melbourne rental listings into a **ranked,
scored shortlist** for property acquisition — with follow-up tracking and an
Excel export. Built for a buyer's agent focused on the Melbourne CBD and inner
suburbs.

It captures listing data from realestate.com.au **as you browse** (via a small
Chrome extension — no automated scraping), scores each listing against a
deterministic acquisition rubric, stores everything in a local database, and
shows it in a desktop dashboard.

> **Personal / educational use.** This tool reads listing data from pages **you**
> open in your own browser, at human speed. Respect realestate.com.au's Terms of
> Service and `robots.txt`, and keep volume low. No data leaves your computer.

---

## How it works

```
YOU browse realestate.com.au           (your real browser — nothing automated)
        │
        ▼
[Chrome extension]   reads the listing data embedded in each page
        │  sends to →
        ▼
[receiver.py]        local server (port 8765) — parses + scores + stores
        │
        ▼
[listings.db]  →  [score_all.py adds location]  →  [dashboard]  →  [Excel export]
```

Why a browser extension instead of a normal scraper? realestate.com.au is
protected by Kasada bot-defense, which blocks automated browsers. Capturing data
from pages you genuinely visit sidesteps that entirely and keeps things polite.

## The scoring (two layers)

- **Hard gates** (pass/fail): bedroom config (1/3/4+ only), location band,
  a required **standout hook**, short-stay permission, and a higher location bar
  for 1-bed properties.
- **Weighted 0–100 score**: Standout 30 · Location 25 · Amenities 20 ·
  Interior 15 · Pricing 10 → verdict **Pursue** (≥70) / **Inspect** (50–69) /
  **Pass** (<50).

All thresholds, suburbs, rent bands and keywords live in **`config.py`** — the
single place to tune behaviour.

---

## Setup (one time)

Requires **Python 3.10+** and **Google Chrome** (or Edge).

```bat
:: from the project folder
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Then load the browser extension once:

1. Open `chrome://extensions`
2. Turn on **Developer mode** (top-right)
3. Click **Load unpacked** and select the `extension` folder

See **[USER_GUIDE.md](USER_GUIDE.md)** for full, non-technical instructions.

## Daily use

Double-click **`START_HERE.bat`** — it starts the capture receiver, opens
realestate.com.au to browse, then (after you finish) scores everything and opens
the dashboard. Or run the steps individually:

| File | What it does |
|------|--------------|
| `START_HERE.bat`    | The whole loop: capture → score → dashboard |
| `run_receiver.bat`  | Capture only (browse REA with it running) |
| `run_score.bat`     | Add location scores / finalise verdicts |
| `run_dashboard.bat` | Open the dashboard app |

## Project layout

| File | Role |
|------|------|
| `config.py`     | All settings: suburbs, rent bands, scoring weights, keywords |
| `extension/`    | Chrome extension that captures listing data as you browse |
| `receiver.py`   | Local server that parses + scores + stores captures |
| `rea_parse.py`  | Extracts clean listings from REA's embedded data |
| `scoring.py`    | The two-layer gates + weighted scoring |
| `location.py` / `geocode.py` | Location scoring via free OpenStreetMap |
| `storage.py`    | Local SQLite database (dedupes on listing id) |
| `dashboard.py` / `dashboard_app.py` | Ranked dashboard + Excel export |
| `score_all.py`  | Batch location scoring pass |

## Notes

- Your data (the database, captured pages, browser profiles) stays local and is
  **not** committed — see `.gitignore`.
- Set your contact email in `config.py` (`NOMINATIM_CONTACT_EMAIL`) for the
  geocoder's politeness policy.
