"""Build data/pioneer.json from Wayne's rough Thai-market Pioneer list.

Same schema + trust model as build_marantz.py. Wayne's rule: price approximates
collectability; Best Buy = collectability x how cheap the Thai baht price is vs USD.
Specs are sourced (never guessed) into SPECS; USD medians (HiFiShark) into PRICES;
per-brand ranking by price into RANKINGS; Best Buy for Thai-priced models into BESTBUY.
Re-run: python scripts/build_pioneer.py
"""
import json, re, os

SOURCE_NOTE = ("Unverified — model and/or Thai price from Wayne's Thai-market list; "
               "not independently confirmed.")
LAST_CHECK = "2026-08"

# model, type, year_start, year_end, series, thb_listings, usd_price, extra_note
# Types from the Pioneer prefix convention: SX=receiver, SA=integrated amp, TX=tuner,
# QX/GX=quad receiver, M/SM=power amp, C=preamp. Uncertain ones left None for research.
DATA = [
    # --- SX stereo receivers ---
    ("SX-1980", "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-1280", None, None, None, "SX Receiver", None, None, None),  # placeholder guard (not in list)
    ("SX-1250", "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-1050", "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-1010", "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-950",  "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-850",  "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-750",  "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-650",  "Receiver", None, None, "SX Receiver", [7900], None, None),
    ("SX-636",  "Receiver", None, None, "SX Receiver", [3800], None, None),
    ("SX-6000", "Receiver", None, None, "SX Receiver", [3900], None, None),
    ("SX-580",  "Receiver", None, None, "SX Receiver", [3290], None, None),
    ("SX-550",  "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-450",  "Receiver", None, None, "SX Receiver", None, None, None),
    ("SX-440",  "Receiver", None, None, "SX Receiver", [3500], None, None),
    ("SX-424",  "Receiver", None, None, "SX Receiver", [2000], None, None),
    ("SX-3700", "Receiver", None, None, "SX Receiver", [3200], None, None),
    ("SX-2000", "Receiver", None, None, "Tube Era", [9500], None, "Tube receiver"),
    ("SX-34",   "Receiver", 1962, None, "Tube Era", [9200], None, "Early tube receiver (1962)"),
    # --- SA integrated amplifiers ---
    ("SA-9900", "Integrated", None, None, "SA Amplifier", None, None, None),
    ("SA-9800", "Integrated", None, None, "SA Amplifier", None, None, None),
    ("SA-9100", "Integrated", None, None, "SA Amplifier", None, None, None),
    ("SA-8800II", "Integrated", None, None, "SA Amplifier", [7500], None, "Dual-mono"),
    ("SA-7700", "Integrated", None, None, "SA Amplifier", [2900], None, None),
    ("SA-7500", "Integrated", None, None, "SA Amplifier", [2900], None, None),
    ("SA-6850", "Integrated", None, None, "SA Amplifier", [4900], None, None),
    ("SA-6800II", "Integrated", None, None, "SA Amplifier", [3800, 3000], None, None),
    ("SA-6750", "Integrated", None, None, "SA Amplifier", [3600], None, None),
    ("SA-6700", "Integrated", None, None, "SA Amplifier", [2350, 2800], None, None),
    ("SA-6600II", "Integrated", None, None, "SA Amplifier", [3300], None, None),
    ("SA-6300", "Integrated", None, None, "SA Amplifier", [3600], None, None),
    ("SA-4400", "Integrated", None, None, "SA Amplifier", [1800], None, None),
    ("SA-70",   "Integrated", None, None, "SA Amplifier", [5900], None, None),
    # --- TX tuners ---
    ("TX-70",   "Tuner", None, None, "TX Tuner", [1350], None, None),
    ("TX-7800", "Tuner", None, None, "TX Tuner", [1500], None, None),
    # --- Quad receiver ---
    ("GX-8000", "Receiver 4-ch", None, None, "Quad Receiver", [7000], None, None),
    # --- Separates / preamps / other (types to confirm) ---
    ("M-77",    "Power Amp", None, None, "Separates", [17900], None, None),
    ("M-1500",  "Power Amp", None, None, "Separates", [4500], None, None),
    ("SM-1500", "Power Amp", None, None, "Tube Era", [20000], None, "Tube power amp; listed with C-1500 preamp + CD player"),
    ("C-200",   "Preamp", None, None, "Separates", [7500], None, None),
    ("EX-700",  None, None, None, None, [4500], None, None),
    ("ES-1000", None, None, None, None, [3900], None, None),
    ("E-3000A", None, None, None, None, [4200], None, None),
    ("MR-1000", None, 1975, None, None, [3900], None, None),
]
# Drop the SX-1280 placeholder (kept above only to make the list order obvious); remove it here.
DATA = [row for row in DATA if row[0] != "SX-1280"]

