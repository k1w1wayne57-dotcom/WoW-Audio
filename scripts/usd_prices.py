"""Set current US market prices (avg_price_usd_3mo) for the Thai-list models.
RESEARCHED = pulled from current Reverb/eBay/HifiShark listings (price_confidence Medium).
ESTIMATE   = ballpark from the model class where US data was thin (price_confidence Low).
Only fills null values + updates AU-D607X (stale). Existing researched values left as-is.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

RESEARCHED = {
    "AU-777D": 650, "AU-888": 750, "AU-666": 300, "AU-217": 230, "QRX-5500": 450,
    "AU-Alpha-607NRA": 1250, "AU-D607": 450, "AU-5500": 500, "G-5000": 800,
    "AU-D607X": 800, "AU-Alpha-607MR": 800, "TU-9900": 700, "QRX-3000": 250,
    "QRX-3500": 350, "AU-Alpha-317K": 400, "AU-Alpha-305RX": 350, "B-2102": 550,
    "A-80": 275, "3000A": 150,
}
ESTIMATE = {
    "2000": 200, "250": 300, "400": 175, "4000": 250, "500A": 350, "551": 175,
    "5900Z": 250, "800": 225, "G-2000": 150, "AU-3500": 250, "AU-D55F": 250,
    "AU-D607G Extra": 500, "AU-Alpha-555VS": 500, "QS-1": 150, "SAX-200": 200,
    "TR-707A": 300, "TU-5500": 150, "TU-707": 200,
}

def apply(d, conf):
    done = []
    for jm, usd in d.items():
        e = by.get(jm)
        if not e:
            print("  !! not found:", jm); continue
        e["avg_price_usd_3mo"] = usd
        e["price_confidence"] = conf
        done.append(jm)
    return done

r = apply(RESEARCHED, "Medium")
s = apply(ESTIMATE, "Low")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# report coverage across the whole Thai list
thai = [e for e in db if e.get("price_thb_listings")]
have = [e for e in thai if e.get("avg_price_usd_3mo")]
print(f"Researched set: {len(r)}   Estimated set: {len(s)}")
print(f"Thai-list models with a US price now: {len(have)}/{len(thai)}")
