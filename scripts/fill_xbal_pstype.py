import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Every model whose amp topology is X-Balanced / alpha-X-Balanced gets ps_type "X-Balanced".
# Keep the more specific "(floating balanced supply)" on the confirmed pure-X integrateds.
changed = []
for e in db:
    ac = (e.get("amp_circuit") or "").lower()
    if "x balanc" in ac or "x-balanc" in ac:
        cur = e.get("ps_type") or ""
        if "X-Balanced" not in cur:   # skip the ones already tagged X-Balanced(...)
            old = e.get("ps_type")
            e["ps_type"] = "X-Balanced"
            changed.append((e["jdm_model"], old))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"Set ps_type=X-Balanced on {len(changed)} models:")
for jm, old in changed:
    print(f"  {jm:26s} (was {old!r})")
from collections import Counter
c = Counter(e.get("ps_type") for e in db if e.get("ps_type"))
print("\nTallies:", dict(c))
