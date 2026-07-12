import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
e = next((x for x in db if x["jdm_model"] == "AU-919"), None)
if not e:
    print("AU-919 not found"); raise SystemExit

e["ps_type"] = "Penta-Power (dual transformer, stage-split)"
note = ("Penta-Power supply: a large toroidal transformer (with independent L/R windings) "
        "feeds the high-current driver/output stages, while a separate EI-core transformer "
        "feeds the Class-A preamp and pre-driver stages. This isolates by operational stage "
        "(power vs. preamp), not by channel - so it is NOT a standard dual-mono design. "
        "Minimizes intermodulation distortion and maximizes channel separation.")
ci = e.setdefault("collector_info", {})
prev = ci.get("collector_notes")
ci["collector_notes"] = f"{prev} | {note}" if prev else note

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("AU-919 ps_type ->", e["ps_type"])
