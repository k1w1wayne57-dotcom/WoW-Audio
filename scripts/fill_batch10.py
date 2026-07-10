import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# BA-60 = user-supplied (thevintageknob/audioequipment). Others: HiFi Engine / search.
DATA = {
    "BA-60":   dict(watts_per_channel=20, freq_response_hz="20-60000", thd_percent=0.3,
                    weight_kg=4.2, amp_circuit="Solid-state stereo power amplifier (13 transistors)"),
    "250":     dict(watts_per_channel=8, freq_response_hz="30-20000", thd_percent=1.5,
                    amp_circuit="Tube AM/FM-multiplex receiver (15 tubes + 12 tr)"),
    "500":     dict(watts_per_channel=13, freq_response_hz="20-20000", thd_percent=1.0,
                    amp_circuit="Tube FM-multiplex stereo receiver"),
    "SAX-200": dict(watts_per_channel=13, thd_percent=1.0,
                    amp_circuit="Tube AM/FM-multiplex stereo receiver"),
    "SAX-100": dict(amp_circuit="Tube AM/FM-multiplex stereo receiver (6BM8 push-pull)"),
    "SM-12M":  dict(amp_circuit="Tube MW/SW/FM tuner-amplifier (10 tubes)"),
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
