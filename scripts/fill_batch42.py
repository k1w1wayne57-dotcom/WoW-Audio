import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

PPDC = "Pure Power DC stereo receiver"
DATA = {
    "G-7700":  dict(watts_per_channel=120, freq_response_hz="5-75000", thd_percent=0.025,
                    weight_kg=18, amp_circuit=PPDC),
    "G-9700":  dict(watts_per_channel=200, freq_response_hz="5-80000", thd_percent=0.02,
                    weight_kg=22.2, amp_circuit=PPDC),
    "G-3500":  dict(watts_per_channel=26, freq_response_hz="10-50000", thd_percent=0.1,
                    weight_kg=8.5, amp_circuit="Solid-state AM/FM stereo receiver"),
    "G-33000": dict(weight_kg=45.4),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:10s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
