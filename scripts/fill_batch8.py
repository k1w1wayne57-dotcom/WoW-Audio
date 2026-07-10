import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: audio-database.com JDM spec sheets
DATA = {
    "AU-9900":  dict(watts_per_channel=80, freq_response_hz="10-50000", thd_percent=0.08,
                     weight_kg=17.9, japan_price_kyen=140,
                     amp_circuit="Pure-complementary OCL, differential amplifier"),
    "AU-6600":  dict(watts_per_channel=40, freq_response_hz="10-40000", thd_percent=0.15,
                     weight_kg=11.3, japan_price_kyen=79.8,
                     amp_circuit="OCL, differential amplifier stages"),
    "AU-7700":  dict(watts_per_channel=52, freq_response_hz="10-50000", thd_percent=0.1,
                     weight_kg=12.3, japan_price_kyen=99.8,
                     amp_circuit="3-stage Darlington drive, parallel push-pull"),
    "AU-11000": dict(watts_per_channel=110, freq_response_hz="10-50000", thd_percent=0.08,
                     weight_kg=19.3, japan_price_kyen=180,
                     amp_circuit="OCL, differential + parallel push-pull"),
    "AU-20000": dict(watts_per_channel=170, freq_response_hz="10-50000", thd_percent=0.05,
                     weight_kg=23.6, japan_price_kyen=280,
                     amp_circuit="Pure OCL, triple push-pull complementary (170W @ 4.8ohm)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:9s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
