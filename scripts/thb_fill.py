"""Fill gaps on Thai-priced models; merge the BA-2102 duplicate into B-2102."""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

# --- merge duplicate: "BA-2102" is a mis-transcription of B-2102 (BA- was the 70s power-amp
# prefix; the 1986 X-Balanced power amp is B-2102). Same specs confirm it. Keep B-2102.
dup, keep = by.get("BA-2102"), by.get("B-2102")
if dup and keep:
    for p in dup.get("price_thb_listings") or []:
        keep.setdefault("price_thb_listings", []).append(p)
    keep["last_price_check"] = dup.get("last_price_check") or keep.get("last_price_check")
    db.remove(dup)
    print(f"merged BA-2102 -> B-2102; B-2102 THB now {keep['price_thb_listings']}")

DATA = {
    "AU-5500":  dict(watts_per_channel=35, freq_response_hz="10-40000", thd_percent=0.2,
                     weight_kg=10.4, amp_circuit="Solid-state integrated amplifier"),
    "QRX-3500": dict(watts_per_channel=22, freq_response_hz="30-30000", thd_percent=0.5,
                     amp_circuit="4-channel quad receiver, QS matrix"),
    "QRX-5500": dict(watts_per_channel=22, freq_response_hz="30-30000", thd_percent=0.3,
                     weight_kg=21.8, amp_circuit="4-channel quad receiver, QS matrix"),
}
for jm, fields in DATA.items():
    e = by.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    ch = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    print(f"  {jm:10s} filled: {', '.join(ch)}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("entries:", len(db))
