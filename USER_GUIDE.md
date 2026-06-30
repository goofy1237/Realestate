# LuxeBot — User Guide (read me first)

This guide assumes **zero technical knowledge**. Follow it top to bottom the
first time. Every click is spelled out. If something looks stuck, the most
common answer is **"it's working — wait"** (see the ⏳ warnings).

**What this tool does, in one sentence:** you browse Melbourne rentals on
realestate.com.au like normal, and LuxeBot captures, scores, and ranks them into
a daily shortlist you can act on.

---

## ⏳ The single most important thing to know

Two steps in this guide are **slow**, and your computer will look like it has
**frozen or crashed**. It hasn't. **Do not close the window. Do not click again.
Just wait.** These are:

- **Setup Step 2** (installing the tool's parts) — can take **2–10 minutes**, and
  the window may show nothing happening for long stretches.
- **Daily Step 2** ("Score now") — can take **1–3 minutes** the first time, and
  longer if you captured a lot of listings.

If you wait, they finish on their own. If you close the window early, you just
have to start that step again. **Patience here saves you headaches.**

---

# PART 1 — First-time setup (do this once)

You do all of Part 1 **one time only**. After that, daily use is just Part 2.

## Step 1 — Install Python  ⏳ (a few minutes)

Python is the engine LuxeBot runs on. If you're not sure whether you have it,
just do this — installing it again is harmless.

1. Go to **<https://www.python.org/downloads/>**
2. Click the big yellow **Download Python** button.
3. Open the file that downloads (bottom of your browser).
4. **VERY IMPORTANT:** on the first screen of the installer, tick the box at the
   bottom that says **"Add python.exe to PATH"**. ✅ (Easy to miss — don't.)
5. Click **Install Now**.
6. ⏳ **Wait** for it to finish — it can take a few minutes and the bar may sit
   still for a while. When it says **"Setup was successful"**, click **Close**.

## Step 2 — Install the tool's parts  ⏳⏳ (THE SLOW ONE — 2–10 minutes)

1. Open the LuxeBot folder in File Explorer (the folder with `START_HERE` in it).
2. Click once in the **address bar** at the top (where the folder path is shown),
   type **`cmd`**, and press **Enter**. A **black window** opens.
3. Click into the black window, then **copy-paste these two lines one at a time**,
   pressing **Enter** after each:

   ```
   python -m venv .venv
   ```
   ```
   .venv\Scripts\pip install -r requirements.txt
   ```

4. ⏳⏳ **NOW WAIT. This is the slow step.** After the second line, the window may:
   - show lines scrolling slowly, **or**
   - **sit completely still for minutes showing nothing** — this is normal, it's
     downloading in the background.

   **Do NOT close the window. Do NOT press keys. Do NOT run it again.** It can
   take anywhere from 2 to 10 minutes depending on your internet. It's done when
   you see the normal prompt again (a line ending in `>` waiting for input).

5. When it's finished, you can close the black window. **You never have to do
   Step 2 again.**

> 😟 "It's been 5 minutes and nothing is happening — did it break?"
> Almost certainly **no**. Give it up to 10 minutes. Only if it's still frozen
> after that, close the window and run the second line again.

## Step 3 — Connect the shared database (Supabase)

This is what lets you and your coworker see the **same** listings. *(If you only
want it on your own computer, you can skip this — it'll use a local file instead.)*

1. Double-click **`setup_db.bat`**.
2. When it asks, **paste your Supabase connection string** and press **Enter**.
   (Your colleague or whoever set up Supabase gives you this string. It's the
   "Session pooler" URI with your password filled in.)
3. ⏳ Wait a few seconds. You want to see the word **SUCCESS**.
4. Done. You won't need to do this again on this computer.

## Step 4 — Install the browser extension (once)

This is the little helper that captures listings as you browse.

1. Open **Google Chrome**.
2. In the address bar type **`chrome://extensions`** and press **Enter**.
3. Top-right, turn **ON** the **Developer mode** switch.
4. Top-left, click **Load unpacked**.
5. A file picker opens. Navigate into the LuxeBot folder and select the
   **`extension`** folder (click it once so it's highlighted, then **Select
   Folder**). Don't go *inside* the folder — just select it.
6. You should now see a card called **"Liveluxe REA Capture"**. ✅ That's it.

**Setup complete.** From now on you only ever do Part 2.

---

# PART 2 — Daily use (the Portal)

## Open the Portal

1. Double-click **`START_HERE.bat`**.
2. Two things appear:
   - A small **black/console window** that says **">>> KEEP THIS WINDOW OPEN
     <<<"**. ⚠️ **Leave it open** the whole time you're working. It *is* the tool
     running. Closing it turns LuxeBot off.
   - The **Portal window** — your dashboard.
3. ⏳ If the Portal window is briefly blank or says "connecting", **wait ~5–10
   seconds** and it'll load. (If Windows SmartScreen warns you, click **More
   info → Run anyway** — it's your own file.)

## Daily Step 1 — Capture listings  ⏳ (as long as you browse)

1. In the Portal, click **🌐 Open realestate.com.au**. Your normal browser opens
   to Melbourne CBD rentals.
2. Browse the suburbs/filters you want. **Every results page you open is captured
   automatically.** You don't click anything to "save" — it just happens.
3. **Hands-free option:** click the extensions (puzzle-piece) icon → **Liveluxe
   REA Capture** → tick **Auto-advance through pages**, set how many pages to stop
   after. Now it pages through results by itself.
   - ⏳ **Auto-advance is deliberately slow** — it waits **3–5 seconds between
     pages** so the website is treated politely. Going through 10 pages takes a
     minute or two. **This slowness is on purpose. Let it run.**
4. If the website shows a **"checking your browser"** screen, that's normal —
   wait a few seconds for it to pass, exactly like normal browsing.

## Daily Step 2 — Score the listings  ⏳⏳ (1–3 minutes — WAIT)

1. Back in the Portal, click **📍 Score now**.
2. An orange **"⏳ Scoring…"** bar appears at the top.
3. ⏳⏳ **NOW WAIT. This is the other slow step.** It looks up the location of
   every new listing (transport, hotels, hospitals nearby) using a free service
   that we deliberately use **gently**, so it takes time:
   - First run, or after capturing lots of listings: **1–3 minutes** (sometimes
     more). The orange bar stays up the whole time.
   - **Do NOT close the Portal. Do NOT click Score now again.** When it's done,
     the page **refreshes itself** automatically and the bar disappears.

> 😟 "The orange bar has been there for two minutes — is it stuck?"
> No — location lookups are slow on purpose. Give it a few minutes. It will
> refresh by itself when finished.

## Daily Step 3 — Review your shortlist

Now the fun part — no waiting here.

- Listings are ranked **best first** by their score.
- Use the **filter bar**:
  - **Today** — only listings added today.
  - **Last 7 days** — the past week.
  - **from / to + Apply range** — any custom date range.
  - **Sort** — by Score (best first) or Date added (newest first).
- Each listing shows its **score breakdown**, a suggested **verdict**
  (Pursue / Inspect / Pass), any **flags** (e.g. `NO PARKING`), and a **🗓 Added**
  date.
- Edit anything — **it saves instantly** (no save button):
  - **Your verdict** (override the suggestion)
  - **Stage** (first-contact → … → negotiate)
  - **Follow-up date** (leads due today jump to the top)
  - **Notes**
- **Export to Excel:** click **⬇ Export shortlist** (alive only) or **⬇ Export
  all**. It respects your date filter, so you can export, say, just today's leads.

## When you're finished

Close the **Portal window**, then close the small **console window** (or press
**Ctrl+C** in it). That turns LuxeBot off until next time.

---

# PART 3 — Good to know

- **No duplicates, ever.** If the same property is captured again, it just updates
  the existing entry — it never creates a copy. Its "Added" date stays as the
  first time you saw it.
- **Shared database.** Because you set up Supabase, you and your coworker see the
  same listings, scores, stages, follow-ups and notes — automatically.
- **A `*` next to a score** means it hasn't had location scoring yet. Click
  **Score now** to finish it.

---

# PART 4 — Changing your criteria (optional)

Everything tunable lives in **`config.py`**. Right-click it → **Open with →
Notepad**. Clearly labelled sections let you change suburbs, rent bands, the
standout keywords (the most important filter), and amenity weights. Save the file,
then click **Score now** in the Portal to apply the changes.

---

# PART 5 — Troubleshooting (plain answers)

**"The black setup window (Step 2) looks frozen."**
It's downloading. Wait up to 10 minutes. Only if still frozen after that, close it
and re-run the second line.

**"The Portal window says it can't connect."**
Look at the small console window — it must still be open and saying "KEEP THIS
WINDOW OPEN". If you closed it, just double-click `START_HERE.bat` again and wait
~10 seconds for the Portal to load.

**"Score now has been spinning forever."**
Location lookups are slow on purpose. Give it a few minutes — it refreshes itself
when done. Don't click it again while the orange bar is showing.

**"A page captured 0 listings."**
That's normal on non-results pages (a single property, the homepage). Open a
search-results page (rentals in a suburb).

**"Nothing happens when I double-click a `.bat` file."**
Make sure you finished Part 1 (the `.venv` folder must exist in the LuxeBot
folder). If Windows SmartScreen warns, choose **More info → Run anyway**.

**"Windows Smart App Control / Defender is BLOCKING `START_HERE.bat`."**
This happens when the files were downloaded from the internet (a GitHub ZIP),
which marks them "untrusted". Do **one** of these — do NOT turn off Smart App
Control (that's permanent and can't be undone without reinstalling Windows):

1. **Unblock the files.** Open the LuxeBot folder, click the address bar, type
   `powershell`, press Enter, then paste:
   ```
   Get-ChildItem -Recurse | Unblock-File
   ```
   Close it and try again. *(Or: right-click `START_HERE.bat` → Properties →
   tick **Unblock** → OK.)*
2. **Run it directly** (Python itself is trusted/signed). In the folder, type
   `cmd` in the address bar, Enter, then:
   ```
   .venv\Scripts\python.exe app.py
   ```
3. **Get it with Git instead of a ZIP** (cloned files aren't marked as
   downloaded): `git clone https://github.com/goofy1237/Realestate.git`

**"The database test failed."**
Re-run `setup_db.bat` and re-paste the connection string. Make sure you replaced
`[YOUR-PASSWORD]` (brackets and all) with your real password, and that you used
the **Session pooler** string.

**"I changed the extension / the code and it's behaving oddly."**
Go to `chrome://extensions` and click the **↻ reload** icon on the Liveluxe card.

---

# PART 6 — The 20-second daily cheat sheet

1. Double-click **`START_HERE.bat`** → keep the console window open.
2. Click **🌐 Open realestate.com.au** → browse (auto-advance optional).
3. Click **📍 Score now** → ⏳ **wait 1–3 min**, it refreshes itself.
4. Review, filter by date, edit verdicts/follow-ups, **Export to Excel**.
5. Close the Portal + console window when done.

---

# Privacy

Everything — captured listings, the database connection, your browser profile —
stays on your computer and your private Supabase database. None of it is in the
public code repository.
