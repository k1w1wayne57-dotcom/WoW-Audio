import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / hifi-wiki
DATA = {
    "AU-117":   dict(watts_per_channel=15, freq_response_hz="10-40000", thd_percent=0.17,
                     weight_kg=6.4, amp_circuit="Solid-state integrated amplifier"),
    "AU-217II": dict(watts_per_channel=40, freq_response_hz="20-20000", thd_percent=0.06,
                     weight_kg=8.3, amp_circuit="Solid-state integrated amplifier"),
    "AU-317II": dict(watts_per_channel=60, freq_response_hz="20-20000", thd_percent=0.03,
                     weight_kg=9.8, amp_circuit="DC integrated amplifier"),
    "AU-2200":  dict(watts_per_channel=10, freq_response_hz="30-22000", thd_percent=0.8,
                     weight_kg=5.5, amp_circuit="Solid-state integrated amplifier"),
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
