import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-222":  dict(watts_per_channel=18, freq_response_hz="20-30000", thd_percent=0.8,
                    weight_kg=5.8, japan_price_kyen=28.7,
                    amp_circuit="All-silicon transistor, complementary Darlington SEPP"),
    "AU-777D": dict(watts_per_channel=30, freq_response_hz="20-100000", thd_percent=0.5,
                    weight_kg=12.5, japan_price_kyen=59.5,
                    amp_circuit="Solid-state, quasi-complementary Darlington"),
    "AU-555A": dict(watts_per_channel=25, freq_response_hz="20-40000", thd_percent=0.5,
                    weight_kg=8, japan_price_kyen=41.8,
                    amp_circuit="All-silicon transistor, SEPP-ITL-OTL"),
    "CA-303":  dict(freq_response_hz="10-50000", thd_percent=0.1, weight_kg=10,
                    japan_price_kyen=88,
                    amp_circuit="Tube/transistor hybrid preamp (6 tubes, 2 tr)"),
    "BA-202":  dict(watts_per_channel=11, freq_response_hz="20-30000", thd_percent=0.5,
                    weight_kg=14, japan_price_kyen=42.2,
                    amp_circuit="Tube power amp (6AQ8x2, 12AU7x2, 6RAx4)"),
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
