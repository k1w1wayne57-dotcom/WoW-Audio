"""Add the Sansui B-7000 4-channel power amplifier (Wayne owns one; faceplate-confirmed).
Faceplate: SANSUI B-7000 POWER AMPLIFIER, 4-Channel Stereo, 340W (rated power
consumption), AC120/220/240V 50/60Hz, Made in Japan. Quad era (early-mid 70s,
QA-7000 companion generation). Output watts NOT verifiable from sources -> left
null and flagged in NEEDS_DATA.md rather than guessed.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

if "B-7000" in by:
    print("B-7000 already present; skipping.")
else:
    e = {
        "id": "sansui-b-7000-1973", "brand": "Sansui", "jdm_model": "B-7000",
        "int_model": None, "type": "Power Amp", "series": "Quad (QS) Era",
        "year_start": 1973, "year_end": 1976, "japan_price_kyen": None,
        "watts_per_channel": None,  # unverified — do not guess
        "freq_response_hz": None, "thd_percent": None, "ps_type": None,
        "amp_circuit": "4-channel solid-state power amplifier (dedicated, no preamp)",
        "weight_kg": None, "special_features":
            "Dedicated 4-channel (quadraphonic) power amplifier — the power-only "
            "counterpart to Sansui's QS-matrix quad line. Multi-voltage export chassis "
            "(AC120/220/240 V). Faceplate rates 340 W total power consumption.",
        "pros": None, "cons": None, "collector_ranking": "Unranked",
        "sonic_signature": None, "circuit_description": None,
        "price_confidence": "None", "last_price_check": None,
        "collector_info": {
            "known_issues": None,
            "collector_notes": "Owned by Wayne (faceplate-confirmed: B-7000 4-Channel "
                               "Stereo Power Amplifier, Made in Japan, S/N 4905001711). "
                               "Rare — little published spec data; output rating unverified."},
        "restorer_info": {
            "known_failure_points": [
                "Output transistor bias drifts with age",
                "Electrolytic caps in power supply dry out",
                "Protection relay contacts oxidize"],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": None, "estimated_recap_cost_usd": None,
            "common_faults": [
                "Protection relay trips on power-up",
                "DC offset out of spec",
                "Channel imbalance across the four outputs"]},
        "best_buy": {"rating": None, "reason": None}, "capacitors": [],
        "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
        "notes": "Output power/channel, weight, and price need verification — no "
                 "reliable published source found. See NEEDS_DATA.md.",
        "verified": False, "avg_price_usd_3mo": None, "price_basis": None,
        "year_source": "research (quad-era estimate)", "price_thb_listings": [],
        "usd_msrp": None, "market": "International", "thb_status": None,
    }
    db.append(e)
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Added B-7000. Total entries:", len(db))

json.load(open(DB_PATH, encoding="utf-8-sig"))
print("valid")
