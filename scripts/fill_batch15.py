import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / hifi-wiki
DATA = {
    "AU-7900": dict(watts_per_channel=75, freq_response_hz="5-40000", thd_percent=0.1,
                    weight_kg=14.2, amp_circuit="Solid-state integrated, parallel push-pull"),
    "AU-4400": dict(watts_per_channel=20, freq_response_hz="20-30000", thd_percent=0.5,
                    weight_kg=6.5, amp_circuit="Solid-state integrated amplifier"),
    "AU-217":  dict(watts_per_channel=30, freq_response_hz="10-50000", thd_percent=0.06,
                    weight_kg=8.4, amp_circuit="Solid-state integrated amplifier"),
    "AU-4900": dict(watts_per_channel=38, freq_response_hz="10-40000", thd_percent=0.15,
                    weight_kg=7.7, amp_circuit="Solid-state integrated amplifier"),
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
