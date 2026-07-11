import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)

# Bidirectional JDM <-> export links (documented: sansui.us export-vs-domestic history)
LINKS = {"AU-607": "AU-517", "AU-517": "AU-607", "AU-707": "AU-717", "AU-717": "AU-707"}
for jm, twin in LINKS.items():
    e = by_jm.get(jm)
    if e:
        e["int_model"] = twin
        print(f"  {jm:8s} int_model -> {twin}")

# AU-607 JDM sheet (audio-database): fill nulls
e = by_jm["AU-607"]
for k, v in dict(freq_response_hz="DC-200000", thd_percent=0.03, weight_kg=15.3,
                 japan_price_kyen=69.8,
                 amp_circuit="DC integrated (1st-gen 07 series)").items():
    if e.get(k) in (None, ""):
        e[k] = v

# AU-707 JDM sheet: fill nulls
e = by_jm["AU-707"]
for k, v in dict(watts_per_channel=85, freq_response_hz="DC-200000", thd_percent=0.03,
                 weight_kg=16.8, japan_price_kyen=93.8,
                 amp_circuit="DC integrated (1st-gen 07 series)").items():
    if e.get(k) in (None, ""):
        e[k] = v

# Corrections: stale estimates contradicted by HiFi Engine + the JDM twins
e = by_jm["AU-517"]
if e.get("watts_per_channel") == 45:
    e["watts_per_channel"] = 65
    print("  AU-517  watts 45 -> 65 (HiFi Engine; matches JDM AU-607)")
e = by_jm["AU-717"]
if e.get("watts_per_channel") == 80:
    e["watts_per_channel"] = 85
    print("  AU-717  watts 80 -> 85 (HiFi Engine; matches JDM AU-707)")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
for jm in ("AU-607", "AU-517", "AU-707", "AU-717"):
    e = by_jm[jm]
    print(f"  {jm:8s} int={e['int_model']:8s} {e['watts_per_channel']}W {e['weight_kg']}kg "
          f"price={e['japan_price_kyen']}k yen")
print("json OK")
