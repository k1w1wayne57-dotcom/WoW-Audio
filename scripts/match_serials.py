"""Match parsed serial-report models to sansui.json and report year diffs (dry run)."""
import json, re, sys
from pathlib import Path

serials = json.load(open("scripts/serials_parsed.json", encoding="utf-8"))
db = json.load(open("data/sansui.json", encoding="utf-8-sig"))

def norm(s):
    if not s:
        return ""
    s = str(s).upper()
    s = s.replace("α", "ALPHA")   # α symbol -> ALPHA
    s = s.replace("ALFA", "ALPHA")
    s = re.sub(r"[\s\-_.]", "", s)      # drop spaces, hyphens, dots, underscores
    return s

# Build normalized index of serial data
sindex = {}
for model, v in serials.items():
    if not v.get("min_year"):
        continue
    sindex.setdefault(norm(model), []).append((model, v))

matched, unmatched, ndiff = [], [], 0
for entry in db:
    jm = entry.get("jdm_model")
    key = norm(jm)
    if key in sindex:
        # pick the serial record with most dates
        rec = sorted(sindex[key], key=lambda x: -x[1]["n_dates"])[0][1]
        matched.append((jm, entry.get("year_start"), entry.get("year_end"),
                        rec["min_year"], rec["max_year"], rec["n_dates"], rec["type"]))
    else:
        unmatched.append(jm)

print(f"DB entries: {len(db)}")
print(f"Matched to serial data: {len(matched)}")
print(f"Unmatched (no serial-year record): {len(unmatched)}\n")

print("=== YEAR DIFFERENCES (DB start/end -> serial min/max) ===")
for jm, ys, ye, smin, smax, n, typ in matched:
    diff_start = (ys != smin)
    diff_end = (ye != smax)
    if diff_start or diff_end:
        ndiff += 1
        flag = ""
        if ys and abs((ys or 0) - smin) >= 3: flag = "  <-- BIG START DIFF"
        print(f"  {jm:22s} DB {str(ys):>5}-{str(ye):<5}  serial {smin}-{smax}  ({n} dates){flag}")
print(f"\n{ndiff} models have differing years.")

print("\n=== SAMPLE UNMATCHED DB MODELS (first 40) ===")
for u in unmatched[:40]:
    print("  ", u)
