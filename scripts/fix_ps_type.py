"""Set ps_type from sourced power-supply topology, distinguishing:
  - "Dual Mono"          = separate transformer per channel / documented dual-mono power-amp topology
  - "Dual Power Supply"  = independent rails/windings & rectifiers, but NOT per-channel-isolated
Leave null everywhere it's a plain single supply or undocumented.
Sources: audio-database, HiFi Engine, vintageknob, AudioKarma 907-series chronology.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)

DUAL_MONO = [
    # true dual mono: separate transformer per channel (517/717/519/719 lineage)
    "AU-517", "AU-717", "AU-519", "AU-719",
    "AU-919",                       # multi-supply flagship; commonly & by Wayne called dual mono
    "AU-X1",
    # F1 / Definition flagship separates (dual-mono construction)
    "CA-3000", "BA-3000", "CA-F1", "BA-F1",
    # AU-D907 D-series: documented dual-mono power-amp topology (Penta-Power)
    "AU-D907", "AU-D907F", "AU-D907G", "AU-D907X",
    "AU-D607G Extra",               # Wayne's spec sheet states "PS dual mono"
]

DUAL_PSU = [
    # alpha-907 ladder: separate secondaries/rectifiers but caps paralleled -> NOT dual mono
    "AU-alpha907", "AU-alpha907i", "AU-alpha907i MOS LIMITED", "AU-alpha907 LIMITED",
    "AU-alpha907EXTRA", "AU-alpha907L EXTRA", "AU-alpha907DR", "AU-alpha907KX",
    "AU-alpha907XR", "AU-alpha907MR", "AU-alpha907NRA",
    # G-series monsters with documented dual/independent power supplies
    "G-9000", "G-9000DB", "G-22000", "G-33000", "G-8700DB", "G-9700",
]

changed = []
for jm in DUAL_MONO:
    e = by_jm.get(jm)
    if e and e.get("ps_type") != "Dual Mono":
        changed.append((jm, e.get("ps_type"), "Dual Mono")); e["ps_type"] = "Dual Mono"
    elif not e:
        print("  !! not found:", jm)
for jm in DUAL_PSU:
    e = by_jm.get(jm)
    if e and e.get("ps_type") != "Dual Power Supply":
        changed.append((jm, e.get("ps_type"), "Dual Power Supply")); e["ps_type"] = "Dual Power Supply"
    elif not e:
        print("  !! not found:", jm)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print("Changes:")
for jm, old, new in changed:
    print(f"  {jm:26s} {str(old):18s} -> {new}")
print(f"\n{len(changed)} changed.")
from collections import Counter
c = Counter(e.get("ps_type") for e in db if e.get("ps_type"))
print("Final ps_type tallies:", dict(c))
