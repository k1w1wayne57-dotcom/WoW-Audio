import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-alpha307": dict(watts_per_channel=65, freq_response_hz="1-200000", thd_percent=0.05,
                        weight_kg=9.0, japan_price_kyen=45,
                        amp_circuit="Integrated DC amp, alpha-X Balanced (entry model)"),
    "AU-alpha907i MOS LIMITED": dict(watts_per_channel=80, freq_response_hz="DC-300000",
                                     thd_percent=0.01, weight_kg=31, japan_price_kyen=260,
                                     amp_circuit="Integrated DC amp, alpha-X Balanced, MOS-FET output (Limited)"),
    "AU-alpha777DG": dict(watts_per_channel=90, freq_response_hz="DC-200000", thd_percent=0.003,
                          weight_kg=18.2, japan_price_kyen=96.5,
                          amp_circuit="Integrated DC amp, alpha-X Balanced (DG)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:26s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
