"""Fill AU-D707 (was entirely specless after the '/' split) + mirror to its export twin AU-819.
Source: audio-database.com/SANSUI/amp/au-d707.-e.html
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

LABEL = "DC pre-main (3 DC amp config), diamond complementary dual-differential, NM transistors"
DESC = (
    "DC pre-main amplifier in a '3 DC amplifier' configuration - equalizer, flat/tone and power "
    "stages are all direct-coupled with no input capacitors. The input uses low-noise, high-gm FETs "
    "in a full push-pull input circuit. The power amp's second stage is a diamond complementary "
    "circuit using dual differential, driving Sansui Custom NM (Non-Magnetic) transistors in a SEPP "
    "output stage with Darlington connection. The MC head amp is fully symmetrical push-pull; the "
    "equalizer uses a diamond differential circuit with dual-FET cascode bootstrap and "
    "constant-current loading. Power comes from a single EI transformer carrying two dedicated "
    "windings and two rectifier circuits for complete left/right channel independence, plus a "
    "separate dedicated winding for the preamp, with 15,000uF x4 of filtering."
)
# One transformer with per-channel windings/rectifiers = independent rails, NOT dual mono
# (dual mono needs a transformer per channel) and NOT Penta-Power (that is stage-split, 2 xfmrs).
PS = "Dual Power Supply"

d = by["AU-D707"]
d.update({
    "watts_per_channel": 90, "freq_response_hz": "DC-500000", "thd_percent": 0.008,
    "weight_kg": 20.1, "japan_price_kyen": 95, "year_start": 1979,
    "ps_type": PS, "amp_circuit": LABEL, "circuit_description": DESC,
})
d.setdefault("links", {})["audio_database"] = "https://audio-database.com/SANSUI/amp/au-d707.-e.html"

# export twin: same amp, same circuit. Its amp_circuit wrongly said "dual-mono".
x = by["AU-819"]
x["amp_circuit"] = LABEL
x["circuit_description"] = DESC
x["ps_type"] = PS
ci = x.setdefault("collector_info", {})
n = "Multi-voltage export twin of the JDM AU-D707 - same amp; slightly heavier export transformer."
ci["collector_notes"] = f"{ci.get('collector_notes')} | {n}" if ci.get("collector_notes") else n

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
for jm in ("AU-D707", "AU-819"):
    e = by[jm]
    print(f"{jm}: {e.get('watts_per_channel')}W thd={e.get('thd_percent')} {e.get('weight_kg')}kg "
          f"JPY{e.get('japan_price_kyen')}k ps={e.get('ps_type')}")
