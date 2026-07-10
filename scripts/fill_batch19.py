import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: HiFi Engine / audio-database / hifi-wiki
DATA = {
    "AU-D907F": dict(watts_per_channel=130, freq_response_hz="10-20000", thd_percent=0.003,
                     weight_kg=17.7, amp_circuit="DC integrated, super-feedforward (Diamond differential)"),
    "AU-D707F": dict(watts_per_channel=100, freq_response_hz="10-20000", thd_percent=0.008,
                     amp_circuit="DC integrated, super-feedforward"),
    "AU-D607X": dict(watts_per_channel=90, freq_response_hz="1-300000", thd_percent=0.003,
                     weight_kg=15, amp_circuit="X-Balanced integrated amplifier"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:11s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
