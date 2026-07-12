import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

PPDC = "Pure Power DC stereo receiver"
DATA = {
    "G-7500":   dict(watts_per_channel=90, freq_response_hz="5-50000", thd_percent=0.025,
                     weight_kg=17.2, amp_circuit=PPDC),
    "G-4500":   dict(watts_per_channel=40, freq_response_hz="10-50000", thd_percent=0.1,
                     weight_kg=13.6, amp_circuit=PPDC),
    "G-4700":   dict(watts_per_channel=50, freq_response_hz="10-70000", thd_percent=0.05,
                     weight_kg=8.6, amp_circuit=PPDC),
    "G-8700DB": dict(thd_percent=0.025, weight_kg=24.9, amp_circuit=PPDC + ", Dolby FM",
                     ps_type="Dual Mono"),
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
