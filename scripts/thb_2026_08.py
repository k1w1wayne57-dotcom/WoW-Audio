"""Update Thai listings from Wayne's latest for-sale list, and mark previously-listed
models that are no longer for sale as Sold (sales tracking).
Each price is a separate listing (never averaged). thb_status: "For sale" | "Sold".
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}
DATE = "2026-08"

# resolved DB name -> current listing price(s)
FORSALE = {
    "551": [5200], "3000A": [8500], "5000X": [8500], "500A": [9000], "5900Z": [3000],
    "TR-707A": [4000], "AU-777D": [12500], "AU-217": [5900], "AU-666": [9900],
    "AU-707": [9500], "AU-888": [20000], "AU-9500": [8900], "AU-Alpha-317K": [3500],
    "AU-Alpha-607MR": [5500], "AU-Alpha-607NRA": [13900], "AU-X11": [25000],
    "AU-D55F": [3200], "AU-D607": [4900, 3900], "AU-D607F Extra": [7500],
    "AU-D607G Extra": [4000], "AU-D607X": [8000], "G-2000": [2600], "G-5700": [12500],
    "G-6700": [18000], "400": [3500], "QR-6500": [11600, 6500], "QR-4500": [9500],
    "QRX-3000": [5900], "QRX-3500": [5700], "QRX-5500": [15500], "QRX-7001": [20500],
    "QS-1": [9900], "SAX-200": [3500], "TU-9900": [8550],
}

# apply for-sale listings
missing = []
for jm, prices in FORSALE.items():
    e = by.get(jm)
    if not e:
        missing.append(jm); continue
    e["price_thb_listings"] = prices
    e["thb_status"] = "For sale"
    e["last_price_check"] = DATE

# anything that previously had a THB price but isn't in this for-sale list -> Sold
sold = []
for e in db:
    if e.get("price_thb_listings") and e["jdm_model"] not in FORSALE:
        if e.get("thb_status") != "Sold":
            e["thb_status"] = "Sold"
            sold.append(e["jdm_model"])
# ensure everyone has the field
for e in db:
    e.setdefault("thb_status", None)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"For sale updated: {len(FORSALE)-len(missing)}")
print(f"Newly marked SOLD: {len(sold)} -> {', '.join(sorted(sold))}")
if missing:
    print("!! for-sale model not in DB:", missing)
