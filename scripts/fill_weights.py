"""Fill researched weights (kg) for models that were otherwise spec-complete.
Sources: audio-database / HiFi Engine / hifi-wiki / Reverb.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

WEIGHTS = {
    "AU-519": 15.6, "AU-6900": 12.9, "8080DB": 20.7, "AU-D707F": 17.5,
    "AU-D907G": 17.7, "AU-D55X": 7.7, "AU-X11": 28.0, "AU-D101": 4.8,
}
done, missing = [], []
for jm, kg in WEIGHTS.items():
    e = by.get(jm)
    if not e:
        missing.append(jm); continue
    if e.get("weight_kg") in (None, ""):
        e["weight_kg"] = kg
        done.append((jm, kg))
    else:
        done.append((jm, f"{kg} (already had {e['weight_kg']}, skipped)"))

json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.load(open(DB_PATH, encoding="utf-8-sig"))
for jm, v in done: print(f"  {jm:12s} {v}")
if missing: print("  !! not found:", missing)
print("valid")
