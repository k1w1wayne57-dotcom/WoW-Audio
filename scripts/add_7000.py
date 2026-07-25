"""Add the Sansui 7000 receiver (1971) — confirmed real by Wayne; not yet in DB.
Sansui's last/most-powerful cap-coupled receiver. Specs from HiFi Engine / Reverb
/ US Audio Mart: 70 wpc into 8Ω, 20Hz-50kHz, THD 0.4%, damping 30, ~15 kg,
MSRP $499.95. Current market ~$450 (good units ask $675-700).
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

if "7000" in by:
    print("7000 already present; skipping.")
else:
    e = {
        "id": "sansui-7000-1971", "brand": "Sansui", "jdm_model": "7000",
        "int_model": None, "type": "Receiver", "series": "Early Solid State",
        "year_start": 1971, "year_end": 1972, "japan_price_kyen": None,
        "watts_per_channel": 70, "freq_response_hz": "20-50000", "thd_percent": 0.4,
        "ps_type": None, "amp_circuit": "Solid-state, capacitor-coupled output",
        "weight_kg": 15.0,
        "special_features": "Sansui's last and most powerful capacitor-coupled receiver; "
                            "made for roughly one year, relatively rare. Walnut wood case.",
        "pros": None, "cons": None, "collector_ranking": "Unranked",
        "sonic_signature": "Early-70s Sansui warmth: a full, rich, slightly soft "
                           "cap-coupled sound - smooth and easy on the ears rather than "
                           "tight and modern. (Family-level: early solid-state era.)",
        "circuit_description": None, "price_confidence": "Medium",
        "last_price_check": "2026-07",
        "collector_info": {"known_issues": None,
            "collector_notes": "Confirmed real by Wayne. Rare - one-year production run; "
                               "the top of Sansui's early cap-coupled solid-state line."},
        "restorer_info": {
            "known_failure_points": [
                "Large output coupling caps dry out (cap-coupled design)",
                "Power-supply electrolytics dry out",
                "Dial lamps and switch contacts degrade"],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": None, "estimated_recap_cost_usd": None,
            "common_faults": ["Scratchy controls", "Weak/uneven channel from aged caps",
                              "FM drift until warmed up"]},
        "best_buy": {"rating": None, "reason": None}, "capacitors": [],
        "links": {"audio_database": None,
                  "hifi_engine": "https://www.hifiengine.com/manual_library/sansui/7000.shtml",
                  "sansui_us": None},
        "notes": "Dimensions 444 x 140 x 327 mm. Sensitivity: 2mV MM, 200mV line. "
                 "S/N 70dB MM / 80dB line. Channel separation 50dB. Damping 30. "
                 "Specs confirmed by Wayne from HiFi Engine sheet.",
        "verified": True, "avg_price_usd_3mo": 450,
        "price_basis": "Reverb/US Audio Mart used listings (good units ask $675-700)",
        "year_source": "research", "price_thb_listings": [],
        "usd_msrp": 500, "market": "International", "thb_status": None,
    }
    db.append(e)
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Added 7000. Total entries:", len(db))

json.load(open(DB_PATH, encoding="utf-8-sig"))
print("valid")
