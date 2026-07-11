import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

e = next((x for x in db if x["jdm_model"] == "AU-alpha607"), None)
if not e:
    print("AU-alpha607 not found"); raise SystemExit

# Authoritative spec-sheet values (user-supplied) - overwrite prior estimates.
e["japan_price_kyen"] = 79.8
e["watts_per_channel"] = 90          # 8 ohm rated
e["thd_percent"] = 0.003
e["freq_response_hz"] = "1-300000"   # line/CD input, +0 -3dB
e["ps_type"] = e.get("ps_type")      # not specified on sheet; leave as-is
e["amp_circuit"] = "Integrated DC amp - alpha-X Balanced circuit"
e["weight_kg"] = 15.7
e["special_features"] = ("alpha-X Balanced power amp; 105W+105W @ 6ohm; damping factor 80 (6ohm); "
                         "slew rate 180V/us; subsonic filter 16Hz; power 240W; dims 448 x 160 x 441 mm")
e["verified"] = True
e["year_source"] = "user (spec sheet)"
# keep existing int_model (AU-X701) and years (1986-1987)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("updated AU-alpha607:", e["watts_per_channel"], "W,", e["weight_kg"], "kg, int:", e["int_model"],
      "verified:", e["verified"])
