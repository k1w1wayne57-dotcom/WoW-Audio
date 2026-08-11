"""
WoW Audio — local admin server (Phase 1).

Serves the existing static site AND exposes a small write API so you can add /
update models from the browser (admin.html). Local only — binds to 127.0.0.1,
never exposed. The public GitHub Pages site stays a pure static read-only copy;
this is just how *you* edit the JSON on the fly.

Run:
    python serve.py            # then open http://127.0.0.1:8137/admin.html
    python serve.py --port 9000

Writes go through format-preserving load_db/save_db (keeps each file's CRLF and
BOM), so edits stay clean git diffs. After editing, commit & push as usual —
GitHub Pages then serves the updated data.

Phase 2 will add a "refresh price" button wired to scripts/scrape.py.

Requires: flask   (pip install flask)
"""

import re
import sys
import json
import copy
import argparse
import datetime
import subprocess
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

BRAND_NAMES = {"sansui": "Sansui", "marantz": "Marantz", "pioneer": "Pioneer"}

# Canonical record shape — new models start from this so every field exists.
CANONICAL = {
    "id": None, "brand": None, "jdm_model": None, "int_model": None,
    "type": None, "series": None, "year_start": None, "year_end": None,
    "japan_price_kyen": None, "watts_per_channel": None, "freq_response_hz": None,
    "thd_percent": None, "ps_type": None, "amp_circuit": None, "weight_kg": None,
    "special_features": None, "pros": None, "cons": None,
    "collector_ranking": None, "price_confidence": "None", "last_price_check": None,
    "collector_info": {"known_issues": None, "collector_notes": None},
    "restorer_info": {"known_failure_points": [], "bias_spec_mv": None,
                      "service_manual_link": None, "recap_difficulty": None,
                      "recap_notes": None, "estimated_recap_cost_usd": None,
                      "common_faults": []},
    "best_buy": {"rating": None, "reason": None},
    "capacitors": [],
    "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None,
              "brochure": None, "source": None},
    "notes": None, "verified": False, "verification": "sourced",
    "avg_price_usd_3mo": None, "price_basis": None, "year_source": None,
    "price_thb_listings": [], "usd_msrp": None, "market": None,
    "sonic_signature": None, "thb_status": None,
}

app = Flask(__name__, static_folder=None)


# ---------------------------------------------------------------------------
# Format-preserving DB IO (mirrors scripts/scrape.py)
# ---------------------------------------------------------------------------
def load_db(brand):
    path = DATA / f"{brand}.json"
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    return json.loads(text), {"path": path, "bom": bom, "crlf": crlf}


def save_db(data, meta):
    s = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if meta["crlf"]:
        s = s.replace("\n", "\r\n")
    encoded = s.encode("utf-8")
    if meta["bom"]:
        encoded = b"\xef\xbb\xbf" + encoded
    meta["path"].write_bytes(encoded)


def deep_merge(base, over):
    """Recursively overlay `over` onto `base`. Keys absent from `over` are kept,
    so form fields overwrite while untouched fields (e.g. capacitors) survive."""
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def gen_id(brand, rec):
    parts = [brand, slugify(rec.get("jdm_model") or "model")]
    if rec.get("year_start"):
        parts.append(str(rec["year_start"]))
    return "-".join(parts)


def bad(msg, code=400):
    return jsonify(ok=False, error=msg), code


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify(ok=True, brands=list(BRAND_NAMES), template=CANONICAL)


@app.get("/api/records")
def get_records():
    brand = request.args.get("brand", "")
    if brand not in BRAND_NAMES:
        return bad(f"unknown brand '{brand}'")
    data, _ = load_db(brand)
    return jsonify(ok=True, records=data)


@app.post("/api/records")
def add_record():
    body = request.get_json(force=True, silent=True) or {}
    brand = body.get("brand")
    rec = body.get("record") or {}
    if brand not in BRAND_NAMES:
        return bad(f"unknown brand '{brand}'")
    if not rec.get("jdm_model"):
        return bad("jdm_model is required")
    data, meta = load_db(brand)
    rid = (rec.get("id") or "").strip() or gen_id(brand, rec)
    if any(r.get("id") == rid for r in data):
        return bad(f"id already exists: {rid}", 409)
    new = deep_merge(copy.deepcopy(CANONICAL), rec)
    new["id"] = rid
    new["brand"] = BRAND_NAMES[brand]
    data.append(new)
    save_db(data, meta)
    return jsonify(ok=True, id=rid, record=new)


@app.get("/api/price")
def price():
    """Run the HiFi Shark scraper for one model and return a USD price summary.

    Uses scripts/scrape.py in a subprocess (--json) so Playwright never runs
    inside the Flask thread. Does NOT write anything — the browser fills the
    field and the user reviews before hitting Save.
    """
    brand = request.args.get("brand", "")
    model = request.args.get("model", "").strip()
    months = request.args.get("months", "3")
    if brand not in BRAND_NAMES:
        return bad(f"unknown brand '{brand}'")
    if not model:
        return bad("model is required")
    try:
        months_i = max(1, min(60, int(months)))
    except ValueError:
        months_i = 3
    cmd = [sys.executable, str(ROOT / "scripts" / "scrape.py"),
           "--brand", brand, "--model", model, "--months", str(months_i), "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", timeout=120)
    except subprocess.TimeoutExpired:
        return bad("scraper timed out (HiFi Shark slow or blocked)", 504)
    line = next((l for l in reversed(proc.stdout.splitlines()) if l.strip().startswith("{")), "")
    if not line:
        return bad("scraper returned no data: " + (proc.stderr.strip()[-300:] or "unknown error"), 502)
    try:
        summary = json.loads(line)
    except json.JSONDecodeError:
        return bad("could not parse scraper output", 502)
    if not summary.get("ok"):
        return jsonify(ok=True, found=False, **summary)
    summary["found"] = True
    summary["price_basis"] = f"hifishark {months_i}mo median (FX->USD) {datetime.date.today():%Y-%m}"
    return jsonify(**summary)


@app.put("/api/records/<rid>")
def update_record(rid):
    body = request.get_json(force=True, silent=True) or {}
    brand = body.get("brand")
    rec = body.get("record") or {}
    if brand not in BRAND_NAMES:
        return bad(f"unknown brand '{brand}'")
    data, meta = load_db(brand)
    idx = next((i for i, r in enumerate(data) if r.get("id") == rid), None)
    if idx is None:
        return bad(f"no record with id '{rid}' in {brand}", 404)
    deep_merge(data[idx], rec)
    data[idx]["id"] = rid          # id is immutable
    data[idx]["brand"] = BRAND_NAMES[brand]
    save_db(data, meta)
    return jsonify(ok=True, id=rid, record=data[idx])


# ---------------------------------------------------------------------------
# Static serving (index.html, app.js, admin.html, data/*, images/*, ...)
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return send_from_directory(ROOT, "index.html")


@app.get("/<path:fname>")
def static_files(fname):
    return send_from_directory(ROOT, fname)


@app.after_request
def no_cache_json(resp):
    # Don't let the browser cache data files, so edits show on reload.
    if request.path.endswith(".json"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


def main():
    ap = argparse.ArgumentParser(description="WoW Audio local admin server")
    ap.add_argument("--port", type=int, default=8137)
    args = ap.parse_args()
    print(f"WoW Audio admin — http://127.0.0.1:{args.port}/admin.html")
    print("Local only. Edit models, then git commit & push to update the public site.")
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
