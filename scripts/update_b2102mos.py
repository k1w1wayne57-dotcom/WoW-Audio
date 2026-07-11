import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

e = next((x for x in db if x["jdm_model"] in ("B-2102 MOS", "B-2102 MOS Vintage")), None)
if not e:
    print("B-2102 MOS not found"); raise SystemExit

e["jdm_model"] = "B-2102 MOS Vintage"
e["type"] = "Power Amp"
e["japan_price_kyen"] = 350
e["watts_per_channel"] = 110          # 8 ohm rated (150W @ 6 ohm)
e["freq_response_hz"] = "DC-300000"
e["thd_percent"] = 0.008
e["amp_circuit"] = "MOS-FET output stereo power amplifier"
e["weight_kg"] = 35.0
e["special_features"] = ("MOS-FET output stage; 150W+150W @ 6ohm; damping factor 200; "
                         "slew rate 150V/us; subsonic filter 10Hz; power 350W; dims 450 x 176 x 477 mm")
e["verified"] = True
e["year_source"] = "user (spec sheet)"

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("updated:", e["jdm_model"], e["watts_per_channel"], "W,", e["weight_kg"], "kg, JPY", e["japan_price_kyen"], "k")
