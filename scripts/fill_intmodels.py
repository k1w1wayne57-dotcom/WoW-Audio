import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Confirmed JDM -> international name pairs (documented equivalences).
# AU-D707/D907 are the Japanese-domestic models; AU-819/AU-919 the export names.
INT = {
    "AU-D707": "AU-819",
    "AU-D907": "AU-919",
    "AU-alpha607": "AU-X701",  # already set; keep
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, intname in INT.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    old = e.get("int_model")
    e["int_model"] = intname
    print(f"  {jm:12s} int_model: {old!r} -> {intname!r}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
