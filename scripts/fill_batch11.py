import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine / hifi-wiki (AU-*), audio-database (TU-9900)
DATA = {
    "AU-717":  dict(watts_per_channel=85, freq_response_hz="20-20000", thd_percent=0.025,
                    weight_kg=17.8, amp_circuit="DC integrated, dual-mono construction"),
    "AU-5900": dict(watts_per_channel=45, freq_response_hz="5-40000", thd_percent=0.1,
                    weight_kg=11.5, amp_circuit="Solid-state integrated, parallel push-pull"),
    "AU-6900": dict(watts_per_channel=60, freq_response_hz="5-40000", thd_percent=0.1,
                    amp_circuit="Solid-state integrated, parallel push-pull, triple tone control"),
    "AU-919":  dict(watts_per_channel=100, freq_response_hz="20-20000", thd_percent=0.008,
                    weight_kg=21.4, amp_circuit="DC integrated, dual-mono, super-feedforward"),
    "TU-9900": dict(weight_kg=9.6, japan_price_kyen=89.8,
                    amp_circuit="MOS FET FM front-end, 6-pole block filter"),
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
