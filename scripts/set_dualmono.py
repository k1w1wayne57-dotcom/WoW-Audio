import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)

# User-confirmed dual-mono integrateds/separates + the full 907 flagship ladder
# (user: the AU-D907/AU-a907 series relied on massive independent L/R supplies).
DUAL_MONO = [
    # classic dual-mono integrateds
    "AU-517", "AU-717", "AU-519", "AU-719", "AU-919",
    "AU-X1",
    # Definition-series separates
    "CA-3000", "BA-3000",
    # 907 D-series
    "AU-D907", "AU-D907F", "AU-D907G", "AU-D907X",
    # 907 Alpha ladder
    "AU-alpha907", "AU-alpha907i", "AU-alpha907i MOS LIMITED", "AU-alpha907 LIMITED",
    "AU-alpha907EXTRA", "AU-alpha907L EXTRA", "AU-alpha907DR", "AU-alpha907KX",
    "AU-alpha907XR", "AU-alpha907MR", "AU-alpha907NRA",
    # export twin of AU-D907 also dual mono
    "AU-919",
]
done, missing = [], []
for jm in dict.fromkeys(DUAL_MONO):
    e = by_jm.get(jm)
    if not e:
        missing.append(jm); continue
    if e.get("ps_type") != "Dual Mono":
        e["ps_type"] = "Dual Mono"
        done.append(jm)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"Set Dual Mono on {len(done)} models:")
for jm in done:
    print("  ", jm)
if missing:
    print("Not found:", missing)
