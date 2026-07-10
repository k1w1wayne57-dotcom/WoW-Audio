import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine, hifi-wiki, classicreceivers, radiomuseum
DATA = {
    "AU-101": dict(watts_per_channel=15, freq_response_hz="20-60000", thd_percent=0.8,
                   weight_kg=5.9, amp_circuit="Solid-state integrated (18 transistors)"),
    "AU-505": dict(watts_per_channel=12, freq_response_hz="20-60000", thd_percent=0.5,
                   weight_kg=8, amp_circuit="Solid-state integrated (23 transistors)"),
    "3000A": dict(watts_per_channel=45, freq_response_hz="20-20000", thd_percent=0.8,
                  weight_kg=15.6, amp_circuit="Solid-state AM/FM stereo receiver"),
    "5000":  dict(watts_per_channel=65, thd_percent=0.5, weight_kg=18.1,
                  amp_circuit="Solid-state AM/FM stereo receiver"),
    "350":   dict(watts_per_channel=20, freq_response_hz="30-30000", thd_percent=1.0,
                  weight_kg=9.5, amp_circuit="Solid-state AM/FM stereo receiver"),
    "1000A": dict(watts_per_channel=40, freq_response_hz="20-20000", thd_percent=0.8,
                  weight_kg=20.3, amp_circuit="Tube FM-multiplex stereo receiver"),
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
