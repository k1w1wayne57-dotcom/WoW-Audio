"""Mark which entries are the international/export badge so the detail page can label the
counterpart correctly. AU-517's int_model is AU-607 - that's the JDM name, so labelling it
"Int'l Model" was backwards.
Confirmed export lines (sansui.us export-vs-domestic history): AU-x17, AU-x19, TU-x17.
Everything else is left unset rather than claimed.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

EXPORT = ["AU-117", "AU-117II", "AU-217", "AU-217II", "AU-317", "AU-317II", "AU-417",
          "AU-517", "AU-717", "AU-519", "AU-719", "AU-819", "AU-919",
          "TU-217", "TU-317", "TU-517", "TU-717"]

for e in db:
    e.setdefault("market", None)
for jm in EXPORT:
    if jm in by:
        by[jm]["market"] = "International"
    else:
        print("  !! not found:", jm)

# the JDM models that have a known export counterpart
jdm_with_export = [e["jdm_model"] for e in db
                   if e.get("int_model") and e.get("market") != "International"]
for jm in jdm_with_export:
    by[jm]["market"] = "JDM"

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"International (export badge): {sum(1 for e in db if e.get('market')=='International')}")
print(f"JDM with a known export name: {sum(1 for e in db if e.get('market')=='JDM')}")
for jm in EXPORT:
    e = by.get(jm)
    if e: print(f"   {jm:9s} market={e['market']:14s} counterpart={e.get('int_model')}")
