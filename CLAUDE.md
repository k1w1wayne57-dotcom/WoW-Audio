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

## Wayne's gear and preferences

- **Owns:** B-2102 (1986 X-Balanced), AU-607, G-5700, B-7000. Edit those with extra care; they carry hands-on notes.
- **Avoids any amp with a proprietary/obsolete output package** (e.g. Pioneer MT-100 — unobtainable, so a blown output stage is terminal). Flag it when recommending.
- **Avoids Super Feedforward** — oscillates readily. He fought an AU-D9 and AU-D55F over it.
- **Bargain hunter.** A large Thai-vs-world multiple matters more than prestige.
- B-2102 safety: X-Balanced, so **both speaker terminals are live**. Never bridge or ground either.
