"""Correct AU-D907X to X-Balanced (not Dual Mono) and add the universal X-Balanced
8-terminal safety warning to every X-Balanced / alpha-X-Balanced model.

Scope decisions:
- ps_type "X-Balanced (floating balanced supply)" set ONLY on the confirmed 1984 X-series
  integrateds (D607X, D907X, G99X). Pre-1984 'X'-suffix models and the alpha ladder's
  supply implementation are left as-is pending confirmation (not guessed).
- The 8-terminal warning applies to ALL balanced-drive (X-Balanced / alpha-X-Balanced)
  amps and is added to each.
- Fix AU-D907G amp_circuit: it is Super Feedforward (1983), NOT X-Balanced (that arrived
  with the 1984 X-series) - my earlier label was wrong.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {e["jdm_model"]: e for e in db}

WARN = ("X-BALANCED SAFETY: both the red (+) and black (-) speaker terminals carry live, "
        "independent voltage. NEVER bridge/common the black terminals together, and NEVER "
        "connect a black terminal to chassis or an external/test ground - doing so shorts the "
        "floating balanced rails and instantly destroys the output transistors.")

XBAL_PS = "X-Balanced (floating balanced supply)"

# 1) AU-D907X: correct topology + detailed note
e = by_jm["AU-D907X"]
e["ps_type"] = XBAL_PS
d907x_note = ("X-Balanced supply (introduced 1984): the power supply is lifted off chassis "
              "ground and works as a closed +/- loop; one colossal centre toroidal (>10kg) with "
              "isolated windings splits into four independent rectify/filter sections driving both "
              "the + and - side of each channel. No chassis-ground return path, so ground-loop "
              "noise/ripple cannot reach the signal - a fundamentally different design from the "
              "AU-919/AU-D907 Penta-Power.")
ci = e.setdefault("collector_info", {})
ci["collector_notes"] = f"{ci.get('collector_notes')} | {d907x_note}" if ci.get("collector_notes") else d907x_note

# 2) ps_type on the confirmed 1984 X-series
for jm in ("AU-D607X", "AU-G99X"):
    by_jm[jm]["ps_type"] = XBAL_PS

# 3) fix mislabeled AU-D907G amp_circuit
g = by_jm["AU-D907G"]
if g.get("amp_circuit", "").startswith("X-Balanced"):
    g["amp_circuit"] = "Super Feedforward DC integrated"

# 4) add the 8-terminal warning to every X-Balanced / alpha-X-Balanced model
warned = []
for e in db:
    ac = (e.get("amp_circuit") or "").lower()
    if "x balanc" in ac or "x-balanc" in ac:
        ri = e.setdefault("restorer_info", {})
        rn = ri.get("recap_notes")
        if not rn or "X-BALANCED SAFETY" not in rn:
            ri["recap_notes"] = f"{WARN} | {rn}" if rn else WARN
            warned.append(e["jdm_model"])

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("AU-D907X ps_type ->", by_jm["AU-D907X"]["ps_type"])
print("D607X/G99X ps_type set to X-Balanced; AU-D907G amp_circuit ->", g["amp_circuit"])
print(f"8-terminal warning added to {len(warned)} X-Balanced models.")
