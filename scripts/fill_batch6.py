import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: audio-database.com (JDM), HiFi Engine/classicreceivers (5000X)
DATA = {
    "AU-666":  dict(watts_per_channel=35, freq_response_hz="10-70000", thd_percent=0.5,
                    weight_kg=9.75, japan_price_kyen=52.8,
                    amp_circuit="Solid-state, 2-stage differential + complementary Darlington"),
    "AU-6500": dict(watts_per_channel=28, freq_response_hz="10-40000", thd_percent=0.1,
                    weight_kg=11.5, japan_price_kyen=59.9,
                    amp_circuit="Solid-state, pure-complementary PNP-NPN"),
    "AU-7500": dict(watts_per_channel=32, freq_response_hz="10-50000", thd_percent=0.1,
                    weight_kg=12.7, japan_price_kyen=75.9,
                    amp_circuit="OCL pure-complementary, 3-stage direct-coupled"),
    "AU-9500": dict(watts_per_channel=75, freq_response_hz="3-80000", thd_percent=0.1,
                    weight_kg=23.3, japan_price_kyen=135,
                    amp_circuit="OCL pure-complementary, parallel push-pull"),
    "TU-999":  dict(weight_kg=10.1, japan_price_kyen=59.9,
                    amp_circuit="Dual-gate MOS FET FM front-end, 3-IC IF"),
    "TU-9500": dict(weight_kg=9.5, japan_price_kyen=74.8,
                    amp_circuit="Dual RF-stage FM front-end, DDC MPX decoder"),
    "5000X":   dict(watts_per_channel=60, freq_response_hz="10-50000", thd_percent=0.5,
                    weight_kg=15.1, amp_circuit="Solid-state AM/FM stereo receiver"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:8s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
