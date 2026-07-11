import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "B-2103 MOS VINTAGE": dict(watts_per_channel=110, freq_response_hz="DC-300000",
                               thd_percent=0.008, weight_kg=35.0, japan_price_kyen=360,
                               amp_circuit="MOS-FET stereo power amp, alpha-X Balanced"),
    "B-2302V": dict(watts_per_channel=300, freq_response_hz="1-300000", thd_percent=0.003,
                    weight_kg=46.0, japan_price_kyen=740,
                    amp_circuit="Stereo power amplifier (Vintage flagship)"),
    "C-2302V": dict(weight_kg=26, japan_price_kyen=1280,
                    amp_circuit="Fully-balanced control preamp, dual MC transformers (Vintage)"),
    "AU-111 VINTAGE": dict(watts_per_channel=40, freq_response_hz="10-50000",
                           weight_kg=25,
                           amp_circuit="Tube pre-main (1999 reissue of the 1965 AU-111)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:20s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
