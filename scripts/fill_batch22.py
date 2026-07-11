import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: audio-database / HiFi Engine / hifi-wiki
DATA = {
    "AU-alpha707": dict(watts_per_channel=130, freq_response_hz="1-300000", thd_percent=0.003,
                        weight_kg=20.5, amp_circuit="Integrated DC amp, alpha-X Balanced"),
    "AU-alpha907": dict(watts_per_channel=180, freq_response_hz="DC-300000", thd_percent=0.003,
                        amp_circuit="Integrated DC amp, alpha-X Balanced (190W @ 6ohm)"),
    "AU-X11":      dict(watts_per_channel=160, freq_response_hz="5-100000", thd_percent=0.003,
                        amp_circuit="Super integrated amplifier (JDM flagship)"),
    "B-2301":      dict(watts_per_channel=300, freq_response_hz="1-300000", thd_percent=0.003,
                        weight_kg=37, amp_circuit="Stereo power amplifier"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:13s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
