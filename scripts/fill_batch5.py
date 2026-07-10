import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "4000": dict(watts_per_channel=45, thd_percent=0.8,
                 amp_circuit="Solid-state AM/FM stereo receiver (45 tr, 4 IC)"),
    "BA-90": dict(watts_per_channel=28, freq_response_hz="15-100000", thd_percent=0.3,
                  amp_circuit="Solid-state basic (power) amplifier"),
    "220": dict(amp_circuit="Tube AM/FM stereo receiver (12 tubes)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:8s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
