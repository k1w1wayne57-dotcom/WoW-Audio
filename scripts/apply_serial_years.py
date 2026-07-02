"""Apply factual production-year ranges from the serial report to sansui.json.

- Matches DB jdm_model to serial-report models (handles alpha glyph, parentheticals, slashes).
- Robust range: drops a lone earliest/latest year if it is isolated by >3 years from the
  next value (single mis-keyed serial), so one bad date can't corrupt the range.
- Updates year_start / year_end. Sets year_source="serial-report" on updated entries.
- Writes UTF-8 (no BOM). Prints a full change report and flags large discrepancies.
"""
import json, re
from pathlib import Path

serials = json.load(open("scripts/serials_parsed.json", encoding="utf-8"))
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

def norm(s):
    if not s:
        return ""
    s = str(s).upper().replace("α", "ALPHA").replace("ALFA", "ALPHA")
    s = re.sub(r"\([^)]*\)", "", s)          # drop parentheticals like (1st Gen)
    s = re.sub(r"\b\d+(ST|ND|RD|TH)\s+GEN\b", "", s)  # stray "3rd gen"
    s = re.sub(r"[\s\-_.]", "", s)
    return s

# Index serial data by normalized key; keep record with most dates
sindex = {}
for model, v in serials.items():
    if not v.get("min_year"):
        continue
    k = norm(model)
    if k not in sindex or v["n_dates"] > sindex[k][1]["n_dates"]:
        sindex[k] = (model, v)

def candidates(jm):
    """Yield normalized keys to try for a DB model name."""
    yield norm(jm)
    if "/" in jm:
        for part in jm.split("/"):
            yield norm(part)

def robust_range(years):
    """Drop a single isolated outlier at either end (>3yr gap to neighbour)."""
    ys = sorted(set(years))
    if len(ys) >= 3:
        if ys[1] - ys[0] > 3:
            ys = ys[1:]
        if ys[-1] - ys[-2] > 3:
            ys = ys[:-1]
    return ys[0], ys[-1]

updated, flagged, unmatched = [], [], []
for entry in db:
    jm = entry.get("jdm_model")
    rec = None
    for k in candidates(jm):
        if k in sindex:
            rec = sindex[k][1]
            break
    if not rec:
        unmatched.append(jm)
        continue

    old_s, old_e = entry.get("year_start"), entry.get("year_end")
    raw_min, raw_max = rec["min_year"], rec["max_year"]
    new_s, new_e = robust_range(rec["years_list"])

    if new_s != old_s or new_e != old_e:
        entry["year_start"] = new_s
        entry["year_end"] = new_e
        entry["year_source"] = "serial-report"
        note = ""
        if raw_min != new_s or raw_max != new_e:
            note = f"  (trimmed outlier from {raw_min}-{raw_max})"
        big = old_s is not None and abs(old_s - new_s) >= 4
        rowinfo = (jm, old_s, old_e, new_s, new_e, rec["n_dates"], note, big)
        updated.append(rowinfo)
        if big:
            flagged.append(rowinfo)
    else:
        entry.setdefault("year_source", "serial-report")

# Write back: UTF-8, no BOM, preserve unicode (α etc.)
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Updated {len(updated)} of {len(db)} models. Unmatched: {len(unmatched)}\n")
print("=== LARGE CHANGES (start moved >=4 yrs) — please eyeball ===")
for jm, os_, oe, ns, ne, n, note, big in flagged:
    print(f"  {jm:26s} {str(os_):>5}-{str(oe):<5} -> {ns}-{ne}  ({n} dates){note}")
print(f"\n{len(flagged)} flagged. All years now sourced from serial report.")
print("\n=== STILL UNMATCHED DB MODELS ===")
for u in unmatched:
    print("  ", u)
