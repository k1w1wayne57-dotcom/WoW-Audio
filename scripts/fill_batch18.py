import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / hifi-wiki
DATA = {
    "5050":   dict(watts_per_channel=30, freq_response_hz="15-40000", thd_percent=0.5,
                   weight_kg=10.1, amp_circuit="Solid-state AM/FM stereo receiver"),
    "8080DB": dict(watts_per_channel=85, freq_response_hz="10-30000", thd_percent=0.1,
                   amp_circuit="Solid-state AM/FM stereo receiver, Dolby FM"),
    "441":    dict(watts_per_channel=11, freq_response_hz="25-30000", thd_percent=1.0,
                   weight_kg=7.7, amp_circuit="Solid-state AM/FM stereo receiver"),
    "331":    dict(watts_per_channel=12, freq_response_hz="20-30000", thd_percent=1.0,
                   weight_kg=5.7, amp_circuit="Solid-state AM/FM stereo receiver"),
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
