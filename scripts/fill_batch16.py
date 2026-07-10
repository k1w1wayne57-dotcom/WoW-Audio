import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / hifi-wiki
DATA = {
    "AU-417": dict(watts_per_channel=65, freq_response_hz="5-100000", thd_percent=0.02,
                   weight_kg=12.2, amp_circuit="DC integrated (single PSU), like AU-517"),
    "AU-819": dict(watts_per_channel=90, freq_response_hz="10-20000", thd_percent=0.008,
                   weight_kg=21.1, amp_circuit="DC integrated amplifier, dual-mono"),
    "AU-719": dict(watts_per_channel=80, freq_response_hz="20-20000", thd_percent=0.08,
                   weight_kg=16, amp_circuit="DC integrated amplifier"),
    "AU-519": dict(watts_per_channel=70, freq_response_hz="10-20000", thd_percent=0.008,
                   amp_circuit="DC integrated amplifier"),
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
