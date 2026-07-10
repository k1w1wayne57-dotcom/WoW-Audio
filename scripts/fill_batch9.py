import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Sources: HiFi Engine (AU-517, 8080, 9090, 6060), audio-database (CA-2000)
DATA = {
    "AU-517":  dict(watts_per_channel=65, freq_response_hz="20-20000", thd_percent=0.025,
                    weight_kg=16.5, amp_circuit="DC integrated, dual-mono construction"),
    "9090":    dict(freq_response_hz="20-20000",
                    amp_circuit="Solid-state AM/FM stereo receiver"),
    "CA-2000": dict(freq_response_hz="10-80000", thd_percent=0.03, weight_kg=9.9,
                    japan_price_kyen=80,
                    amp_circuit="Class-A push-pull preamplifier, differential input"),
    "8080":    dict(watts_per_channel=80, freq_response_hz="10-30000", thd_percent=0.2,
                    weight_kg=20.9, amp_circuit="Solid-state AM/FM stereo receiver"),
    "6060":    dict(watts_per_channel=44, freq_response_hz="15-40000", thd_percent=0.4,
                    weight_kg=11.4, amp_circuit="Solid-state AM/FM stereo receiver"),
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
