"""Apply factual corrections and fix naming quirks in sansui.json.
See accompanying chat message for rationale. Idempotent-ish: run once on the
serial-updated DB.
"""
import json
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_id = {e["id"]: e for e in db}

def note(e, text):
    ci = e.setdefault("collector_info", {})
    ci["collector_notes"] = text

# --- Deletions (spurious / fiction / duplicates) ---
DELETE = {
    "sansui-au-111-1973",          # no 1973 AU-111; real reissue is 1999 Vintage
    "sansui-au-319-1979",          # fiction; only the AU-317 exists
    "sansui-au-701-1975",          # folded into AU-alpha607 as int_model (AU-X701)
    "sansui-au-alpha607-1978",     # spurious duplicate of the 1986 alpha607
    "sansui-au-alpha717-1st-gen-1976",  # duplicate of existing AU-717
}

# --- Field edits by id ---
# 1. AU-111 Vintage: re-released 1999 (later the AU-111G)
if "sansui-au-111-vintage-2001" in by_id:
    e = by_id["sansui-au-111-vintage-2001"]
    e["year_start"] = 1999
    e["year_end"] = 2001
    e["year_source"] = "manual"
    note(e, "Re-released 1999 as the AU-111 Vintage due to the original's legendary "
            "status; the AU-111G followed later. Redesigned to complement modern "
            "SACD/DVD-Audio sources while retaining the original tube sonic signature.")

# 2. A-M99 is a real servo amplifier
if "sansui-a-m99-1980" in by_id:
    e = by_id["sansui-a-m99-1980"]
    e["amp_circuit"] = "Servo amplifier"
    note(e, "Servo (power) amplifier — a real model, not fiction.")

# 3. Canonical AU-alpha607 (from the '(7th gen)' entry), INT = AU-X701 / AU-701
if "sansui-au-alpha607-7th-gen-1986" in by_id:
    e = by_id["sansui-au-alpha607-7th-gen-1986"]
    e["jdm_model"] = "AU-alpha607"
    e["int_model"] = "AU-X701"
    e["year_start"], e["year_end"] = 1986, 1987
    e["series"] = "Alpha Series"
    e["year_source"] = "serial-report"
    note(e, "International equivalent sold as the AU-X701 (often called AU-701), "
            "released 1987. Praised for a refined, detailed sound and powerful bass.")

# 4. Canonical AU-alpha707 (from the '(7th gen)' entry)
if "sansui-au-alpha707-7th-gen-1986" in by_id:
    e = by_id["sansui-au-alpha707-7th-gen-1986"]
    e["jdm_model"] = "AU-alpha707"
    e["year_start"], e["year_end"] = 1986, 1987
    e["series"] = "Alpha Series"
    e["year_source"] = "serial-report"

# 5. Relabel mislabeled first-gen entries to the missing plain AU-607 / AU-707
if "sansui-au-alpha607-1st-gen-1976" in by_id:
    e = by_id["sansui-au-alpha607-1st-gen-1976"]
    e["jdm_model"] = "AU-607"
    e["year_start"], e["year_end"] = 1977, 1979   # fix serial-strip corruption (was 1986)
    e["year_source"] = "manual"
    note(e, "First-generation AU-607 (1977). Start of the long-running 607 integrated line.")

if "sansui-au-alpha707-1977" in by_id:
    e = by_id["sansui-au-alpha707-1977"]
    e["jdm_model"] = "AU-707"
    e["year_start"], e["year_end"] = 1977, 1979
    e["year_source"] = "manual"
    note(e, "First-generation AU-707 (1977). Start of the long-running 707 integrated line.")

# --- Apply deletions ---
before = len(db)
db = [e for e in db if e["id"] not in DELETE]
after = len(db)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Deleted {before - after} entries: {sorted(DELETE)}")
print(f"Entries now: {after}")
print("\nEdited/renamed:")
for i in ["sansui-au-111-vintage-2001", "sansui-a-m99-1980",
          "sansui-au-alpha607-7th-gen-1986", "sansui-au-alpha707-7th-gen-1986",
          "sansui-au-alpha607-1st-gen-1976", "sansui-au-alpha707-1977"]:
    e = next((x for x in db if x["id"] == i), None)
    if e:
        print(f"  {i:38s} -> {e['jdm_model']!r:16s} int={e.get('int_model')!r} {e['year_start']}-{e['year_end']}")
