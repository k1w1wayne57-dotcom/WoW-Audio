import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "AU-D707F Extra": dict(watts_per_channel=100, thd_percent=0.003, japan_price_kyen=113,
                           amp_circuit="Super Feedforward, diamond differential"),
    "AU-D55F": dict(watts_per_channel=50, thd_percent=0.004, weight_kg=7.3,
                    amp_circuit="Super Feedforward integrated amplifier"),
    "5900Z": dict(watts_per_channel=75, freq_response_hz="5-100000", thd_percent=0.03,
                  weight_kg=9.5, amp_circuit="Digital-synthesizer DC stereo receiver"),
    "B-2201L": dict(watts_per_channel=200, thd_percent=0.003, weight_kg=36.0,
                    amp_circuit="Stereo power amplifier (B-2201 luxury version)"),
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
