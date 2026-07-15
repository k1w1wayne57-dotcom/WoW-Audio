import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

DATA = {
    "QR-6500": dict(watts_per_channel=37, freq_response_hz="20-30000", thd_percent=0.5,
                    weight_kg=22, amp_circuit="4-channel quad receiver (37W x4 @ 8ohm)"),
    "AU-X1":   dict(freq_response_hz="DC-500000", thd_percent=0.007),
    "G-5000":  dict(freq_response_hz="5-50000", weight_kg=14),
}
for jm, fields in DATA.items():
    e = by.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    ch = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:10s} filled: {', '.join(ch) if ch else '(already set)'}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
