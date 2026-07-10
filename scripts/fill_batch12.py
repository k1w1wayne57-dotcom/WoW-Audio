import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine / hifi-wiki
DATA = {
    "AU-317":  dict(freq_response_hz="5-70000", thd_percent=0.03, weight_kg=9.5,
                    amp_circuit="DC integrated amplifier"),
    "AU-3900": dict(watts_per_channel=22, freq_response_hz="10-40000", thd_percent=0.15,
                    amp_circuit="Solid-state integrated amplifier"),
    "BA-3000": dict(watts_per_channel=170, freq_response_hz="20-20000", thd_percent=0.05,
                    amp_circuit="Solid-state stereo power amplifier (finned heatsinks)"),
    "9090DB":  dict(freq_response_hz="10-30000",
                    amp_circuit="Solid-state AM/FM stereo receiver, Dolby FM"),
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
