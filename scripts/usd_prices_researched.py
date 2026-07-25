"""Replace the 18 ballpark ESTIMATE prices with researched current US market values.
Sources: Reverb/eBay/HifiShark/US Audio Mart sold+asking listings (mid-2026).
All go price_confidence=Medium except AU-D55F (data genuinely thin -> stays Low).
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

# jdm_model -> (usd, confidence)
UPDATES = {
    "2000": (275, "Medium"),          # 2000A asking $335; working units ~$250-300
    "250": (325, "Medium"),           # serviced tube, Reverb/Canuck ~$350
    "400": (300, "Medium"),           # fully serviced asking $409; typical ~$300
    "4000": (450, "Medium"),          # Reverb sold $550 (exc) / $700 (serviced); typical ~$450
    "500A": (400, "Medium"),          # tube, $369-500 across US Audio Mart/Reverb
    "551": (175, "Medium"),           # sold ~$150; retail $259
    "5900Z": (300, "Medium"),         # 75wpc, Reverb listings ~$250-350
    "800": (300, "Medium"),           # HifiShark $339; solid-state 25wpc
    "G-2000": (175, "Medium"),        # least-coveted G; serviced $799 outlier, typical ~$150-200
    "AU-3500": (225, "Medium"),       # $187-200 working; serviced bundles higher
    "AU-D55F": (250, "Low"),          # data thin (only AU-D55X comps) -> keep Low
    "AU-D607G Extra": (400, "Medium"),# $350-460 operation-confirmed
    "AU-Alpha-555VS": (475, "Medium"),# actual alpha-555VS ~$485
    "QS-1": (350, "Medium"),          # $250-535 quad synth
    "SAX-200": (350, "Medium"),       # tube; restored to €950, typical ~$350
    "TR-707A": (285, "Medium"),       # Reverb $269-300 good condition
    "TU-5500": (175, "Medium"),       # working ~$150-200; median €228
    "TU-707": (175, "Medium"),        # HifiShark median ~€144; Japan units higher
}

done, missing = [], []
for jm, (usd, conf) in UPDATES.items():
    e = by.get(jm)
    if not e:
        missing.append(jm); continue
    e["avg_price_usd_3mo"] = usd
    e["price_confidence"] = conf
    done.append((jm, usd, conf))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

for jm, usd, conf in done:
    print(f"  {jm:20s} ${usd:<5d} {conf}")
if missing:
    print("  !! not found:", missing)
print(f"\nUpdated {len(done)}/{len(UPDATES)}")
