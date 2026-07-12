import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by_jm = {e["jdm_model"]: e for e in db}
existing = set(by_jm)

# 1) Fill base AU-D907 specs (were all null after the '/' split). Keep Penta-Power ps_type.
e = by_jm["AU-D907"]
for k, v in dict(watts_per_channel=100, thd_percent=0.008, freq_response_hz="10-20000",
                 weight_kg=18).items():
    if e.get(k) in (None, ""):
        e[k] = v
ci = e.setdefault("collector_info", {})
phono = ("Top-tier built-in phono equalizer (MM + MC), widely praised. JDM (100V) equivalent "
         "of the AU-919. NOTE: sometimes marketed as 'dual-mono', but the actual design is "
         "Penta-Power (stage-split), not one transformer per channel.")
ci["collector_notes"] = f"{ci.get('collector_notes')} | {phono}" if ci.get("collector_notes") else phono

def entry(id, jm, typ, ys, ye, **f):
    return {
        "id": id, "brand": "Sansui", "jdm_model": jm, "int_model": None, "type": typ,
        "series": f.pop("series", "DC Era"), "year_start": ys, "year_end": ye,
        "japan_price_kyen": f.pop("japan_price_kyen", None),
        "watts_per_channel": f.pop("watts_per_channel", None),
        "freq_response_hz": f.pop("freq_response_hz", None),
        "thd_percent": f.pop("thd_percent", None), "ps_type": f.pop("ps_type", None),
        "amp_circuit": f.pop("amp_circuit", None), "weight_kg": f.pop("weight_kg", None),
        "special_features": f.pop("special_features", None),
        "pros": None, "cons": None, "collector_ranking": None,
        "price_thb_listings": [], "price_confidence": "Low", "last_price_check": None,
        "collector_info": {"known_issues": None, "collector_notes": f.pop("collector_notes", None)},
        "restorer_info": {
            "known_failure_points": [
                "DC servo/offset circuit drifts with aging caps, risking speaker damage if unchecked",
                "Protection relay contacts oxidize and cause dropouts",
                "Electrolytic caps throughout the signal path dry out",
                "IC-based stages can degrade and are harder to source replacements for"],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": None, "estimated_recap_cost_usd": None,
            "common_faults": ["Protection relay trips on power-up",
                              "DC offset out of spec at speaker terminals",
                              "Channel imbalance after long storage"]},
        "best_buy": {"rating": None, "reason": None}, "capacitors": [],
        "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
        "notes": None, "verified": False, "avg_price_usd_3mo": None, "price_basis": None,
        "year_source": "research",
    }

NEW = [
    entry("sansui-au-d907-limited-1979", "AU-D907 LIMITED", "Integrated", 1979, 1980,
          japan_price_kyen=179, watts_per_channel=100, freq_response_hz="10-20000",
          thd_percent=0.008, weight_kg=20.0, ps_type="Penta-Power (dual transformer, stage-split)",
          amp_circuit="Wide-range DC integrated (Penta-Power), premium AU-X1-derived build",
          special_features=("Premium AU-D907 variant using AU-X1 development know-how: copper-plated "
                            "chassis, gold-plated connectors, bronze baseplate, wooden side panels. "
                            "Dims 466 x 182 x 432 mm; power consumption 260W."),
          collector_notes="Highly sought-after collector's edition of the AU-D907."),
    entry("sansui-au-d907f-extra-1981", "AU-D907F Extra", "Integrated", 1981, 1982,
          japan_price_kyen=175, watts_per_channel=130, freq_response_hz="DC-300000",
          thd_percent=0.003, weight_kg=17.7,
          amp_circuit="Super Feedforward, diamond differential"),
    entry("sansui-au-d907g-extra-1983", "AU-D907G Extra", "Integrated", 1983, 1984,
          japan_price_kyen=178, watts_per_channel=130, freq_response_hz="DC-300000",
          thd_percent=0.003, weight_kg=18.0,
          amp_circuit="Super Feedforward DC integrated"),
]
added = []
for ne in NEW:
    if ne["jdm_model"] in existing:
        print("  exists:", ne["jdm_model"]); continue
    db.append(ne); added.append(ne["jdm_model"])

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("AU-D907 base filled ->", e["watts_per_channel"], "W,", e["thd_percent"], "THD,", e["weight_kg"], "kg")
print("Added:", added, "| total:", len(db))
