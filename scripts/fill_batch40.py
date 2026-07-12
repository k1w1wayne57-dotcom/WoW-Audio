import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

PPDC = "Pure Power DC stereo receiver"
SS = "Solid-state AM/FM stereo receiver"
DATA = {
    "G-6700": dict(watts_per_channel=90, freq_response_hz="5-75000", thd_percent=0.025,
                   weight_kg=16.1, amp_circuit=PPDC, ps_type="Dual Mono"),
    "G-5500": dict(watts_per_channel=60, thd_percent=0.03, weight_kg=12.8, amp_circuit=PPDC),
    "G-2000": dict(freq_response_hz="10-50000", thd_percent=0.15, weight_kg=7.3, amp_circuit=SS),
    "G-3000": dict(watts_per_channel=26, freq_response_hz="10-50000", thd_percent=0.15,
                   weight_kg=8, amp_circuit=SS),
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
