import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: audio-database.com JDM spec sheets
CIRC = "Integrated DC amp, alpha-X Balanced (LAPT)"
DATA = {
    "AU-alpha607L EXTRA": dict(watts_per_channel=90, freq_response_hz="DC-300000", thd_percent=0.003,
                               weight_kg=18.0, japan_price_kyen=85, amp_circuit=CIRC),
    "AU-alpha707L EXTRA": dict(watts_per_channel=130, freq_response_hz="DC-300000", thd_percent=0.003,
                               weight_kg=22.0, japan_price_kyen=145, amp_circuit=CIRC),
    "AU-alpha907L EXTRA": dict(watts_per_channel=160, freq_response_hz="DC-300000", thd_percent=0.003,
                               weight_kg=33.0, japan_price_kyen=250, amp_circuit=CIRC),
    "AU-alpha907DR":      dict(watts_per_channel=160, freq_response_hz="DC-300000", thd_percent=0.003,
                               weight_kg=33.0, japan_price_kyen=250, amp_circuit=CIRC),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:22s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
