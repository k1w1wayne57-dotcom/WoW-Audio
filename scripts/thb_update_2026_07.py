"""Apply Wayne's July 2026 Thai Baht current-find price list.

- Multiple sightings of one model are averaged (AU-111, AU-5900, QRX-3500, G-6700).
- Models not in the DB are added as new JDM entries (nulls for unknown specs).
- last_price_check -> 2026-07 on every touched entry.
"""
import json, re
from pathlib import Path

DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

RAW = [
    ("au-d607x", 8000), ("au-d607gextra", 4000), ("au-5900", 8900), ("au-x1", 23000),
    ("au-alpha317x", 3500), ("au-217", 3700), ("au-707", 9500), ("au-alpha555vs", 4500),
    ("au-alpha607nra", 13900), ("au-111", 59000), ("au-666", 9900), ("4000", 3000),
    ("au-5500", 9000), ("qr-6500", 6500), ("au-d55f", 3900), ("tu-707", 3500),
    ("au-9500", 65000), ("au-777d", 12500), ("au-d607", 3900), ("au-888", 20000),
    ("au-111", 49000), ("tr-707a", 4000), ("au-5900", 9500), ("au-3500", 5500),
    ("500a", 9000), ("qrx-3000", 5900), ("qrx-3500", 9900), ("tu-5500", 1250),
    ("800", 4000), ("551", 4500), ("qrx-5500", 15500), ("g-6700", 18000),
    ("qrx-3500", 5800), ("2000", 5000), ("g-2000", 2600), ("g6700", 18000),
]

def norm(s):
    return re.sub(r"[\s\-_.]", "", str(s)).upper()

# average duplicates
sums = {}
for name, baht in RAW:
    k = norm(name)
    sums.setdefault(k, []).append(baht)
prices = {k: round(sum(v) / len(v)) for k, v in sums.items()}

by_norm = {}
for e in db:
    by_norm.setdefault(norm(e["jdm_model"]), e)

# canonical names/types for the models not yet in the DB
NEW = {
    "AUALPHA317X":  ("AU-alpha317X",  "Integrated", "Alpha Series"),
    "AUALPHA555VS": ("AU-alpha555VS", "Integrated", "Alpha Series"),
    "TU707":        ("TU-707",        "Tuner",      "Silver Era"),
    "AU888":        ("AU-888",        "Integrated", "Classic Era"),
    "TR707A":       ("TR-707A",       "Receiver",   "Classic Era"),
    "AU3500":       ("AU-3500",       "Integrated", "Silver Era"),
    "500A":         ("500A",          "Receiver",   "Classic Era"),
}

def new_entry(jm, typ, series):
    is_rx = typ == "Receiver"
    return {
        "id": "sansui-" + re.sub(r"[^a-z0-9]+", "-", jm.lower()).strip("-"),
        "brand": "Sansui", "jdm_model": jm, "int_model": None, "type": typ,
        "series": series, "year_start": None, "year_end": None,
        "japan_price_kyen": None, "watts_per_channel": None, "freq_response_hz": None,
        "thd_percent": None, "ps_type": None, "amp_circuit": None, "weight_kg": None,
        "special_features": None, "pros": None, "cons": None, "collector_ranking": None,
        "avg_price_thb_3yr": None, "price_confidence": "Low", "last_price_check": None,
        "collector_info": {"known_issues": None,
                           "collector_notes": "Added from Wayne's Thai market finds (Jul 2026); specs pending research."},
        "restorer_info": {
            "known_failure_points": [
                "Electrolytic caps throughout the signal path dry out",
                "Protection relay/switch contacts oxidize over time",
                ("Dial cord/string stretches or breaks on tuner sections" if is_rx
                 else "Speaker relay and protection circuit contacts oxidize over time"),
            ],
            "bias_spec_mv": None, "service_manual_link": None, "recap_difficulty": 3,
            "recap_notes": None, "estimated_recap_cost_usd": None,
            "common_faults": ["Scratchy pots and switches", "Channel imbalance after long storage"],
        },
        "best_buy": {"rating": None, "reason": None},
        "capacitors": [],
        "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
        "notes": None, "verified": False, "avg_price_usd_3mo": None, "price_basis": None,
        "year_source": None,
    }

updated, added = [], []
for k, price in prices.items():
    e = by_norm.get(k)
    if e is None:
        if k not in NEW:
            print(f"  ?? unmapped model: {k}"); continue
        jm, typ, series = NEW[k]
        e = new_entry(jm, typ, series)
        db.append(e)
        by_norm[k] = e
        added.append(jm)
    old = e.get("avg_price_thb_3yr")
    e["avg_price_thb_3yr"] = price
    e["last_price_check"] = "2026-07"
    n = len(sums[k])
    updated.append((e["jdm_model"], old, price, n))

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

print(f"Updated {len(updated)} models ({len(added)} newly added). Total entries: {len(db)}")
for jm, old, new, n in sorted(updated):
    avg = f" (avg of {n})" if n > 1 else ""
    print(f"  {jm:18s} {str(old):>7} -> {new}{avg}")
print("\nNew entries:", ", ".join(added))
