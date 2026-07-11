import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {e["jdm_model"]: e for e in db}

NOTE = ("Original data load had {val} in the Japan-price field. Export model, so not a yen "
        "price - possibly the US launch MSRP (~${val}). Unconfirmed; moved here pending "
        "verification.")

for jm in ("AU-517", "AU-717"):
    e = by_jm[jm]
    val = e.get("japan_price_kyen")
    if val in (450, 550):
        e["japan_price_kyen"] = None
        note = NOTE.format(val=int(val))
        ci = e.setdefault("collector_info", {})
        existing = ci.get("collector_notes")
        ci["collector_notes"] = f"{existing} | {note}" if existing else note
        print(f"  {jm}: price {val} -> null, noted in collector_notes")
    else:
        print(f"  {jm}: price is {val}, skipped")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
