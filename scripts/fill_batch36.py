import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

DATA = {
    "B2105V": dict(watts_per_channel=110, freq_response_hz="10-20000", thd_percent=0.008,
                   amp_circuit="MOS-FET power amp (50th-anniversary, last 2SK405/2SJ115 model)"),
    "C-2105V": dict(freq_response_hz="20-20000", weight_kg=16.5, japan_price_kyen=380,
                    amp_circuit="Control preamp (50th-anniversary, pairs with B-2105)"),
    "B-209 The Tube": dict(watts_per_channel=30, thd_percent=0.5, weight_kg=24.5,
                           amp_circuit="Tube power amp, 6L6GC push-pull (limited 200 units, George Kaye design)"),
}
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:16s} filled: {', '.join(changed)}")
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
