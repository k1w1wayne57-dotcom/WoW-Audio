# WoW Audio — project rules

Extends `../CLAUDE.md`. Vintage audio reference DB: Sansui, Marantz, Pioneer.

## Pricing

- **Prefer Wayne's own HiFi Shark exports over live scraping.** His exports are region-filtered, sold prices, and cover the whole brand. Use them.
- **Never price from Japanese or Hong Kong sellers.** Export-optimistic, shipping included, and they dominate JDM results. Enforced by `is_export_seller()` in `scripts/scrape.py`.
- Prices are **listing/asking medians, not confirmed sales.** `price_basis` must say so.
- JDM models often have no clean US/EU figure. Leave it blank.
- `MIN_LISTINGS = 1` — for oddballs a thin figure honestly flagged beats none; `auto_price.n` records how thin.
- Coherence guard uses quartile ratio q3/q1 (≤5), applied only at n≥4.

## scrape.py — bugs already fixed, don't regress

- Multi-char currency prefixes **must** precede bare `$` in `PRICE_RE`. `HK$` read as USD made every Hong Kong listing ~8× too dear.
- Junk filter catches `board`, `terminal`, `kit`, `instruction`, `anleitung`, `lamp`. But `parts`/`repair` only in their junk senses — bare `parts` discarded a $1,500 complete amp reading "Vintage Original Parts".
- Model matching joins up to 4 adjacent title tokens; sellers write "BA 5000" as often as "BA-5000".
- `VARIANT_SUFFIX` rejects different models (MR/XR/KX/DR/NRA/MOS/Limited/Extra/II). **"vintage" is not a variant marker** — it's a stock word in these titles.
- Alpha models: search **without** the word "Alpha" (`AU-607NRA`). See `search_term()`.

## Data

- `scripts/audit_db.py` — read-only integrity check. Run before committing data changes. Exits 1 on any HIGH finding.
- Sources: Audio Database (specs, structured spec table), HiFi Engine (blocked to automation — Wayne pastes it), Classic Receivers, the Audiokarma product history.
- `norm_model()` in `backfill_specs.py` is the shared key. It folds `AU-AL607` / `AU-α607` / `AU-a607` / `AU-Alpha-607`.
- Faceplate photos outrank published sources. Two DB errors were caught that way (Black Era, Twin Diamond Balanced Drive).
- **`year_source: "serial-report"` means `Service manuals/02 Sansui Serial Number Report.pdf`** — 425 models, decodable with PyMuPDF. Sansui serials encode the date: digits 1–2 assembly line, digit 3 the year (decade from the model), digits 4–5 the month, so `838040898` is April 1978.
- **Take the first year of *volume* production, never the earliest serial.** Single-unit years are mis-keyed serials — one stray 1975 among 234 AU-317s had dated that model 1975. Count units per year and use the first substantial one. This also beats the Audiokarma product history, which lists the AU-417 twice at two different years.
- **`series` holds the generation heading, not an era.** It mirrors the headings in `sansui_history.json` (`generations`), which the timeline renders. Faceplate colour is *not* a generation: the silver tag belongs to receivers only, the black-face tag to 1st/2nd Gen 07 plus the x17 juniors, and it lives in `sonic_signature`. Numeric models group by the **shape** of the number, not its size — AU-999 sits with AU-777, not AU-9900. Claim the specific shapes (`\d900`, `[6-9]500`) before the general `\d{2}00`, or the greedy rule swallows the other waves.
- **`circuit_family` drives the family sonic text**, not the faceplate: Classic solid-state (capacitor-coupled), DC integrated, Diamond Differential, Super Feedforward, Pure Power DC, X-Balanced/α-X Balanced, Tube. Where the circuit is unsourced, leave both blank.
- **`collector_ranking` bands hold ten each** (50 ranked, rest Unranked), ordered on `avg_price_usd_3mo` with market twins sharing a slot. Rank across the whole catalogue, never within the existing band. Most top-50 prices are hand-entered (`auto_price.n` = 0) — treat the order as provisional.
- **Paired JDM/export records are not duplicates.** Seven Sansui amps hold two records each (AU-517/607, 717/707, 919/D907, 819/D707, 519/D607, D9/D707F, D55F/D33). Each stores its *own* name in `jdm_model` and its counterpart in `int_model` — the fields are not swapped, the naming is just misleading. **Differing weights are real:** the export unit carries a 240V transformer against the JDM 100V, and international models may also have had larger main caps, so the heavier of a pair is the export one. Never merge them or "correct" the weight to match.

## Wayne's gear and preferences

- **Owns:** B-2102 (1986 X-Balanced), AU-607, G-5700. Edit those with extra care; they carry hands-on notes.
- **Avoids any amp with a proprietary/obsolete output package** (e.g. Pioneer MT-100 — unobtainable, so a blown output stage is terminal). Flag it when recommending.
- **Avoids Super Feedforward** — oscillates readily. He fought an AU-D9 and AU-D55F over it.
- **Bargain hunter.** A large Thai-vs-world multiple matters more than prestige.
- B-2102 safety: X-Balanced, so **both speaker terminals are live**. Never bridge or ground either.
