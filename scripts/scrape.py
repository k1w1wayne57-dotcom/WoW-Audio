"""
WoW Audio — Playwright web scraper.

A browser-based companion to research.py. Playwright drives a real Chromium, so
it can render JS-heavy pages and get past the simpler bot walls that block plain
requests.

Two modes:

1) HiFi Shark price research (structured, --update into the brand JSON):
    python scripts/scrape.py --brand marantz --model 2230
    python scripts/scrape.py --brand marantz --model 2285B --months 3 --update
    # writes avg_price_usd_3mo / price_confidence / last_price_check into
    # data/marantz.json for the record whose jdm_model matches --model.

2) Ad-hoc page scraping by URL:
    python scripts/scrape.py "https://classicreceivers.com/marantz-2230" --dump
    python scripts/scrape.py "https://www.usaudiomart.com/details/..." --headful --profile .pw-profile

Working today with a plain headless fetch: hifishark.com, classicreceivers.com,
hifiengine.com, radiomuseum.org. Behind Cloudflare (need --headful --profile, or
an official API): usaudiomart.com, canuckaudiomart.com, ebay.com.

Cloudflare note: for walled sites, run once with --headful --profile <dir>, solve
the "Just a moment..." challenge yourself, and the saved session is reused after.

Requires: playwright, beautifulsoup4  (pip install playwright beautifulsoup4
          && python -m playwright install chromium)
"""

import sys
import re
import json
import argparse
import datetime
from pathlib import Path
from urllib.parse import urlparse, quote_plus

try:
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run:")
    print("  python -m pip install playwright beautifulsoup4")
    print("  python -m playwright install chromium")
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Multi-char symbols MUST come before single-char ones (CA$ before A$, US$ before $).
CURRENCY = {"US$": "USD", "CA$": "CAD", "C$": "CAD", "A$": "AUD", "AU$": "AUD",
            "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "฿": "THB"}
PRICE_RE = re.compile(r"(US\$|CA\$|C\$|AU\$|A\$|[$€£¥฿])\s?([\d.,]{2,})")
DATE_RE = re.compile(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(20\d{2})")

# Approximate FX -> USD, ~Aug 2026. HiFi Shark aggregates many currencies; edit
# these if they drift. Used only to average mixed-currency listings into USD.
FX_TO_USD = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27, "AUD": 0.66,
             "CAD": 0.73, "JPY": 0.0067, "THB": 0.030}


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------
def fetch_rendered(url, wait_selector=None, headful=False, profile=None, timeout=30000):
    """Load `url` in Chromium, wait for the page, return the rendered HTML.

    `profile` = a directory for a persistent browser profile. Run once with
    --headful and solve any Cloudflare challenge yourself; the session is saved
    there and reused, so later runs get through.
    """
    with sync_playwright() as p:
        if profile:
            ctx = p.chromium.launch_persistent_context(
                profile, headless=not headful, user_agent=UA, locale="en-US")
            page = ctx.new_page()
            close = ctx.close
        else:
            browser = p.chromium.launch(headless=not headful)
            ctx = browser.new_context(user_agent=UA, locale="en-US")
            page = ctx.new_page()
            close = browser.close
        page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        try:
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout)
            else:
                page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception:
            pass  # partial render is still worth parsing
        page.wait_for_timeout(1500)  # let late JS settle
        html = page.content()
        close()
    return html


def parse_price(text):
    """First currency+amount found in `text` -> (float, currency) or (None, None)."""
    m = PRICE_RE.search(text or "")
    if not m:
        return None, None
    sym, num = m.group(1), m.group(2).replace(",", "")
    try:
        return float(num), CURRENCY.get(sym, sym)
    except ValueError:
        return None, None


def parse_date(text):
    """'Jun 1, 2026' -> datetime.date, or None."""
    m = DATE_RE.search(text or "")
    if not m:
        return None
    try:
        return datetime.datetime.strptime(m.group(0), "%b %d, %Y").date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Site parsers  (add one per domain)
