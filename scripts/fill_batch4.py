import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine, audio-database (TU-555), classicreceivers
DATA = {
    "3000":   dict(watts_per_channel=45, freq_response_hz="20-20000", thd_percent=0.8,
                   amp_circuit="Solid-state AM/FM stereo receiver"),
    "800":    dict(watts_per_channel=22, freq_response_hz="20-30000", thd_percent=0.8,
                   weight_kg=10.2, amp_circuit="Solid-state AM/FM stereo receiver"),
    "5000A":  dict(watts_per_channel=55, freq_response_hz="20-30000", thd_percent=0.8,
                   weight_kg=13.2, amp_circuit="Solid-state AM/FM stereo receiver"),
    "2000A":  dict(watts_per_channel=35, freq_response_hz="20-20000", thd_percent=0.8,
                   amp_circuit="Solid-state AM/FM stereo receiver"),
    "400":    dict(watts_per_channel=20, freq_response_hz="20-30000", thd_percent=1.0,
                   weight_kg=10.4, amp_circuit="Solid-state AM/FM stereo receiver"),
    "TU-555": dict(weight_kg=3.9, japan_price_kyen=28.9,
                   amp_circuit="FET FM front-end, 4-stage IF, 3-stage limiter"),
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
