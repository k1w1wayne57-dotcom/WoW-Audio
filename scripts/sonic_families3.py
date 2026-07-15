"""Third pass - catch models the earlier matching missed:
  - "super-feedforward" (hyphen) didn't match "super feedforward"
  - tube receivers whose series/type isn't tagged Tube (500, 500A, SAX-100/200) but whose
    amp_circuit says tube
  - Alpha models with a null amp_circuit (matched on series instead)
  - early SS + quad receivers outside the classic-era window/type filter
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

ALPHA = next(e["sonic_signature"] for e in db if e["jdm_model"] == "AU-Alpha-707i")
SFF = next(e["sonic_signature"] for e in db if e["jdm_model"] == "AU-D33")
TUBE = next(e["sonic_signature"] for e in db if e["jdm_model"] == "AU-70")
CLASSIC = next(e["sonic_signature"] for e in db if e["jdm_model"] == "AU-999")

added = []
for e in db:
    if e.get("sonic_signature"):
        continue
    ac = (e.get("amp_circuit") or "").lower()
    series = e.get("series") or ""
    typ = e.get("type") or ""
    yr = e.get("year_start") or 0
    sig = None
    if "feedforward" in ac or "super ff" in ac:
        sig = SFF
    elif "tube" in ac:
        sig = TUBE
    elif series == "Alpha Series" and typ == "Integrated":
        sig = ALPHA
    elif typ in ("Integrated", "Receiver", "Receiver 4-ch") and 1965 <= yr <= 1973:
        sig = CLASSIC
    if sig:
        e["sonic_signature"] = sig
        added.append((e["jdm_model"], sig.split(":")[0]))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Added: {len(added)}")
for jm, fam in added:
    print(f"   {jm:22s} <- {fam}")
total = sum(1 for e in db if e.get("sonic_signature"))
print(f"\nsonic_signature now on {total} / {len(db)}")
from collections import Counter
miss = [e for e in db if not e.get("sonic_signature")]
print("Still none:", len(miss), dict(Counter(e.get("type") for e in miss)))
