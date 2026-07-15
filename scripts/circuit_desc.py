"""Add amp_circuit label + detailed circuit_description for AU-D907 and AU-X1.
Source: audio-database.com JDM catalogue pages.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

D907_DESC = (
    "Wide-range DC pre-main amplifier, direct-coupled throughout with FET inputs on every stage "
    "and no input capacitors in any block. The power amp runs three stages: a constant-current "
    "dual-FET input, Sansui's patent-pending Diamond operation circuit (dual complementary) to "
    "suppress TIM distortion, then a current-operation push-pull stage driving symmetrical Sansui "
    "Custom NM (Non-Magnetic) output transistors. The equalizer uses a diamond drive circuit and "
    "the flat/tone amp runs open-loop to minimise distortion. Fed by four independent supply "
    "systems (Penta-Power): a high-regulation twin-winding toroidal for the power amp, an EI "
    "transformer giving two independent supplies for the pre-drive stage, plus stabilised supplies "
    "for the MC head amp and the DC flat amp."
)
X1_DESC = (
    "Flagship DC integrated built around Sansui's diamond differential circuit, direct-coupled from "
    "input to output. The power stage uses a triple push-pull connection of then-new NM-LAPT "
    "(Non-Magnetic Linear Amplifier Power Transistor) devices held at optimised linear operating "
    "points to minimise distortion. Head amp: symmetrical push-pull DC amp with parallel low-noise "
    "FETs, direct-coupled input. Equalizer: direct-coupled DC amp with diamond differential and "
    "cascode bootstrap. Flat amp: push-pull drive DC amp with differential FET input. The power "
    "supply fills roughly half the chassis - eight supply configurations with independent left and "
    "right channels, a 600VA toroidal plus an 80VA EI transformer, 10,000uF x8 custom electrolytics "
    "and 1.2mm copper-plate grounding."
)

d = by["AU-D907"]
d["amp_circuit"] = "Wide-range DC pre-main, Diamond operation circuit, NM output transistors"
d["circuit_description"] = D907_DESC

x = by["AU-X1"]
x["amp_circuit"] = "DC integrated, diamond differential, triple push-pull NM-LAPT"
x["circuit_description"] = X1_DESC
# fill missing spec data from the same source
for k, v in dict(weight_kg=27.7, japan_price_kyen=210, freq_response_hz=None).items():
    if v is not None and x.get(k) in (None, ""):
        x[k] = v
        print(f"  AU-X1 {k} -> {v}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
for jm in ("AU-D907", "AU-X1"):
    e = by[jm]
    print(f"\n{jm}\n  amp_circuit: {e['amp_circuit']}\n  weight={e.get('weight_kg')} price={e.get('japan_price_kyen')}k")
