import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

if any(e["jdm_model"] == "AU-D607" for e in db):
    print("already exists"); raise SystemExit

entry = {
    "id": "sansui-au-d607-1979",
    "brand": "Sansui",
    "jdm_model": "AU-D607",
    "int_model": None,
    "type": "Integrated",
    "series": "DC Era",
    "year_start": 1979,
    "year_end": None,
    "japan_price_kyen": 69.8,
    "watts_per_channel": 70,
    "freq_response_hz": "DC-400000",
    "thd_percent": 0.008,
    "ps_type": None,
    "amp_circuit": "Wide-range DC pre-main, diamond differential circuit",
    "weight_kg": 15.5,
    "special_features": "Diamond differential circuit; output bandwidth 5Hz-70kHz; slew rate 160V/us; "
                        "damping factor 100; subsonic filter 16Hz; headphone out 85mW; power 195W; "
                        "dims 430 x 168 x 390 mm; optional BX-7 rack adapter (JPY3,000)",
    "pros": None,
    "cons": None,
    "collector_ranking": None,
    "avg_price_thb_3yr": None,
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
print("added AU-D607; total entries:", len(db))
