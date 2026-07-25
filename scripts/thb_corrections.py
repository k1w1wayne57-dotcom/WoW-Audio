import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}
DATE = "2026-08"

# 1) B-2102: Wayne bought it for THB 20,000 -> mark sold at that price
b = by["B-2102"]
b["price_thb_listings"] = [20000]
b["thb_status"] = "Sold"
b["last_price_check"] = DATE
ci = b.setdefault("collector_info", {})
note = "Bought by Wayne (Aug 2026, THB 20,000)."
ci["collector_notes"] = f"{ci.get('collector_notes')} | {note}" if ci.get("collector_notes") else note

# 2) QR-6500: qr-6599 was a typo for the same unit -> single listing
by["QR-6500"]["price_thb_listings"] = [11600]

def entry(id, jm, typ, ys, ye, thb, note, **f):
    return {
        "id": id, "brand": "Sansui", "jdm_model": jm, "int_model": None, "type": typ,
        "series": f.pop("series", "Silver Era"), "year_start": ys, "year_end": ye,
        "japan_price_kyen": f.pop("japan_price_kyen", None),
        "watts_per_channel": f.pop("watts_per_channel", None),
        "freq_response_hz": f.pop("freq_response_hz", None),
        "thd_percent": f.pop("thd_percent", None), "ps_type": None,
        "amp_circuit": f.pop("amp_circuit", None), "weight_kg": f.pop("weight_kg", None),
        "special_features": None, "pros": None, "cons": None,
        "collector_ranking": "Unranked", "sonic_signature": f.pop("sonic_signature", None),
        "price_thb_listings": thb, "thb_status": "For sale", "price_confidence": "Low",
        "last_price_check": DATE,
        "collector_info": {"known_issues": None, "collector_notes": note},
        "restorer_info": {
            "known_failure_points": ["Electrolytic caps throughout the signal path dry out",
                                     "Protection relay/switch contacts oxidize over time"],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": None, "estimated_recap_cost_usd": None,
            "common_faults": ["Scratchy pots and switches", "Channel imbalance after long storage"]},
        "best_buy": {"rating": None, "reason": None}, "capacitors": [],
        "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
        "notes": None, "verified": False, "avg_price_usd_3mo": None, "price_basis": None,
        "usd_msrp": None, "market": None, "year_source": "research",
    }

new = []
if "A-80" not in by:
    new.append(entry("sansui-a-80-1980", "A-80", "Integrated", 1980, 1982, [6500],
        "Listed for sale as a combo with a D-100 cassette deck (combo THB 6,500).",
        watts_per_channel=65, freq_response_hz="5-70000", thd_percent=0.05, weight_kg=7.1,
        amp_circuit="Integrated DC servo amplifier (with meters)",
        sonic_signature=("Silver-era Sansui: the warm, musical house sound of Sansui's peak years - "
                         "full-bodied and rich with a smooth top end and an engaging, non-fatiguing "
                         "presentation. (Family-level: mid/late-70s silver-face line.)")))
if "AU-Alpha-305RX" not in by:
    new.append(entry("sansui-au-alpha305rx-1997", "AU-Alpha-305RX", "Integrated", 1997, None, [5500],
        "Entry Alpha-series integrated.", series="Alpha Series", japan_price_kyen=40,
        watts_per_channel=65, freq_response_hz="10-70000", thd_percent=0.04, weight_kg=8.8,
        amp_circuit="Integrated DC amp, alpha-X Balanced (entry model)",
        sonic_signature=("Alpha-series voicing: a move to a more neutral tone with very good clarity "
                         "and detail while staying musically involving - refined, with layers of "
                         "depth, pinpoint imaging and crisper, more refined highs than the older warm "
                         "Sansuis. (Family-level: alpha-X Balanced series.)")))
db.extend(new)

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("B-2102 -> SOLD @ THB 20,000")
print("QR-6500 -> single listing [11600]")
print("Added:", [e["jdm_model"] for e in new], "| total entries:", len(db))
