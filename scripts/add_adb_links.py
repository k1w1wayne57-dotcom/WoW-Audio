"""Set links.audio_database for each model to its audio-database.com page, where one exists.
The site redirects (302) unknown paths to its index and serves 200 only for real pages,
so we probe candidate URLs and keep the first that returns 200. URL patterns are
inconsistent (some -e.html, some not; amps under /amp/, tuners under /tuner/), so we try
several. Idempotent: skips models that already have a link.
"""
import json
import re
import subprocess
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
BASE = "https://audio-database.com/SANSUI"

def slug(jm):
    s = jm.lower().replace("α", "alpha")
    s = re.sub(r"[^a-z0-9\-]", "", s)   # drop spaces & punctuation, keep hyphens
    return s

def sections(typ):
    if typ == "Tuner":
        return ["tuner", "amp"]
    if typ == "Tape Deck":
        return ["tape", "deck", "amp"]
    return ["amp", "tuner"]

def candidates(jm, typ):
    sl = slug(jm)
    urls = []
    for sec in sections(typ):
        urls.append(f"{BASE}/{sec}/{sl}-e.html")
        urls.append(f"{BASE}/{sec}/{sl}.html")
    return urls

def http_status(url):
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-A", "Mozilla/5.0",
             "--max-time", "12", url],
            capture_output=True, text=True, timeout=20)
        return r.stdout.strip()
    except Exception:
        return "000"

found, missing = [], []
for e in db:
    links = e.setdefault("links", {})
    if links.get("audio_database"):
        found.append(e["jdm_model"]); continue
    hit = None
    for url in candidates(e["jdm_model"], e.get("type", "")):
        if http_status(url) == "200":
            hit = url; break
    if hit:
        links["audio_database"] = hit
        found.append(e["jdm_model"])
    else:
        missing.append(e["jdm_model"])

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Linked: {len(found)} / {len(db)}   No page found: {len(missing)}")
print("\nNo audio-database page (sample):")
for m in missing[:60]:
    print("  ", m)
