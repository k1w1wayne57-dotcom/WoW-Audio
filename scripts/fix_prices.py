"""Split the contaminated japan_price_kyen column - EVIDENCE ONLY, no guessing.

Background: some japan_price_kyen values are really US dollar MSRPs (proved by e.g.
AU-777 = 280 while audio-database gives its real Japan price as JPY57,000). But the column
is a MIX: e.g. AU-9500 = 135 IS the correct yen (JPY135,000). So a blanket rule would
mislabel the already-correct rows.

Rule applied here:
  - researched yen exists AND differs from stored -> stored is provably NOT the yen:
    move it to usd_msrp and write the correct yen.  (PROVEN)
  - researched yen exists and matches            -> already correct, leave alone.
  - no researched yen                            -> UNKNOWN, leave untouched (do not guess).
"""
import json
import re
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# recover researched yen (audio-database figures) from my own fill scripts
researched = {}
pat_entry = re.compile(r'"([^"]+)":\s*dict\((.*?)\),\n', re.S)
pat_price = re.compile(r"japan_price_kyen\s*=\s*([\d.]+)")
for p in sorted(Path("scripts").glob("fill_batch*.py")):
    for model, body in pat_entry.findall(p.read_text(encoding="utf-8")):
        m = pat_price.search(body)
        if m:
            researched[model] = float(m.group(1))

fixed, already_ok, unknown = [], [], []
for e in db:
    e.setdefault("usd_msrp", None)
    cur = e.get("japan_price_kyen")
    yen = researched.get(e["jdm_model"])
    if cur is None or yen is None:
        if cur is not None:
            unknown.append(e["jdm_model"])
        continue
    if abs(cur - yen) < 0.01:
        already_ok.append(e["jdm_model"])
    else:
        e["usd_msrp"] = int(cur)          # provably not the yen -> the US list price
        e["japan_price_kyen"] = yen
        fixed.append((e["jdm_model"], int(cur), yen))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"FIXED (proven dollar->usd_msrp, correct yen restored): {len(fixed)}")
for jm, usd, yen in sorted(fixed):
    print(f"   {jm:12s} ${usd:<5} US   ->  japan JPY {yen}k")
print(f"\nAlready correct yen (left alone): {len(already_ok)} -> {', '.join(sorted(already_ok))}")
print(f"\nUNVERIFIED (no researched yen; left untouched): {len(unknown)}")