CONV = "Pioneer SX/SA naming convention (unconfirmed watts)"

# Sourced specs (verified=false). w=watts/ch into 8ohm, thd=%, fr=freq Hz, wt=weight kg.
SPECS = {}

# Latest USD market price (HiFiShark median, ~2026), approximates collectability.
PRICES = {}

# Per-brand collector ranking (Sansui-style bands), ordered by price. Filled after research.
RANKINGS = {}

# Best Buy (1-5) = collectability x how cheap the Thai price is vs USD. Thai-priced models only.
BESTBUY = {}


def slug(model):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", model.lower())).strip("-")


def build():
    records = []
    for (model, mtype, ys, ye, series, thb, usd, extra) in DATA:
        has_price = bool(thb) or usd is not None
        note = SOURCE_NOTE + (f" {extra}." if extra else "")
        sp = SPECS.get(model, {})
        if sp:
            ys = sp.get("ys", ys)
            ye = sp.get("ye", ye)
            mtype = sp.get("type", mtype)
            note += f" Specs sourced from {sp['src']} (still unverified)."
        src_str = sp.get("src", "")
        if sp and "convention" not in src_str.lower():
            verification = "sourced"
        else:
            verification = "unconfirmed"
        links = {"audio_database": None, "hifi_engine": None, "sansui_us": None, "source": None}
        src_urls = sp.get("url")
        if src_urls:
            if isinstance(src_urls, str):
                src_urls = [src_urls]
            for u in src_urls:
                if "audio-database.com" in u:
                    links["audio_database"] = u
                elif "hifiengine.com" in u:
                    links["hifi_engine"] = u
                else:
                    links["source"] = u
        rec = {
            "id": f"pioneer-{slug(model)}" + (f"-{ys}" if ys else ""),
            "brand": "Pioneer",
            "jdm_model": model,
            "int_model": None,
            "type": mtype,
            "series": series,
            "year_start": ys,
            "year_end": ye,
            "japan_price_kyen": sp.get("yen"),
            "watts_per_channel": sp.get("w"),
            "freq_response_hz": sp.get("fr"),
            "thd_percent": sp.get("thd"),
            "ps_type": sp.get("ps"),
            "amp_circuit": sp.get("ckt"),
            "weight_kg": sp.get("wt"),
            "special_features": None,
            "pros": None,
            "cons": None,
            "collector_ranking": RANKINGS.get(model, "Unranked"),
            "price_confidence": "Medium" if model in PRICES else ("Low" if has_price else "None"),
            "last_price_check": LAST_CHECK if has_price else None,
            "collector_info": {"known_issues": None, "collector_notes": sp.get("cnote")},
            "restorer_info": {
                "known_failure_points": [], "bias_spec_mv": None, "service_manual_link": None,
                "recap_difficulty": None, "recap_notes": None, "estimated_recap_cost_usd": None,
                "common_faults": [],
            },
            "best_buy": {"rating": BESTBUY.get(model, (None,))[0],
                         "reason": BESTBUY[model][1] if model in BESTBUY else None},
            "capacitors": [],
            "links": links,
            "notes": note,
            "verified": False,
            "verification": verification,
            "avg_price_usd_3mo": PRICES.get(model, usd),
            "price_basis": "hifishark median 2026" if model in PRICES else None,
            "year_source": sp.get("src", "wayne-list (Thai market, unverified)"),
            "price_thb_listings": thb or [],
            "usd_msrp": None,
            "market": None,
            "sonic_signature": sp.get("sonic"),
            "thb_status": None,
        }
        records.append(rec)
    return records


if __name__ == "__main__":
    recs = build()
    out = os.path.join(os.path.dirname(__file__), "..", "data", "pioneer.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
        f.write("\n")
    ids = [r["id"] for r in recs]
    assert len(ids) == len(set(ids)), "dup ids: " + str([i for i in ids if ids.count(i) > 1])
    priced = sum(1 for r in recs if r["price_thb_listings"] or r["avg_price_usd_3mo"] is not None)
    print(f"wrote {len(recs)} Pioneer records ({priced} with a price) -> data/pioneer.json")
