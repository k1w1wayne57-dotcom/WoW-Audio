"""B-2101 / B-2102 MOS Vintage / C-2102 topology + circuit detail.
Sources: Wayne (faceplates/knowledge), HiFi Engine / 1001hifi (B-2101), audio-database
(B-2102 MOS Vintage).
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

WARN = ("X-BALANCED SAFETY: both the red (+) and black (-) speaker terminals carry live, "
        "independent voltage. NEVER bridge/common the black terminals together, and NEVER "
        "connect a black terminal to chassis or an external/test ground - doing so shorts the "
        "floating balanced rails and instantly destroys the output transistors.")

# --- B-2101: X-Balanced (Wayne + sources) and twin-mono with three supplies
e = by["B-2101"]
e["amp_circuit"] = "X-Balanced stereo power amplifier, twin-mono, double parallel push-pull"
e["ps_type"] = "X-Balanced"
e["circuit_description"] = (
    "X-Balanced Amp System - circuitry that eliminates ground-related problems such as IHM "
    "distortion for a cleaner, crisper sound. Twin-mono construction with three power supplies "
    "keeps each channel physically and electrically separate. Output stage uses 16 oversized "
    "power transistors in a double parallel push-pull configuration. 200W RMS/ch; 2x350W into "
    "4 ohm (DIN) and 2x680W dynamic at 2 ohm. Fluorescent 24-segment peak level meters with "
    "peak hold, and separate L/R input attenuators.")
ri = e.setdefault("restorer_info", {})
rn = ri.get("recap_notes")
if not rn or "X-BALANCED SAFETY" not in rn:
    ri["recap_notes"] = f"{WARN} | {rn}" if rn else WARN

# --- B-2102 MOS Vintage: twin-monaural (dual mono) + NEW diamond differential + MOS-FET
m = by["B-2102 MOS Vintage"]
m["amp_circuit"] = "MOS-FET output, NEW diamond differential, twin-monaural construction"
m["ps_type"] = "Dual Mono"
m["circuit_description"] = (
    "Twin-monaural construction: the power amplifier blocks are arranged symmetrically so mutual "
    "interference between channels is eliminated. The NEW diamond differential circuit is used, "
    "with an FET cascade in the initial stage to reduce the effect of impedance differences "
    "between connected devices. MOS-FETs in the output stage give excellent frequency and "
    "transient characteristics. The supply uses custom-made heavy-duty transformers and a "
    "balanced power supply configuration forming a closed loop independent of the ground circuit. "
    "150W/ch at 6 ohm, 110W/ch at 8 ohm.")
mri = m.setdefault("restorer_info", {})
caution = ("CAUTION - check before grounding: the factory description states a balanced power "
           "supply forming a closed loop independent of the ground circuit. If the outputs are "
           "balanced-drive, the black (-) speaker terminals are live and must never be commoned "
           "together or tied to chassis/test ground. Confirm against the service manual before "
           "connecting a common ground.")
mrn = mri.get("recap_notes")
if not mrn or "CAUTION - check before grounding" not in (mrn or ""):
    mri["recap_notes"] = f"{caution} | {mrn}" if mrn else caution

# --- C-2102: semi-balanced architecture, high-grade parts (Wayne)
c = by["C-2102"]
c["amp_circuit"] = "Semi-balanced control (pre) amplifier, high-grade audio components"
c["circuit_description"] = (
    "Semi-balanced architecture built with high-grade audio components; widely regarded as one of "
    "Sansui's premium late-era audiophile products. Designed as the matching control amplifier for "
    "the B-2102.")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
for jm in ("B-2101", "B-2102 MOS Vintage", "C-2102"):
    x = by[jm]
    print(f"{jm:20s} ps={str(x.get('ps_type')):12s} circ={x.get('amp_circuit')}")