# ---------------------------------------------------------------------------
def parse_hifishark(soup, url):
    """HiFi Shark model/search pages: each listing is an <a.search-product-row>."""
    out = []
    for row in soup.select("a.search-product-row"):
        info = row.select_one(".search-product-info")
        price_el = row.select_one(".price")
        price, cur = parse_price(price_el.get_text() if price_el else "")
        info_txt = info.get_text(" ", strip=True) if info else row.get_text(" ", strip=True)
        href = row.get("href", "")
        out.append({
            "title": info_txt[:80],
            "price": price,
            "currency": cur,
            "date": parse_date(info_txt),
            "condition": None,
            "url": ("https://www.hifishark.com" + href) if href.startswith("/") else href,
        })
    return out


def parse_usaudiomart(soup, url):
    """usaudiomart / canuckaudiomart detail pages (Cloudflare-walled — needs --profile)."""
    out = []
    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else None
    price, cur = None, None
    price_el = soup.find(class_=re.compile("price", re.I))
    if price_el:
        price, cur = parse_price(price_el.get_text(" ", strip=True))
    if price is None:
        price, cur = parse_price(soup.get_text(" ", strip=True))
    out.append({"title": title, "price": price, "currency": cur,
                "condition": None, "url": url})
    return out


SITE_PARSERS = {
    "hifishark.com": parse_hifishark,
    # usaudiomart/canuckaudiomart are Cloudflare-walled — need --headful --profile.
    "usaudiomart.com": parse_usaudiomart,
    "canuckaudiomart.com": parse_usaudiomart,
    # "reverb.com": parse_reverb,   # prefer the Reverb API where possible
    # NOTE: eBay and Facebook are intentionally omitted — eBay blocks scraping
    # (use its official API); Facebook needs login and forbids scraping.
}


def dump_prices(soup, limit=40):
    """Print every price-like token — for figuring out a new site's selectors."""
    seen = 0
    for m in PRICE_RE.finditer(soup.get_text(" ", strip=True)):
        print("  ", m.group(0))
        seen += 1
        if seen >= limit:
            break
    if not seen:
        print("  (no price-like text found — try --headful to see what rendered)")


# ---------------------------------------------------------------------------
# HiFi Shark research mode
# ---------------------------------------------------------------------------
def hifishark_search_url(brand, model):
    return "https://www.hifishark.com/search?q=" + quote_plus(f"{brand} {model}")


# Parts/manuals/accessories masquerading as the amp in HiFi Shark results.
# Filtering by title removes them regardless of price, so the median reflects
# whole, working units — not a pile of $80 faceplates.
JUNK_RE = re.compile(
    r"(\b(manual|faceplate|face\s?plate|front\s?panel|knob|meter|manuals|parts|"
    r"for\s?parts|repair|not\s?working|as[-\s]?is|dial|bulb|glass|wood\s?case|"
    r"wooden\s?case|cabinet\s?only|case\s?only|badge|emblem|logo|switch|capacitor|"
    r"cap\s?kit|recap|restoration\s?kit|pcb|circuit\s?board|schematic|service|"
    r"remote|cover|feet|screw|transformer|output\s?board|kit|instruction|"
    r"instructions|anleitung|prospekt|katalog|brochure|sticker|decal|"
    r"replacement|rebuild)\b|lamp)", re.I)


# Model-name suffixes that mark a DIFFERENT (usually later, dearer) model.
# "AU-607" must not match "AU-607 MR"; "Model 250" must not match "Model 250M".
# note: "vintage" is deliberately absent — it's a stock word in vintage-audio
# listing titles ("Top Vintage Endstufe"), and "mos" already guards the real
# MOS Vintage models.
VARIANT_SUFFIX = {"mr", "mrx", "xr", "kx", "dr", "nra", "mos", "limited", "extra",
                  "ii", "iii", "decade", "anniversary", "premium",
                  "ltd", "mkii", "mk2", "signature"}


