"""
WoW Audio — one-time spec backfill from Audio Database (audio-database.com).

Fills ONLY blank factual fields on existing records, from the structured spec
table on each model's Audio Database page. Never overwrites data you already
have, and never touches judgment fields (sonic_signature, best_buy,
collector_ranking, ps_type, notes) — those stay yours.

Every record it fills is stamped with an `auto_specs` provenance block
(source + date + which fields) and left verified=False so you can spot-check.

    python scripts/backfill_specs.py                 # DRY RUN (writes nothing)
    python scripts/backfill_specs.py --brand sansui  # dry run, one brand
    python scripts/backfill_specs.py --apply         # actually write the JSON
    python scripts/backfill_specs.py --limit 15      # only first 15 (testing)

A dry run also writes a review file: scripts/backfill_review.tsv
(open in Excel) — every proposed change, source URL included.

Fetches are cached under the scratchpad so a dry-run then --apply won't
re-hit the site.
"""

import re
import sys
import json
import time
import argparse
import datetime
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Need beautifulsoup4:  py -m pip install beautifulsoup4")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = Path(__file__).resolve().parent / ".adb_cache"
CACHE.mkdir(exist_ok=True)
UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")}
BRANDS = {"sansui": "SANSUI", "marantz": "MARANTZ", "pioneer": "PIONEER"}
# Audio Database's own section paths per brand (Pioneer lives under PIONEER-EXCLUSIVE).
ADB_PATHS = {
    "sansui":  [("SANSUI", "amp"), ("SANSUI", "tuner")],
    "marantz": [("MARANTZ", "amp"), ("MARANTZ", "receiver"), ("MARANTZ", "tuner")],
    "pioneer": [("PIONEER-EXCLUSIVE", "amp"), ("PIONEER-EXCLUSIVE", "tuner"),
                ("PIONEER", "amp")],
}
TODAY = f"{datetime.date.today():%Y-%m}"


def norm_model(s):
    """AU-717 / au-717 / 'AU 717' -> 'au717' for matching DB models to adb slugs.

    Sansui's Alpha series is written every which way — 'AU-α607MR' on listings,
    'AU-Alpha-607MR' in this DB, sometimes 'AU-a607MR' — so the alpha glyph and
    the bare 'a' prefix are both folded to 'alpha' before stripping.
    """
    s = str(s).lower().replace("α", "alpha").replace("Α", "alpha")
    s = re.sub(r"\bau[\s-]*a(?=\d)", "aualpha", s)     # AU-a607 -> AU-alpha607
    s = re.sub(r"[^a-z0-9]", "", s)
    # Sellers often drop the alpha entirely ("Au-907mr"). No plain AU-607/707/907
    # ever carried an MR/DR/KX/XR/NRA suffix, so those are unambiguously Alpha.
    s = re.sub(r"^au([679]07)(mr|mrx|dr|kx|xr|nra)", r"aualpha\1\2", s)
    return s

# Factual fields we may fill (blank-only). Judgment fields are deliberately absent.
YEN = r"[¥￥]"


