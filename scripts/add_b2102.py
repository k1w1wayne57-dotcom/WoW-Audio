import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

if any(e["jdm_model"] == "B-2102" for e in db):
    print("already exists"); raise SystemExit

entry = {
    "id": "sansui-b-2102-1986",
    "brand": "Sansui",
    "jdm_model": "B-2102",
    "int_model": None,
    "type": "Power Amp",
    "series": "Alpha Series",
    "year_start": 1986,
    "year_end": 1990,
    "japan_price_kyen": None,
    "watts_per_channel": 200,
    "freq_response_hz": "1-300000",
    "thd_percent": 0.003,
    "ps_type": None,
    "amp_circuit": "Stereo power amplifier",
    "weight_kg": 17.7,
    "special_features": "Input sensitivity 1V; S/N 115dB; speaker load 4-16 ohm; "
                        "dims 430 x 160 x 412 mm",
    "pros": None,
    "cons": None,
    "collector_ranking": None,
    "avg_price_thb_3yr": None,
    "price_confidence": "Low",
    "last_price_check": "2026-07",
    "collector_info": {"known_issues": None, "collector_notes": None},
    "restorer_info": {
        "known_failure_points": [
            "DC offset / protection circuit drifts with aging caps, risking speaker damage",
            "Protection relay contacts oxidize and cause dropouts",
            "Main filter and signal-path electrolytics dry out",
            "Output devices run hot; check bias and heatsink thermal paste",
        ],
        "bias_spec_mv": None,
        "service_manual_link": None,
        "recap_difficulty": 3,
        "recap_notes": None,
        "estimated_recap_cost_usd": None,
        "common_faults": [
            "Protection relay trips on power-up",
            "DC offset out of spec at speaker terminals",
            "One channel low or dead after storage",
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
print("added B-2102; total entries:", len(db))
