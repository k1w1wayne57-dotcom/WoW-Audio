"""Scrap the '/' combined names: give each model its own entry.
The second names (AU-819/AU-919/AU-D9) already exist as standalone entries,
so we just rename the '/' rows to their first (D-series) model and clean the
generation text. Years come from each model's own serial record (robust-trimmed).
"""
import json
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
serials = json.load(open("scripts/serials_parsed.json", encoding="utf-8"))

def snorm(k): return k.upper().replace(" ", "")
def rec_for(model):
    for k, v in serials.items():
        if snorm(k) == snorm(model):
            return v
    return None
def robust(years):
    ys = sorted(set(years))
    if len(ys) >= 3:
        if ys[1]-ys[0] > 3: ys = ys[1:]
        if ys[-1]-ys[-2] > 3: ys = ys[:-1]
    return ys[0], ys[-1]

# id -> (new jdm, generation label for note)
RENAME = {
    "sansui-au-d707-au-819-2nd-gen-1978":  ("AU-D707",  "2nd-generation 707 D-series"),
    "sansui-au-d907-au-919-2nd-gen-1978":  ("AU-D907",  "2nd-generation 907 D-series"),
    "sansui-au-d707f-au-d9-3rd-gen-1980":  ("AU-D707F", "3rd-generation 707 D-series"),
}
# also strip generation noise from these single-name entries
STRIP_GEN = {
    "sansui-au-d907f-3rd-gen-1980":       "AU-D907F",
    "sansui-au-d607f-extra-4th-gen-1981": "AU-D607F Extra",
    "sansui-au-d707f-extra-4th-gen-1981": "AU-D707F Extra",
    "sansui-au-d907g-5th-gen-1983":       "AU-D907G",
    "sansui-au-d607x-6th-gen-1984":       "AU-D607X",
    "sansui-au-d907x-6th-gen-1984":       "AU-D907X",
    "sansui-au-dalpha607-2nd-gen-1978":   "AU-Dalpha607",
}
by_id = {e["id"]: e for e in db}

for eid, (new_jm, genlabel) in RENAME.items():
    e = by_id[eid]
    e["jdm_model"] = new_jm
    e["int_model"] = None
    rec = rec_for(new_jm)
    if rec and rec["years_list"]:
        e["year_start"], e["year_end"] = robust(rec["years_list"])
        e["year_source"] = "serial-report"
    ci = e.setdefault("collector_info", {})
    if not ci.get("collector_notes"):
        ci["collector_notes"] = genlabel + "."

for eid, new_jm in STRIP_GEN.items():
    if eid in by_id:
        by_id[eid]["jdm_model"] = new_jm

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# verify no dup model numbers
from collections import Counter
c = Counter(e["jdm_model"] for e in db)
dups = {k: v for k, v in c.items() if v > 1}
print("Entries:", len(db))
print("Duplicate model numbers:", dups)
print("\nRenamed:")
for eid in list(RENAME) + list(STRIP_GEN):
    e = by_id[eid]
    print(f"  {e['jdm_model']:16s} {e['year_start']}-{e['year_end']}  (was {eid})")
