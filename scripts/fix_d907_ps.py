import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {e["jdm_model"]: e for e in db}

# AU-D907 = JDM (100V) equivalent of AU-919 -> same Penta-Power architecture (Wayne/Gemini).
e = by_jm["AU-D907"]
e["ps_type"] = "Penta-Power (dual transformer, stage-split)"
note = ("Penta-Power supply, identical to the AU-919 (this is its 100V JDM equivalent): four "
        "independent supply systems derived from two separate transformers (toroidal for "
        "driver/output with independent L/R windings; EI-core for the Class-A preamp/pre-driver), "
        "plus a dedicated stabilized section. Stage isolation, not channel isolation - NOT dual mono.")
ci = e.setdefault("collector_info", {})
prev = ci.get("collector_notes")
ci["collector_notes"] = f"{prev} | {note}" if prev else note

# AU-D907F / AU-D907G: previously tagged Dual Mono by (now-broken) blanket assumption.
# No confirmed source -> null pending confirmation rather than assert.
for jm in ("AU-D907F", "AU-D907G"):
    by_jm[jm]["ps_type"] = None

# AU-D907X: leave Dual Mono (AudioKarma 907 chronology cites its dual-mono power-amp topology).

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
for jm in ("AU-D907", "AU-D907F", "AU-D907G", "AU-D907X"):
    print(f"  {jm:10s} ps_type = {by_jm[jm].get('ps_type')!r}")
