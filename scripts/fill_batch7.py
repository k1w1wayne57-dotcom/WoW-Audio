import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: audio-database.com (QRX-3000, TU-7500), HiFi Engine / classicreceivers
DATA = {
    "QRX-3000": dict(watts_per_channel=8, freq_response_hz="30-30000", thd_percent=0.5,
                     weight_kg=11.5, japan_price_kyen=99.8,
                     amp_circuit="4-channel quad receiver, QS matrix (8W x4 @ 8ohm)"),
    "QRX-6500": dict(watts_per_channel=33, weight_kg=22,
                     amp_circuit="4-channel quad receiver, QS vario-matrix + CD-4/SQ"),
    "QRX-7500": dict(watts_per_channel=30, freq_response_hz="30-30000", thd_percent=0.3,
                     weight_kg=22,
                     amp_circuit="4-channel quad receiver, CD-4/SQ/QS decoders"),
    "350A":     dict(watts_per_channel=20, freq_response_hz="30-30000", thd_percent=1.0,
                     weight_kg=9, amp_circuit="Solid-state AM/FM stereo receiver"),
    "1000X":    dict(watts_per_channel=28, freq_response_hz="20-30000", thd_percent=0.8,
                     weight_kg=10.3, amp_circuit="Solid-state AM/FM stereo receiver"),
    "TU-7500":  dict(weight_kg=8, japan_price_kyen=54.3,
                     amp_circuit="DDC MOS FET FM front-end, ceramic-filter IF"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:9s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
