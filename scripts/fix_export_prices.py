"""Export-badged models (the AU-x17 / AU-x19 lines and their TU-x17 tuners) were sold
outside Japan only - their JDM counterparts carry the Japan name. So a 'japan price' on
them cannot be a yen figure; it is the US list price. Move it to usd_msrp and null the yen.
The JDM twin (linked via int_model) carries the real Japan price.
"""
import json
import re
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

EXPORT = ["AU-117", "AU-117II", "AU-217", "AU-217II", "AU-317", "AU-317II", "AU-417",
          "AU-517", "AU-717", "AU-519", "AU-719", "AU-819", "AU-919",
          "TU-217", "TU-317", "TU-517", "TU-717"]

moved = []
for jm in EXPORT:
    e = by.get(jm)
    if not e:
        print("  !! not found:", jm); continue
    jp = e.get("japan_price_kyen")
    if jp is not None:
        e["usd_msrp"] = int(jp)
        e["japan_price_kyen"] = None
        moved.append((jm, int(jp)))
    # recover the value I had parked in a note for AU-517 / AU-717
    ci = e.get("collector_info") or {}
    note = ci.get("collector_notes")
    if note and "Japan-price field" in note:
        m = re.search(r"had (\d+) in the Japan-price field", note)
        if m and not e.get("usd_msrp"):
            e["usd_msrp"] = int(m.group(1))
            moved.append((jm, int(m.group(1))))
        # drop the now-obsolete placeholder note
        parts = [p.strip() for p in note.split("|") if "Japan-price field" not in p]
        ci["collector_notes"] = " | ".join(parts) if parts else None

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("Export models: japan_price -> usd_msrp (yen nulled; JDM twin holds the real Japan price)")
for jm, v in moved:
    tw = by[jm].get("int_model")
    twyen = by[tw].get("japan_price_kyen") if tw and tw in by else None
    print(f"   {jm:9s} ${v:<5} US" + (f"   (JDM twin {tw} = JPY {twyen}k)" if twyen else ""))
