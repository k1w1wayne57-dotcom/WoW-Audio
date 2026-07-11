import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-X1111 MOS": dict(watts_per_channel=110, freq_response_hz="1-300000", thd_percent=0.008,
                         weight_kg=35.1, japan_price_kyen=400,
                         amp_circuit="Master integrated, 16x MOS-FET diamond power stage"),
    "AU-alpha607NRA II": dict(watts_per_channel=80, freq_response_hz="20-20000", thd_percent=0.003,
                              weight_kg=19, japan_price_kyen=119,
                              amp_circuit="Integrated DC amp, alpha-X Balanced (LAPT)"),
    "AU-X711": dict(watts_per_channel=100,
                    amp_circuit="X-Balanced integrated amplifier"),
    "AU-alpha999DG": dict(watts_per_channel=95, freq_response_hz="DC-200000", thd_percent=0.003,
                          weight_kg=19.6, japan_price_kyen=135,
                          amp_circuit="Integrated DC amp, alpha-X Balanced (DG)"),
    "AU-X111 MOS": dict(watts_per_channel=110, freq_response_hz="DC-300000", thd_percent=0.008,
                        weight_kg=32.1, japan_price_kyen=330,
                        amp_circuit="Master integrated, MOS-FET output (X111 MOS Vintage)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:18s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
