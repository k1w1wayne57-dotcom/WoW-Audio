import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
existing = {e["jdm_model"] for e in db}

WARN = ("X-BALANCED SAFETY: both the red (+) and black (-) speaker terminals carry live, "
        "independent voltage. NEVER bridge/common the black terminals together, and NEVER "
        "connect a black terminal to chassis or an external/test ground - doing so shorts the "
        "floating balanced rails and instantly destroys the output transistors.")

def entry(id, jm, typ, year, year_end=None, **f):
    is_rx = typ == "Receiver"
    recap = f.pop("recap_notes", None)
    e = {
        "id": id, "brand": "Sansui", "jdm_model": jm, "int_model": f.pop("int_model", None),
        "type": typ, "series": f.pop("series", "DC Era"),
        "year_start": year, "year_end": year_end,
        "japan_price_kyen": f.pop("japan_price_kyen", None),
        "watts_per_channel": f.pop("watts_per_channel", None),
        "freq_response_hz": f.pop("freq_response_hz", None),
        "thd_percent": f.pop("thd_percent", None),
        "ps_type": f.pop("ps_type", None),
        "amp_circuit": f.pop("amp_circuit", None),
        "weight_kg": f.pop("weight_kg", None),
        "special_features": f.pop("special_features", None),
        "pros": None, "cons": None, "collector_ranking": None,
        "price_thb_listings": [], "price_confidence": "Low", "last_price_check": None,
        "collector_info": {"known_issues": None, "collector_notes": f.pop("collector_notes", None)},
        "restorer_info": {
            "known_failure_points": [
                "DC servo/offset circuit drifts with aging caps, risking speaker damage if unchecked",
                "Protection relay contacts oxidize and cause dropouts",
                "Electrolytic caps throughout the signal path dry out",
                "IC-based stages can degrade and are harder to source replacements for",
            ],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": recap, "estimated_recap_cost_usd": None,
            "common_faults": ["Protection relay trips on power-up",
                              "DC offset out of spec at speaker terminals",
                              "Channel imbalance after long storage"],
        },
        "best_buy": {"rating": None, "reason": None}, "capacitors": [],
        "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
        "notes": None, "verified": False, "avg_price_usd_3mo": None, "price_basis": None,
        "year_source": "research",
    }
    assert not f, f"leftover fields: {f}"
    return e

NEW = [
    entry("sansui-au-d707x-1984", "AU-D707X", "Integrated", 1984, 1986,
          japan_price_kyen=129, watts_per_channel=130, freq_response_hz="DC-300000",
          thd_percent=0.003, weight_kg=17.5, ps_type="X-Balanced (floating balanced supply)",
          amp_circuit="X-Balanced DC integrated, twin diamond differential", recap_notes=WARN),
    entry("sansui-au-d507x-1984", "AU-D507X", "Integrated", 1984, 1986,
          watts_per_channel=80, freq_response_hz="DC-300000", weight_kg=9.8,
          ps_type="X-Balanced (floating balanced supply)",
          amp_circuit="X-Balanced DC integrated (budget); 90W @ 6ohm", recap_notes=WARN),
    entry("sansui-au-d607f-1980", "AU-D607F", "Integrated", 1980, 1981,
          japan_price_kyen=76, watts_per_channel=75, freq_response_hz="DC-300000",
          thd_percent=0.005, weight_kg=12.4,
          amp_circuit="Super Feedforward, diamond differential"),
    entry("sansui-au-d11-1982", "AU-D11", "Integrated", 1982, 1983,
          watts_per_channel=120, freq_response_hz="10-20000", thd_percent=0.005, weight_kg=17.5,
          amp_circuit="Super Feedforward DC integrated (flagship)"),
    entry("sansui-b-2101-1985", "B-2101", "Power Amp", 1985, 1988,
          watts_per_channel=200, freq_response_hz="1-300000", thd_percent=0.003, weight_kg=18,
          amp_circuit="Stereo power amplifier"),
    entry("sansui-c-2301-1985", "C-2301", "Preamp", 1985, 1988,
          japan_price_kyen=550, freq_response_hz="DC-500000", weight_kg=21,
          amp_circuit="Stereo control preamplifier (flagship)",
          collector_notes="Widely regarded as the best preamp Sansui ever made."),
]

added = []
for e in NEW:
    if e["jdm_model"] in existing:
        print("  already exists:", e["jdm_model"]); continue
    db.append(e); added.append(e["jdm_model"])

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("Added:", added, "| total entries:", len(db))
