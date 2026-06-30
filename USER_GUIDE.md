# LuxeBot — User Guide

A plain-English guide to setting up and using LuxeBot. No coding knowledge
needed. If you get stuck, the **Troubleshooting** section at the end covers the
common things.

---

## What this tool does

You browse Melbourne rental listings on realestate.com.au like normal. LuxeBot
quietly captures each listing, scores it against your acquisition criteria, and
gives you a **ranked shortlist** with a suggested verdict (Pursue / Inspect /
Pass), the 7 acquisition stages to track each lead, follow-up reminders, and an
Excel export.

Everything runs on your own computer. Nothing is uploaded anywhere.

---

## Part 1 — One-time setup (about 10 minutes)

You only do this once.

### 1. Install Python
If you don't already have it: download Python from
<https://www.python.org/downloads/> and install it. On the first screen of the
installer, **tick "Add Python to PATH"**, then click Install.

### 2. Set up the tool
Open the project folder (`luxebot`) in File Explorer. Click in the address bar,
type `cmd`, and press Enter — a black window opens in that folder. Paste these
two lines, pressing Enter after each:

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

When the second line finishes, setup is done. You can close the window.

### 3. Install the browser extension (once)
1. Open **Google Chrome**.
2. In the address bar type `chrome://extensions` and press Enter.
3. Turn **ON** the **Developer mode** switch (top-right corner).
4. Click **Load unpacked** (top-left).
5. Select the **`extension`** folder inside the project folder.
6. You should see a card titled **"Liveluxe REA Capture"**. Done.

> Optional: set your email in `config.py` (the line `NOMINATIM_CONTACT_EMAIL`).
> It's only used to be polite to the free map service. The tool works without it.

---

## Part 2 — Daily use

### Everything in one window: the Portal
Double-click **`START_HERE.bat`**. A single **Portal** window opens — you do
everything from here:

1. Click **🌐 Open realestate.com.au**. Browse the suburbs/pages you want — each
   page is captured automatically. (Turn on the extension's *Auto-advance* to
   page through results hands-free.)
2. Back in the Portal, click **📍 Score now**. It adds location scores in the
   background; the page refreshes itself when done.
3. Review your ranked shortlist right there.

That's it: open REA → score → review, all in one window. Close the window to stop.

### Filtering by date
Use the filter bar to see exactly what you want:
- **Today** — just today's newly-added listings.
- **Last 7 days** — the past week.
- **from / to** — pick any custom date range, then **Apply range**.
- **Sort** — by Score (best first) or Date added (newest first).

Every listing shows a **🗓 Added** date, and there are **never duplicates** — if
the same listing is captured again, it just updates in place.

### Auto-advance through pages (optional)
If you don't want to click "next page" yourself:

1. Click the **extensions icon** (puzzle piece) in Chrome → **Liveluxe REA Capture**.
2. Tick **Auto-advance through pages** and set how many pages to stop after.

Now, when you open a search, LuxeBot pages through the results on its own
(waiting a few seconds between pages), capturing each one.

### Doing the steps individually (optional)
- **`run_receiver.bat`** — start the catcher, then browse REA.
- **`run_score.bat`** — add location scores after browsing.
- **`run_dashboard.bat`** — open the dashboard.

---

## Part 3 — The dashboard

The dashboard opens as its own app window. Listings are ranked best-first by
their composite score.

For each listing you can see:
- The **composite score** and the five **sub-scores** (Standout, Location,
  Amenities, Interior, Pricing) — so you can see *why* it ranked where it did.
- The suggested **verdict** (Pursue / Inspect / Pass).
- **Flags** like `NO PARKING` or `OVER BAND`.
- A **VERIFY** badge for things only you can confirm (e.g. short-stay rules).

You can edit, and your changes save automatically:
- **Your verdict** — override the suggestion.
- **Stage** — move a lead through first-contact → application → suitability →
  lodge → follow-up → conduct → negotiate.
- **Follow-up date** — leads due today show at the top under "Follow-ups due".
- **Notes** — call notes, anything.

### Export to Excel
Two buttons at the top:
- **Export shortlist** — only the listings still alive after the gates.
- **Export all** — everything, including rejected.

The Excel file is formatted for reading: frozen header, colour-coded verdicts,
a score heat-scale, filters on every column, and clickable links to each listing.

---

## Part 3b — Sharing a database with a coworker (optional)

By default the tool keeps listings in a file on your own computer. If you want
you and a coworker to **share the same listings and scores**, point both of your
computers at one Supabase database.

1. In Supabase, click **Connect** (top bar) → choose **Session pooler** → copy
   the **URI**. (Use *Session pooler*, port **5432** — it works on all networks.
   Avoid "Transaction pooler" / port 6543.) Replace `[YOUR-PASSWORD]` with your
   database password.
2. Double-click **`setup_db.bat`**, paste the connection string when asked, and
   press Enter. It saves it privately and tests the connection for you.

   *(Manual alternative: copy `.env.example` to `.env`, paste your string after
   `SUPABASE_DB_URL=`, then run `run_db_test.bat`.)*

Give your coworker the same connection string (they put it in their own `.env`).
Now you both share one database. Your `.env` file is private and never leaves your
computer.

> If you skip this, everything still works — it just uses a local database only
> you can see.

---

## Part 4 — Changing your criteria

Everything tunable lives in **`config.py`** (open it in Notepad). Clearly
labelled sections let you change:

- **Suburbs** you search.
- **Rent bands** per bedroom count.
- **Standout keywords** and their points (the most important filter).
- **Amenity weights** (car park, pool, gym, furnished).
- **Scraper politeness** (the delay between pages).

Save the file, then re-run the scorer (`run_score.bat`) to apply changes.

---

## Troubleshooting

**The Receiver window says "could not reach the local tool".**
Make sure the Receiver is running (`START_HERE.bat` or `run_receiver.bat`) before
you browse.

**A page shows "0 listings found".**
That's normal on non-results pages (a single listing, the homepage). Open a
search-results page (e.g. rentals in a suburb).

**Listings show a `*` (provisional score).**
They haven't had location scoring yet. Run **`run_score.bat`** once.

**realestate.com.au shows a "checking your browser" screen.**
That's the site's normal human check — just wait a few seconds for it to pass,
as you would when browsing normally.

**The dashboard didn't pick up my latest browsing.**
Re-run **`run_score.bat`**, then refresh/reopen the dashboard.

**Nothing happens when I double-click a `.bat` file.**
Make sure you did the one-time setup in Part 1 (the `.venv` folder must exist).
If Windows SmartScreen warns, choose **More info → Run anyway** (it's your own file).

---

## Privacy

All your data — captured listings, the database, your browser profile — stays on
your computer and is never uploaded. (These files are deliberately excluded from
the code repository.)
