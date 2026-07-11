import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-alpha607 MOS PREMIUM": dict(watts_per_channel=45, freq_response_hz="DC-300000",
                                    thd_percent=0.008, weight_kg=18.8, japan_price_kyen=138,
                                    amp_circuit="Integrated DC amp, alpha-X Balanced, MOS-FET Class-A"),
    "AU-alpha607 MOS LIMITED": dict(watts_per_channel=50, freq_response_hz="DC-300000",
                                    thd_percent=0.008, weight_kg=22.5, japan_price_kyen=180,
                                    amp_circuit="Integrated DC amp, alpha-X Balanced, MOS-FET (Limited)"),
    "AU-alpha907": dict(weight_kg=28),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:24s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