def _tokens(s):
    """'Sansui AU-607 MR' -> ['sansui', 'au607', 'mr']

    The Alpha series appears as 'AU-α607', 'AU-a607' or 'AU-Alpha-607'
    depending on the seller, so those are folded together first.
    """
    s = str(s or "").lower().replace("α", "alpha")
    s = re.sub(r"\bau[\s-]*a(?=\d)", "au-alpha", s)
    return [re.sub(r"[^a-z0-9]", "", t)
            for t in re.split(r"\s+", s) if t.strip()]


def title_matches(title, model):
    """True if `title` is really about `model` and not a variant of it.

    Listings spell a model every which way — "BA-5000", "BA 5000", "Ba5000" —
    so the model's tokens are joined and compared against joins of up to four
    adjacent title tokens. Once matched, the following token is checked: a
    variant marker (MR, XR, MOS Limited, ...) means it's a different amp.
    A trailing-letter variant (250 vs 250M) fails the join comparison outright.
    """
    if not title or not model:
        return True                      # nothing to check against
    want = "".join(t for t in _tokens(model) if t)
    tt = [t for t in _tokens(title) if t]
    if not want:
        return True
    for i in range(len(tt)):
        joined = ""
        for j in range(i, min(i + 4, len(tt))):
            joined += tt[j]
            if joined == want:
                nxt = tt[j + 1] if j + 1 < len(tt) else ""
                return nxt not in VARIANT_SUFFIX
            if len(joined) > len(want):
                break
    return False


