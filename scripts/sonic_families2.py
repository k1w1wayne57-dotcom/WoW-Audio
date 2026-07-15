"""Second pass: cover the mid/late-70s silver-era amps and receivers that fall between the
classic-era AU line and the D/Alpha circuits. Their documented house character is the warm,
musical 'classic Sansui sound' of the company's peak years.
Accessories (tuners/decks/quad synths) and the BA/CA separates are left alone - a tuner has no
amp voicing, and I have no sourced character for the separates.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

SILVER = ("Silver-era Sansui: the warm, musical house sound of Sansui's peak years - full-bodied "
          "and rich with a smooth top end and an engaging, non-fatiguing presentation. "
          "(Family-level: mid/late-70s silver-face line.)")

TARGET_TYPES = ("Integrated", "Receiver", "Receiver 4-ch", "Power Amp 4-ch")
added = []
for e in db:
    if e.get("sonic_signature"):
        continue
    yr = e.get("year_start") or 0
    if e.get("type") in TARGET_TYPES and 1974 <= yr <= 1979:
        e["sonic_signature"] = SILVER
        added.append(e["jdm_model"])

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

total = sum(1 for e in db if e.get("sonic_signature"))
print(f"Added silver-era signatures: {len(added)}")
print(f"Models with a sonic_signature now: {total} / {len(db)}")
from collections import Counter
missing = [e for e in db if not e.get("sonic_signature")]
print(f"\nStill none: {len(missing)} -> by type:",
      dict(Counter(e.get("type") for e in missing)))
