import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

if any(e["jdm_model"] == "C-2102" for e in db):
    print("already exists"); raise SystemExit

entry = {
    "id": "sansui-c-2102-1986",
    "brand": "Sansui",
    "jdm_model": "C-2102",
    "int_model": None,
    "type": "Preamp",
    "series": "Alpha Series",
    "year_start": 1986,
    "year_end": 1990,
    "japan_price_kyen": None,
    "watts_per_channel": None,
    "freq_response_hz": "1-300000",
    "thd_percent": 0.003,
    "ps_type": None,
    "amp_circuit": "Stereo control (pre) amplifier",
    "weight_kg": 5.5,
    "special_features": "Input sens. 0.25mV MC / 2.5mV MM / 150mV line; pre-out 1V (max 15V); "
                        "S/N 70dB MC / 88dB MM / 110dB line; dims 430 x 119 x 326 mm",
    "pros": None,
    "cons": None,
    "collector_ranking": None,
    "avg_price_thb_3yr": None,
    "price_confidence": "Low",
    "last_price_check": "2026-07",
    "collector_info": {"known_issues": None, "collector_notes": None},
    "restorer_info": {
        "known_failure_points": [
            "Electrolytic caps in the signal path dry out and shift the sound",
            "Input/function switch contacts oxidize and cause crackle or channel loss",
            "DC servo / offset circuit drifts with aging caps",
            "IC-based stages can degrade and be harder to source replacements for",
        ],
        "bias_spec_mv": None,
        "service_manual_link": None,
        "recap_difficulty": 2,
        "recap_notes": None,
        "estimated_recap_cost_usd": None,
        "common_faults": [
            "Crackling on source/function switching",
            "Channel imbalance after long storage",
            "Scratchy volume/balance pots",
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
print("added C-2102; total entries:", len(db))