def summarize_usd(listings, months, headful=False, profile=None, model=None):
    """Filter to the last `months`, convert to USD, return a summary dict."""
    cutoff = datetime.date.today() - datetime.timedelta(days=int(30.4 * months))
    usd, kept, skipped_cur = [], [], set()
    for x in listings:
        if x["price"] is None or not x["currency"]:
            continue
        if x.get("title") and JUNK_RE.search(x["title"]):
            continue  # skip parts, manuals, faceplates, etc.
        if model and not title_matches(x.get("title"), model):
            continue  # different model / variant
        if x["date"] and x["date"] < cutoff:
            continue
        rate = FX_TO_USD.get(x["currency"])
        if rate is None:
            skipped_cur.add(x["currency"])
            continue
        usd.append(round(x["price"] * rate))
        kept.append(x)
    if not usd:
        return None
    raw_n = len(usd)
    # Trim junk before averaging: a hard floor/ceiling kills parts, manuals and
    # knobs (too cheap) and price typos (too dear); then an IQR fence removes the
    # remaining outliers so the median reflects real amplifier sales.
    FLOOR, CEIL = 60, 20000
    usd = [v for v in usd if FLOOR <= v <= CEIL]
    if not usd:
        return None
    usd.sort()
    if len(usd) >= 4:
        q1 = usd[len(usd) // 4]
        q3 = usd[(3 * len(usd)) // 4]
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        fenced = [v for v in usd if lo <= v <= hi]
        if fenced:
            usd = fenced
    mid = usd[len(usd) // 2] if len(usd) % 2 else round((usd[len(usd) // 2 - 1] + usd[len(usd) // 2]) / 2)
    return {"count": len(usd), "raw_count": raw_n, "avg": round(sum(usd) / len(usd)),
            "median": mid, "low": usd[0], "high": usd[-1],
            "skipped_currencies": sorted(skipped_cur)}


def research_hifishark(brand, model, months, update, headful, profile, emit_json=False):
    url = hifishark_search_url(brand, model)
    if not emit_json:
        print(f"HiFi Shark: {brand} {model}  (last {months} mo)")
        print(f"  {url}")
    html = fetch_rendered(url, wait_selector="a.search-product-row",
                          headful=headful, profile=profile)
    soup = BeautifulSoup(html, "html.parser")
    listings = parse_hifishark(soup, url)
    summary = summarize_usd(listings, months, model=model)

    if emit_json:
        # Machine-readable one-liner for serve.py's /api/price endpoint.
        if not summary:
            print(json.dumps({"ok": False, "error": "no dated, priced listings in window",
                              "count": 0, "brand": brand, "model": model, "months": months}))
        else:
            print(json.dumps({"ok": True, "brand": brand, "model": model,
                              "months": months, **summary}))
        return

    if not summary:
        print("  No dated, priced listings in window.")
        return
    print(f"  n={summary['count']}  avg=${summary['avg']:,}  median=${summary['median']:,}  "
          f"range ${summary['low']:,}-${summary['high']:,}  (USD, FX-converted)")
    if summary["skipped_currencies"]:
        print(f"  (skipped currencies with no FX rate: {summary['skipped_currencies']})")

    if update:
        meta = None
        db, meta = load_db(brand)
        hit = None
        for e in db:
            if str(e.get("jdm_model", "")).lower() == model.lower():
                hit = e
                break
        if not hit:
            print(f"  No record with jdm_model == '{model}' in {brand}.json — not written.")
            return
        hit["avg_price_usd_3mo"] = summary["median"]  # median is sturdier than mean
        hit["price_basis"] = f"hifishark {months}mo median (FX->USD) {datetime.date.today():%Y-%m}"
        hit["price_confidence"] = "Medium" if summary["count"] >= 3 else "Low"
        hit["last_price_check"] = f"{datetime.date.today():%Y-%m}"
        save_db(db, meta)
        print(f"  Updated {meta['path'].name}: {model} -> avg_price_usd_3mo ${summary['median']:,}")


# ---------------------------------------------------------------------------
# DB helpers — preserve BOM + line endings so edits stay a clean git diff
# ---------------------------------------------------------------------------
def load_db(brand):
    path = DATA_DIR / f"{brand}.json"
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    return json.loads(text), {"path": path, "bom": has_bom, "crlf": crlf}


def save_db(data, meta):
    s = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if meta["crlf"]:
        s = s.replace("\n", "\r\n")
    encoded = s.encode("utf-8")
    if meta["bom"]:
        encoded = b"\xef\xbb\xbf" + encoded
    meta["path"].write_bytes(encoded)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Playwright scraper for WoW Audio.")
    ap.add_argument("url", nargs="?", help="page to scrape (ad-hoc mode)")
    ap.add_argument("--brand", help="HiFi Shark mode: brand, e.g. marantz")
    ap.add_argument("--model", help="HiFi Shark mode: model, e.g. 2230")
    ap.add_argument("--months", type=int, default=3, help="price window in months (default 3)")
    ap.add_argument("--update", action="store_true",
                    help="write avg_price_usd_3mo into data/<brand>.json (HiFi Shark mode)")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="HiFi Shark mode: print the summary as one JSON line (for serve.py)")
    ap.add_argument("--dump", action="store_true",
                    help="ad-hoc mode: print all price-like text instead of parsing")
    ap.add_argument("--headful", action="store_true", help="show the browser")
    ap.add_argument("--profile", metavar="DIR",
                    help="persistent profile dir (clear Cloudflare once in --headful, reuse after)")
    args = ap.parse_args()

    # HiFi Shark research mode
    if args.brand and args.model:
        research_hifishark(args.brand, args.model, args.months,
                           args.update, args.headful, args.profile,
                           emit_json=args.as_json)
        return

    if not args.url:
        ap.error("give a URL, or --brand and --model for HiFi Shark mode")

    # Ad-hoc URL mode
    host = urlparse(args.url).netloc.replace("www.", "")
    print(f"Fetching {args.url} ...")
    html = fetch_rendered(args.url, headful=args.headful, profile=args.profile)
    soup = BeautifulSoup(html, "html.parser")

    if args.dump:
        print("Price-like text on page:")
        dump_prices(soup)
        return

    parser = SITE_PARSERS.get(host)
    if not parser:
        print(f"No parser registered for '{host}'.")
        print("Run with --dump to inspect the page, then add a parse_<site>() function.")
        return

    for row in parser(soup, args.url):
        printable = {k: (v.isoformat() if isinstance(v, datetime.date) else v)
                     for k, v in row.items()}
        print(json.dumps(printable, ensure_ascii=False))


if __name__ == "__main__":
    main()
