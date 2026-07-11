import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

if any(e["jdm_model"] == "AU-D607G Extra" for e in db):
    print("already exists"); raise SystemExit

entry = {
    "id": "sansui-au-d607g-extra-1983",
    "brand": "Sansui",
    "jdm_model": "AU-D607G Extra",
    "int_model": None,
    "type": "Integrated",
    "series": "DC Era",
    "year_start": 1983,
    "year_end": None,
    "japan_price_kyen": 79.8,
    "watts_per_channel": 90,
    "freq_response_hz": "DC-300000",
    "thd_percent": 0.003,
    "ps_type": "Dual Mono",
    "amp_circuit": "Integrated DC amp - Ground Floating, Super Feedforward & DD/DC",
    "weight_kg": 13.5,
    "special_features": "Newly developed Ground Floating circuit; Hi-Precision DC servo equalizer; "
                        "output bandwidth 5Hz-70kHz; slew rate 180V/us; damping factor 100; "
                        "dims 460 x 160 x 404 mm; power consumption 220W",
    "pros": None,
    "cons": None,
    "collector_ranking": None,
    "avg_price_thb_3yr": 4000,
    "price_confidence": "Low",
    "last_price_check": "2026-07",
    "collector_info": {"known_issues": None, "collector_notes": None},
    "restorer_info": {
        "known_failure_points": [
            "DC servo/offset circuit drifts with aging caps, risking speaker damage if unchecked",
            "Protection relay contacts oxidize and cause dropouts",
            "Electrolytic caps throughout the signal path dry out",
            "IC-based stages can degrade and are harder to source replacements for",
        ],
        "bias_spec_mv": None,
        "service_manual_link": None,
        "recap_difficulty": 3,
        "recap_notes": None,
        "estimated_recap_cost_usd": None,
        "common_faults": [
            "Protection relay trips on power-up",
            "DC offset out of spec at speaker terminals",
            "Channel imbalance after long storage",
            "Crackling on input/source switching",
        ],
    },
    "best_buy": {"rating": None, "reason": None},
    "capacitors": [],
    "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
    "notes": None,
    "verified": True,
    "avg_price_usd_3mo": None,
    "price_basis": None,
    "year_source": "user (spec sheet)",
}
db.append(entry)
with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("added AU-D607G Extra; total entries:", len(db))
