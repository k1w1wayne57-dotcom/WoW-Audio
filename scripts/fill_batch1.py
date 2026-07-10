"""Fill researched specs for the oldest models (batch 1). Sources: audio-database.com
(JDM spec sheets), hifi-wiki, hifiengine. Only fills fields that are currently null;
never overwrites existing non-null data. verified stays false.
"""
import json
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# keyed by jdm_model (all unique now). Values only set where currently null.
DATA = {
    "AU-111": dict(watts_per_channel=40, freq_response_hz="20-50000", thd_percent=0.8,
                   weight_kg=24.5, japan_price_kyen=65,
                   amp_circuit="Tube pre-main, PP fixed-bias (4x 6L6GC), multiple NFB"),
    "AU-70":  dict(watts_per_channel=25, freq_response_hz="10-80000", thd_percent=0.15,
                   weight_kg=13.7, japan_price_kyen=42,
                   amp_circuit="Tube pre-main (4x 7189), multiple NFB 26dB"),
    "AU-777": dict(watts_per_channel=25, freq_response_hz="20-100000", thd_percent=0.5,
                   weight_kg=12.3, japan_price_kyen=57,
                   amp_circuit="All-silicon transistor (26 tr), SEPP output"),
    "AU-999": dict(watts_per_channel=80, freq_response_hz="5-100000", thd_percent=0.4,
                   weight_kg=17.5, japan_price_kyen=85,
                   amp_circuit="Solid-state, 2-stage differential, fully direct-coupled"),
    "AU-555": dict(watts_per_channel=20, freq_response_hz="20-80000", thd_percent=0.5,
                   weight_kg=7.9, japan_price_kyen=37.5,
                   amp_circuit="Solid-state SEPP-ITL-OTL, complementary Darlington"),
    "1000":   dict(watts_per_channel=35, weight_kg=18.5,
                   amp_circuit="Tube, FM-multiplex stereo receiver"),
    "2000":   dict(watts_per_channel=30, freq_response_hz="20-20000", weight_kg=12,
                   amp_circuit="Solid-state stereo receiver"),
}

by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)

filled = []
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print(f"  !! {jm} not found"); continue
    changed = []
    for k, v in fields.items():
        if e.get(k) in (None, ""):
            e[k] = v
            changed.append(k)
    filled.append((jm, changed))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

for jm, changed in filled:
    print(f"  {jm:10s} filled: {', '.join(changed) if changed else '(all already set)'}")
