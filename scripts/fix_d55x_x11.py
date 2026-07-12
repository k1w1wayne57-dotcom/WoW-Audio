import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {e["jdm_model"]: e for e in db}

WARN_KEY = "X-BALANCED SAFETY"

# AU-D55X: research + Wayne -> it is Super Feedforward (short-lived SFF circuit), NOT
# X-Balanced. Correct the amp_circuit and strip the X-Balanced safety warning I wrongly added.
e = by_jm["AU-D55X"]
e["amp_circuit"] = "Super Feedforward integrated amplifier"
ri = e.get("restorer_info", {})
rn = ri.get("recap_notes")
if rn and WARN_KEY in rn:
    # remove the warning segment (it was stored as "WARN | rest" or just "WARN")
    parts = [p.strip() for p in rn.split("|")]
    kept = [p for p in parts if WARN_KEY not in p]
    ri["recap_notes"] = " | ".join(kept) if kept else None

# AU-X11 (1981, flagship): EI-core (preamp) + large toroidal (power, independent L/R windings)
# = the same stage-split as the AU-919/AU-D907 => Penta-Power. (Sources also loosely call it
# "dual mono"; the EI+toroidal stage-split description is the defining evidence.)
x = by_jm["AU-X11"]
x["ps_type"] = "Penta-Power (dual transformer, stage-split)"
note = ("Stage-split supply like the AU-919/AU-D907: smaller EI-core transformer feeds the "
        "preamp/pre-driver, larger toroidal (independent L/R windings, 8 filter caps) feeds the "
        "power amps. Diamond-differential drive + Super Feedforward. Predates X-Balanced (1984).")
ci = x.setdefault("collector_info", {})
ci["collector_notes"] = f"{ci.get('collector_notes')} | {note}" if ci.get("collector_notes") else note

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("AU-D55X amp_circuit ->", e["amp_circuit"])
print("AU-D55X recap_notes ->", e["restorer_info"].get("recap_notes"))
print("AU-X11 ps_type ->", x["ps_type"])
