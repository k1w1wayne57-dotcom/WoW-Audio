import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

# Source: audio-database (907X) / HiFi Engine / hifi-wiki
DATA = {
    "AU-D907X": dict(watts_per_channel=160, freq_response_hz="DC-300000", thd_percent=0.003,
                     weight_kg=20.5, japan_price_kyen=189,
                     amp_circuit="X-Balanced DC integrated, twin diamond differential"),
    "AU-D907G": dict(freq_response_hz="DC-300000", thd_percent=0.003,
                     amp_circuit="X-Balanced DC integrated (Super Feedforward)"),
    "AU-D77X":  dict(amp_circuit="X-Balanced 'Super GF' integrated (Ground-Free circuit)"),
    "AU-D55X":  dict(freq_response_hz="20-20000", thd_percent=0.004,
                     amp_circuit="X-Balanced integrated amplifier"),
    "AU-D11II": dict(freq_response_hz="10-20000", thd_percent=0.0028,
                     amp_circuit="DC integrated amplifier (flagship)"),
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
