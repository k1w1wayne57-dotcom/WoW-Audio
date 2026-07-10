import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine / hifi-wiki / audio-database
DATA = {
    "CA-3000": dict(freq_response_hz="10-100000", thd_percent=0.03, weight_kg=13.9,
                    amp_circuit="Solid-state control preamplifier (Definition series)"),
    "BA-5000": dict(watts_per_channel=300, freq_response_hz="15-30000", thd_percent=0.1,
                    weight_kg=49,
                    amp_circuit="Solid-state power amp w/ output transformer, stereo/mono"),
    "BA-2000": dict(watts_per_channel=110, freq_response_hz="5-100000", thd_percent=0.03,
                    weight_kg=18.3, amp_circuit="Solid-state stereo power amplifier"),
    "AU-2900": dict(watts_per_channel=15, freq_response_hz="10-40000", thd_percent=0.3,
                    weight_kg=5.7, amp_circuit="Solid-state integrated amplifier"),
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