# ---------------------------------------------------------------------------
# Fetch (cached)
# ---------------------------------------------------------------------------
def fetch(url):
    key = CACHE / (hashlib.md5(url.encode()).hexdigest() + ".html")
    if key.exists():
        return key.read_text(encoding="utf-8", errors="replace")
    try:
        req = urllib.request.Request(url, headers=UA)
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None
    key.write_text(html, encoding="utf-8")
    time.sleep(0.6)  # be polite
    return html


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------
def spec_rows(soup):
    rows = []
    tab = soup.find("table")
    if not tab:
        return rows
    for tr in tab.find_all("tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
        if len(tds) >= 2 and tds[0] and tds[1]:
            rows.append((tds[0], tds[1]))
    return rows


def parse_price_year(soup):
    """Header looks like: 'SANSUI AU-777 ¥57,000 (released in May 1967) ...'"""
    head = soup.get_text(" ", strip=True)[:400]
    price = year = None
    m = re.search(YEN + r"\s?([\d,]{4,})", head)
    if m:
        try:
            price = round(int(m.group(1).replace(",", "")) / 1000)  # -> k-yen
        except ValueError:
            pass
    m = re.search(r"\b(19\d{2}|20\d{2})\b", head)
    if m:
        year = int(m.group(1))
    return price, year


def parse_watts(rows):
    """First continuous/rated per-channel output. Skip music/peak/practical-max."""
    best = None
    prio = [("rated", 0), ("continuous", 1), ("rms", 1), ("effective power", 2),
            ("effective output", 3)]
    for lab, val in rows:
        low = lab.lower()
        if "music" in low or "practical maximum" in low or "peak" in low:
            continue
        rank = next((p for key, p in prio if key in low), None)
        if rank is None:
            if not re.search(r"\b(output|power)\b", low):
                continue
            rank = 5
        # per-channel figure: '30W + 30W', '30W/30W', '30 W x 2'
        m = re.search(r"(\d+(?:\.\d+)?)\s*W\s*(?:\+|/|x|×|,|\s)\s*\d", val)
        if not m:
            m = re.search(r"(\d+(?:\.\d+)?)\s*W", val)
        if m:
            w = float(m.group(1))
            if w.is_integer():
                w = int(w)
            if best is None or rank < best[0]:
                best = (rank, w)
    return best[1] if best else None


def parse_thd(rows):
    for lab, val in rows:
        if re.search(r"harmonic distortion", lab, re.I):
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", val)
            if m:
                return float(m.group(1))
    return None


UNIT = {"hz": 1, "khz": 1000, "mhz": 1_000_000}


def _to_hz(num, unit):
    if num.upper() == "DC":
        return "DC"
    return int(round(float(num) * UNIT.get((unit or "hz").lower(), 1)))


def parse_freq(rows):
    """First 'Frequency characteristic' row -> 'LOW-HIGH' in Hz (or 'DC-...')."""
    for lab, val in rows:
        if re.search(r"frequency", lab, re.I):
            m = re.search(r"(DC|\d+(?:\.\d+)?)\s*(Hz|kHz|MHz)?\s*(?:~|–|−|-|to)\s*"
                          r"(\d+(?:\.\d+)?)\s*(Hz|kHz|MHz)", val, re.I)
            if m:
                lo = _to_hz(m.group(1), m.group(2) or (m.group(4)))
                hi = _to_hz(m.group(3), m.group(4))
                return f"{lo}-{hi}"
    return None


def parse_weight(rows):
    for lab, val in rows:
        if re.fullmatch(r"weight", lab.strip(), re.I) or lab.strip().lower() == "weight":
            m = re.search(r"(\d+(?:\.\d+)?)\s*kg", val, re.I)
            if m:
                return float(m.group(1))
    # fallback: any row whose label starts with Weight
    for lab, val in rows:
        if lab.strip().lower().startswith("weight"):
            m = re.search(r"(\d+(?:\.\d+)?)\s*kg", val, re.I)
            if m:
                return float(m.group(1))
    return None


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = spec_rows(soup)
    if not rows:
        return None
    price, year = parse_price_year(soup)
    return {
        "watts_per_channel": parse_watts(rows),
        "thd_percent": parse_thd(rows),
        "freq_response_hz": parse_freq(rows),
        "weight_kg": parse_weight(rows),
        "japan_price_kyen": price,
        "year_start": year,
    }


# ---------------------------------------------------------------------------
# DB helpers (preserve BOM + line endings, like scrape.py)
# ---------------------------------------------------------------------------
def load_db(brand):
    path = DATA / f"{brand}.json"
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    return json.loads(text), {"path": path, "bom": has_bom, "crlf": crlf}


def save_db(data, meta):
    s = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if meta["crlf"]:
        s = s.replace("\n", "\r\n")
    enc = s.encode("utf-8")
    if meta["bom"]:
        enc = b"\xef\xbb\xbf" + enc
    meta["path"].write_bytes(enc)


EMPTY = (None, "", "—", [], {})
FILLABLE = ["watts_per_channel", "thd_percent", "freq_response_hz",
            "weight_kg", "japan_price_kyen", "year_start"]

# Type-gating: a tuner's "frequency" is the FM band, a preamp/tuner has no
# watts/channel, a tape deck/reverb isn't an amplifier. Only fill fields that
# make physical sense for the record's type.
AMP_TYPES = {"Integrated", "Power Amp", "Power Amp 4-ch", "Receiver",
             "Receiver 4-ch", "Tube Integrated", "Tube Receiver"}
PRE_OK = AMP_TYPES | {"Preamp"}   # types that legitimately have audio THD / freq


def _freq_sane(s):
    m = re.match(r"(DC|\d+)-(\d+)$", str(s))
    if not m:
        return False
    lo = 0 if m.group(1) == "DC" else int(m.group(1))
    hi = int(m.group(2))
    return lo <= 2000 and 8000 <= hi <= 5_000_000   # rejects FM band (76-90 MHz)


def sane(field, val, rtype):
    """Second safety net: right type + plausible magnitude."""
    if val in EMPTY:
        return False
    if field == "watts_per_channel":
        return rtype in AMP_TYPES and isinstance(val, (int, float)) and 1 <= val <= 2000
    if field == "thd_percent":
        return rtype in PRE_OK and 0.0001 <= val <= 10
    if field == "freq_response_hz":
        return rtype in PRE_OK and _freq_sane(val)
    if field == "weight_kg":
        return 0.5 <= val <= 120
    if field == "japan_price_kyen":
        return 1 <= val <= 5000
    if field == "year_start":
        return 1948 <= val <= 2010
    return True


def build_index(brand):
    """Scrape adb's section index pages -> {norm_model: full_url}. English
    (-e) pages win over the Japanese page when both exist for a model."""
    idx = {}
    for br, sec in ADB_PATHS[brand]:
        base = f"https://audio-database.com/{br}/{sec}/"
        html = fetch(base)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href") or ""
            if not href.endswith(".html") or "index" in href:
                continue
            slug = href.split("/")[-1][:-5]           # drop .html
            is_en = slug.endswith("-e")
            model = norm_model(re.sub(r"-e$", "", slug))
            model = re.sub(r"vintage.*", "", model)
            if not model:
                continue
            url = base + href if not href.startswith("http") else href
            if model not in idx or (is_en and "-e.html" not in idx[model]):
                idx[model] = url
    return idx


def adb_url(rec, brand, index):
    link = (rec.get("links") or {}).get("audio_database")
    if link:
        return link, True
    model = norm_model(rec.get("jdm_model") or rec.get("model") or "")
    if model and model in index:
        return index[model], False
    return None, False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(brands, apply, limit):
    review = ["\t".join(["brand", "model", "field", "old", "new", "source_url"])]
    totals = {"records": 0, "pages_ok": 0, "pages_miss": 0, "fields_filled": 0,
              "records_touched": 0}
    for brand in brands:
        data, meta = load_db(brand)
        index = build_index(brand)
        print(f"  {brand}: adb index has {len(index)} models")
        recs = data if not limit else data[:limit]
        for rec in recs:
            totals["records"] += 1
            # skip if nothing fillable is empty
            gaps = [f for f in FILLABLE if rec.get(f) in EMPTY]
            if not gaps:
                continue
            url, had_link = adb_url(rec, brand, index)
            if not url:
                continue
            html = fetch(url)
            if not html:
                totals["pages_miss"] += 1
                continue
            specs = parse_page(html)
            if not specs:
                totals["pages_miss"] += 1
                continue
            totals["pages_ok"] += 1
            filled_here = []
            rtype = rec.get("type")
            for f in gaps:
                new = specs.get(f)
                if not sane(f, new, rtype):
                    continue
                review.append("\t".join([brand, str(rec.get("jdm_model") or rec.get("model")),
                                         f, str(rec.get(f)), str(new), url]))
                if apply:
                    rec[f] = new
                filled_here.append(f)
                totals["fields_filled"] += 1
            if filled_here:
                totals["records_touched"] += 1
                if apply:
                    # remember the adb link if we discovered it by construction
                    if not had_link:
                        rec.setdefault("links", {})["audio_database"] = url
                    rec["auto_specs"] = {"source": "audio-database.com",
                                         "date": TODAY, "fields": filled_here}
        if apply:
            save_db(data, meta)
            print(f"  wrote data/{brand}.json")

    (Path(__file__).resolve().parent / "backfill_review.tsv").write_text(
        "\n".join(review), encoding="utf-8")
    print()
    mode = "APPLIED" if apply else "DRY RUN (nothing written)"
    print(f"=== {mode} ===")
    for k, v in totals.items():
        print(f"  {k:16} {v}")
    print(f"  review file: scripts/backfill_review.tsv ({len(review)-1} proposed fills)")


def main():
    ap = argparse.ArgumentParser(description="Backfill specs from Audio Database.")
    ap.add_argument("--brand", choices=list(BRANDS), help="one brand (default: all)")
    ap.add_argument("--apply", action="store_true", help="write the JSON (default: dry run)")
    ap.add_argument("--limit", type=int, default=0, help="only first N records per brand")
    args = ap.parse_args()
    brands = [args.brand] if args.brand else list(BRANDS)
    run(brands, args.apply, args.limit)


if __name__ == "__main__":
    main()
