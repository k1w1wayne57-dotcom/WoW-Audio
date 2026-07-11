import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {}
for e in db:
    by_jm.setdefault(e["jdm_model"], e)

# rename the mislabeled Thai-find entry: the real model is AU-alpha317K (audio-database)
e = by_jm.get("AU-alpha317X")
if e:
    e["jdm_model"] = "AU-alpha317K"
    ci = e.setdefault("collector_info", {})
    ci["collector_notes"] = ((ci.get("collector_notes") or "") +
        " | Listed on FB as '317x'; actual model is AU-alpha317K (1994).").strip(" |")
    by_jm["AU-alpha317K"] = e
    print("  renamed AU-alpha317X -> AU-alpha317K")

# specs (audio-database / HiFi Engine / radiomuseum); years from sources, tagged research
DATA = {
    "AU-888":        dict(watts_per_channel=45, freq_response_hz="15-50000", thd_percent=0.4,
                          weight_kg=12.6, japan_price_kyen=72.5, year_start=1969, year_end=1971,
                          amp_circuit="Solid-state, 2-stage differential, complementary Darlington"),
    "TR-707A":       dict(watts_per_channel=18, freq_response_hz="20-20000", thd_percent=1.0,
                          weight_kg=15.0, year_start=1965, year_end=1967,
                          amp_circuit="Sansui's first solid-state AM/FM receiver (40 tr)"),
    "500A":          dict(watts_per_channel=20, freq_response_hz="20-20000", thd_percent=1.0,
                          weight_kg=18.0, year_start=1964, year_end=1966,
                          amp_circuit="Tube AM/FM-MPX receiver (4x 7189A push-pull)"),
    "TU-707":        dict(weight_kg=8.7, japan_price_kyen=54.8, year_start=1977, year_end=1979,
                          amp_circuit="AM/FM tuner, MOS FET front-end, PLL MPX (pairs AU-707)"),
    "AU-alpha555VS": dict(watts_per_channel=80, freq_response_hz="DC-100000", thd_percent=0.008,
                          weight_kg=11.0, japan_price_kyen=69.8, year_start=1989,
                          amp_circuit="Integrated DC amp, alpha-X Balanced"),
    "AU-alpha317K":  dict(watts_per_channel=55, thd_percent=0.05, weight_kg=8.9,
                          japan_price_kyen=44, year_start=1994,
                          amp_circuit="Integrated amplifier (entry Alpha series)"),
    "AU-3500":       dict(year_start=1976),
}
for jm, fields in DATA.items():
    e = by_jm.get(jm)
    if not e:
        print("  !!", jm, "not found"); continue
    changed = [k for k, v in fields.items() if e.get(k) in (None, "") and not e.__setitem__(k, v)]
    if any(f in changed for f in ("year_start", "year_end")):
        e["year_source"] = "research"
    print(f"  {jm:16s} filled: {', '.join(changed)}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("json OK")
