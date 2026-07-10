import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / hifi-wiki / audio-database
DATA = {
    "AU-D9":   dict(freq_response_hz="10-20000", thd_percent=0.005,
                    amp_circuit="DC integrated, Super Feedforward"),
    "AU-D7":   dict(watts_per_channel=80, freq_response_hz="20-20000", thd_percent=0.02,
                    weight_kg=11.3, amp_circuit="Linear A + DD/DC integrated"),
    "AU-D101": dict(watts_per_channel=30, freq_response_hz="20-20000", thd_percent=0.008,
                    amp_circuit="Super Feedforward integrated amplifier"),
    "AU-D33":  dict(watts_per_channel=50, freq_response_hz="20-20000", thd_percent=0.004,
                    weight_kg=8.3, amp_circuit="Super Feedforward integrated amplifier"),
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
