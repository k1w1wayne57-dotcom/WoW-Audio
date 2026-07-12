import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

PPDC = "Pure Power DC stereo receiver"
DATA = {
    "G-9000":   dict(freq_response_hz="0-200000", thd_percent=0.02, weight_kg=27.2,
                     amp_circuit=PPDC, ps_type="Dual Mono"),
    "G-9000DB": dict(freq_response_hz="0-200000", thd_percent=0.03, weight_kg=28,
                     amp_circuit=PPDC + ", Dolby FM", ps_type="Dual Mono"),
    "G-33000":  dict(thd_percent=0.005,
                     amp_circuit="Pure Power Straight DC receiver (two-piece, forced-air cooled)",
                     ps_type="Dual Mono"),
    "G-22000":  dict(freq_response_hz="5-50000", thd_percent=0.009, weight_kg=42.1,
                     amp_circuit="Pure Power Straight DC receiver (two-piece, Diamond Differential)",
                     ps_type="Dual Mono"),
    "G-8000":   dict(freq_response_hz="5-50000", thd_percent=0.03, weight_kg=24.6, amp_circuit=PPDC),
    "G-7000":   dict(thd_percent=0.03, amp_circuit=PPDC),
    "G-6000":   dict(freq_response_hz="5-50000", thd_percent=0.03, weight_kg=17.5, amp_circuit=PPDC),
    "G-5000":   dict(thd_percent=0.03, amp_circuit=PPDC),
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
