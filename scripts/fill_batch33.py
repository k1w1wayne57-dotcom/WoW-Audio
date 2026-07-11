import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-G99X": dict(watts_per_channel=160, freq_response_hz="DC-300000", thd_percent=0.003,
                    weight_kg=17.3, amp_circuit="G-X Balanced integrated amplifier"),
    "AU-D607F Extra": dict(watts_per_channel=80, thd_percent=0.003, japan_price_kyen=78,
                           amp_circuit="Super Feedforward, diamond differential (as AU-D707F Extra)"),
    "AU-D22": dict(watts_per_channel=35, freq_response_hz="20-20000", thd_percent=0.006,
                   weight_kg=6.8, amp_circuit="Super Feedforward DC integrated"),
    "B-2201": dict(watts_per_channel=200, thd_percent=0.003, weight_kg=36.0,
                   amp_circuit="Stereo power amplifier (480W @ 4ohm)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:16s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
