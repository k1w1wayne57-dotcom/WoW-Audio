import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine / hifi-wiki
DATA = {
    "771":    dict(watts_per_channel=32, freq_response_hz="15-30000", thd_percent=0.5,
                   weight_kg=12, amp_circuit="Solid-state AM/FM stereo receiver"),
    "881":    dict(watts_per_channel=60, freq_response_hz="10-30000", thd_percent=0.3,
                   weight_kg=13.2, amp_circuit="Solid-state AM/FM stereo receiver"),
    "551":    dict(watts_per_channel=16, freq_response_hz="15-30000", thd_percent=0.8,
                   weight_kg=7.7, amp_circuit="Solid-state AM/FM stereo receiver"),
    "661":    dict(watts_per_channel=20, freq_response_hz="15-30000", thd_percent=0.5,
                   weight_kg=10, amp_circuit="Solid-state AM/FM receiver, direct-coupled OCL"),
    "TU-717": dict(weight_kg=9.2, amp_circuit="AM/FM tuner, dual-bandwidth IF (1.7uV sens.)"),
    "TU-517": dict(weight_kg=8.7, amp_circuit="AM/FM tuner, dual-bandwidth IF (1.7uV sens.)"),
    "TU-217": dict(weight_kg=5.3, amp_circuit="AM/FM tuner, MOS FET front-end"),
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
