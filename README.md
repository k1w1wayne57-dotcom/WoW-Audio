# WoW Audio — World of Wayne

A personal reference database and website documenting Sansui amplifiers, receivers, tuners, tape decks
and related equipment from 1954 to 1987, plus selected post-1987 Alpha series models for the Japanese
domestic market (JDM). Built for personal research and second-hand market analysis.

Live site: https://k1w1wayne57.github.io/wow-audio

## Project structure

```
wow-audio/
├── index.html          # Main website
├── style.css            # Dark gold premium theme
├── app.js               # Sort / filter / search / modal logic (vanilla JS, no frameworks)
├── data/
│   └── sansui.json      # Master database — 260 models
├── scripts/
│   └── research.py      # Price research helper (HiFi Shark lookups)
├── images/               # Model photos (placeholder)
└── README.md
```

## Database

`data/sansui.json` follows a fixed schema per model — see the field comments in the file itself, or the
project notes. Key points:

- `verified: false` on every entry until manually confirmed by Wayne.
- Unknown fields are `null`, never guessed.
- `avg_price_usd_1yr` — researched current single-year USD market estimate (low confidence, aggregate).
- `price_thb_listings` — array of Wayne's own second-hand Thai market finds (each number is one listing, in Baht). Never averaged; the site shows every listing. Not auto-researched. Edit with `scripts/set_thb.py`.
- `japan_price_kyen` — original Japan list price in thousands of yen, where known.
- `ps_type` — power-supply topology, only when explicitly documented (never inferred from marketing copy). Values: `"Dual Mono"` = separate transformer per channel / documented dual-mono power-amp topology (e.g. AU-517/717/519/719, AU-D907/D907X); `"Dual Power Supply"` = independent rails/windings & rectifiers but not per-channel-isolated (e.g. the α907 ladder, the big G-series receivers); `"Penta-Power (dual transformer, stage-split)"` = Sansui's AU-919 design — two transformers split by stage (power vs. preamp), not by channel, so NOT dual mono. `null` = plain single supply or undocumented.
- `collector_ranking` — Top 10 / Top 10-20 / Top 20-30 / Top 30-40 / Top 40-50 / Unranked. JDM/export twins share the same rank (same amp).
- `sonic_signature` — how the model actually sounds, from owner/reviewer consensus. Shown as its own section on the detail page. Only set where sourced; twins share it.
- `amp_circuit` — short circuit label (shown in the table's Circuit column). `circuit_description` — the full topology write-up (power stage, differential/diamond circuits, supply arrangement), shown as its own section on the detail page.
- `restorer_info.recap_difficulty` — 1 (beginner) to 5 (expert/dangerous).

## Running locally

The site fetches `data/sansui.json` via `fetch()`, which browsers block on `file://` URLs. Serve the folder
over HTTP instead, e.g. with any static file server, then open `http://localhost:<port>/index.html`.

## Editing models on the fly (local admin server)

`serve.py` is a small local-only Flask server (binds to `127.0.0.1`, never exposed). It serves the existing
static site **and** a write API, so you can add/update models from the browser instead of hand-editing JSON:

```
python -m pip install -r requirements.txt
python serve.py
```

Then open `http://127.0.0.1:8137/admin.html`. Pick a brand, choose an existing model to edit (or leave it on
"— new model —"), fill the form, and **Save** — it writes straight into `data/<brand>.json`, preserving each
file's exact line endings and BOM so the git diff stays clean. `index.html` and the public GitHub Pages site
are untouched (they stay a static, read-only copy). After editing, `git commit && git push` to publish.

Notes:
- New records start from a canonical template, so every field exists; edits deep-merge, so untouched fields
  (e.g. `capacitors`) are preserved.
- IDs auto-generate as `<brand>-<model>-<year>` when left blank; existing IDs are immutable.

## Web scraper

`scripts/scrape.py` (Playwright + BeautifulSoup) drives a headless Chromium — see its docstring. HiFi Shark
price research with `--update` into the brand JSON:

```
python scripts/scrape.py --brand marantz --model 2285B --months 3 --update
```

Cloudflare-walled sites (usaudiomart, canuckaudiomart, eBay) need `--headful --profile <dir>` (clear the
challenge yourself once) or an official API. Requires `python -m playwright install chromium`.

## Research helper script

```
python scripts/research.py "AU-111"
python scripts/research.py all
```

Looks up completed/active HiFi Shark listings for a model (or every model), reports average price, listing
count, date range, lowest and highest, and can optionally write the results back into `sansui.json` along
with a timestamp. Requires Python 3 — not installed on this machine at time of writing; install Python
before running.

## Phase 2 (not yet built)

- Full capacitor list per model with supplier links and a "Generate Cap Order List" export
- Price trend graphs
- Service manual PDF links
- Multi-brand expansion (Pioneer, Marantz, Luxman, etc.)

## Status

Personal project, not affiliated with Sansui Electric Co. Data sourced from audio-database.com, HiFi Engine,
sansui.us, AudioKarma, period dealer price lists, and Wayne's own market research.
