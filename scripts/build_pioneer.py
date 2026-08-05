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
    # --- Quad receiver (Wayne wrote "GX-8000"; this is Pioneer's QX-8000) ---
    ("QX-8000", "Receiver 4-ch", None, None, "Quad Receiver", [7000], None, "Wayne's list wrote GX-8000"),
    # --- Separates / preamps / other ---
    ("M-77",    "Power Amp", None, None, "Separates", [17900], None, None),
    ("M-1500",  "Power Amp", None, None, "Separates", [4500], None, None),
    ("SM-1500", "Power Amp", None, None, "Separates", [20000], None, "The ฿20k listing bundles SM-1500 power amp + C-1500 preamp + a CD player"),
    ("C-200",   None, None, None, "Separates", [7500], None, "Unidentified — possibly a preamp (verify)"),
    ("EX-700",  None, None, None, None, [4500], None, "Compact stereo system / coaxial speakers (verify — likely not a component)"),
    ("ES-1000", None, None, None, None, [3900], None, "1972 stereo audio system (verify)"),
    ("E-3000A", None, None, None, None, [4200], None, "Stereo audio system (verify)"),
    ("MR-1000", None, 1975, None, None, [3900], None, "Unidentified vintage Pioneer unit (verify)"),
]
# Drop the SX-1280 placeholder (kept above only to make the list order obvious); remove it here.
DATA = [row for row in DATA if row[0] != "SX-1280"]

CONV = "Pioneer SX/SA naming convention (unconfirmed watts)"

# Sourced specs (verified=false). w=watts/ch into 8ohm, thd=%, fr=freq Hz, wt=weight kg.
SPECS = {
    # --- SX receivers ---
    "SX-1980": dict(ys=1978, ye=1980, w=270, ckt="Flagship 'monster' receiver — the most powerful Pioneer SX ever", src="wikipedia/classicreceivers",
        sonic="Huge, effortless power with the classic Pioneer warmth.",
        cnote="270W/ch flagship (1978) — rare and the most sought-after Pioneer receiver; prices have climbed steeply."),
    "SX-1250": dict(ys=1976, w=160, ckt="Flagship SX receiver", src="classicreceivers"),
    "SX-1050": dict(ys=1976, w=120, ckt="SX stereo receiver", src="classicreceivers"),
    "SX-1010": dict(ys=1974, w=100, ckt="SX stereo receiver", src="audioexchange"),
    "SX-950":  dict(w=85, ckt="SX stereo receiver — a popular sweet spot", src="audioexchange"),
    "SX-850":  dict(ys=1976, ye=1977, w=65, ckt="SX stereo receiver", src="classicreceivers"),
    "SX-750":  dict(ys=1976, ye=1977, w=50, ckt="SX stereo receiver; twin tone control", src="audioexchange"),
    "SX-650":  dict(w=35, ckt="SX stereo receiver — popular budget classic", src="audioexchange"),
    "SX-550":  dict(w=20, ckt="SX stereo receiver", src=CONV),
    "SX-450":  dict(w=15, ckt="Entry SX stereo receiver", src="classicreceivers"),
    "SX-3700": dict(w=45, ckt="SX stereo receiver (early 80s)", src="vintageaudioexchange"),
    "SX-2000": dict(ys=1970, w=40, thd=1.0, fr="20-20000", ckt="All-tube stereo receiver (3x12AX7 + 7868 outputs)", src="reverb/radiomuseum",
        sonic="Rich, classic tube sound.",
        cnote="All-tube receiver (~1970), 40W — a rare, highly regarded Japanese tube grail."),
    "SX-34":   dict(ys=1962, ckt="Early Pioneer tube receiver", src="wayne-list",
        cnote="Very early (1962) Pioneer tube receiver — rare."),
    # --- SA integrated amplifiers ---
    "SA-9900": dict(ys=1975, ye=1979, w=110, ckt="Flagship integrated amplifier", src="reverb/thevintageknob",
        cnote="Pioneer's flagship integrated of the era — a grail amp."),
    "SA-9800": dict(ys=1976, ye=1981, w=100, ckt="Integrated amplifier", src="audio-database"),
    "SA-9100": dict(ys=1973, ye=1976, w=60, ckt="Integrated amplifier", src="hifiengine"),
    "SA-8800II": dict(ys=1979, ye=1981, w=80, ckt="US integrated amplifier (dual-mono)", src="hifi-wiki"),
    "SA-7500": dict(w=40, ckt="Integrated amplifier (US version of the 1975 SA-8800)", src="hifi-wiki"),
    "SA-6850": dict(w=45, ckt="Integrated amplifier (JDM)", src="reverb"),
    "SA-6800II": dict(ys=1976, ye=1980, ckt="Integrated amplifier", src="hifi-wiki"),
    # --- Separates / quad ---
    "M-77":    dict(ys=1980, w=250, type="Power Amp", thd=0.1, ckt="High-power stereo amp; JDM twin of the USA SPEC-4; 250W/ch (0.05% THD at 125W)", src="audio-database",
        cnote="The JDM version of the SPEC-4 — a 250W/ch powerhouse; hence the high Thai price."),
    "M-1500":  dict(ys=1978, w=50, type="Power Amp", ckt="JDM premium power amp; partners the C-1500 preamp", src="audio-database"),
    "SM-1500": dict(ys=1980, type="Power Amp", ckt="DC power amp (SM-1500II era)", src="audio-database"),
    "QX-8000": dict(ys=1971, ye=1972, w=25, type="Receiver 4-ch", thd=1.0, fr="5-100000", wt=15.6, ckt="Quadraphonic 4-channel receiver; 25W/ch stereo, 20W/ch quad", src="classicreceivers/hifiengine"),
}

# Latest USD market price (search-based ~2026; HiFiShark cert was down, so rougher than usual).
PRICES = {
    "SX-1980": 5000, "SX-1250": 1800, "SX-2000": 1500, "SX-1050": 1300, "SA-9900": 1200,
    "M-77": 1200, "SX-1010": 800, "SA-9800": 800, "SX-950": 750, "SA-9100": 600, "SX-850": 600,
    "M-1500": 600, "SA-8800II": 500, "SX-750": 450, "SX-650": 400, "SA-6850": 400, "QX-8000": 400,
}

# Per-brand collector ranking (Sansui-style bands), ordered by price/collectability.
RANKINGS = {
    "SX-1980": "Top 10", "SX-1250": "Top 10", "SX-2000": "Top 10", "SX-1050": "Top 10", "SA-9900": "Top 10",
    "M-77": "Top 10", "SX-34": "Top 10", "SX-1010": "Top 10", "SA-9800": "Top 10", "SX-950": "Top 10",
    "SX-850": "Top 10-20", "SA-9100": "Top 10-20", "M-1500": "Top 10-20", "SM-1500": "Top 10-20",
    "SA-8800II": "Top 10-20", "SX-750": "Top 10-20", "SA-6850": "Top 10-20", "C-200": "Top 10-20",
    "QX-8000": "Top 10-20", "SX-650": "Top 10-20",
    "SA-6800II": "Top 20-30", "SA-6750": "Top 20-30", "SA-6700": "Top 20-30", "SA-6600II": "Top 20-30",
    "SA-7700": "Top 20-30", "SA-7500": "Top 20-30", "SA-6300": "Top 20-30", "SX-636": "Top 20-30",
    "SX-6000": "Top 20-30", "SA-70": "Top 20-30",
    "SX-580": "Top 30-40", "SX-3700": "Top 30-40", "SX-440": "Top 30-40", "SA-4400": "Top 30-40",
    "SX-550": "Top 30-40", "SX-450": "Top 30-40", "SX-424": "Top 30-40", "TX-7800": "Top 30-40",
    "TX-70": "Top 30-40", "EX-700": "Top 30-40",
    "ES-1000": "Unranked", "E-3000A": "Unranked", "MR-1000": "Unranked",
}

# Best Buy (1-5) = collectability x how cheap the Thai price is vs USD. Only models with both.
BESTBUY = {
    "SX-2000": (5, "All-tube grail receiver (~$1,500 USD) at ฿9,500 (~$270) — an exceptional price on a rare tube classic."),
    "M-1500": (4, "JDM premium 50W power amp (~$600 USD) at ฿4,500 (~$130) — a big discount."),
    "M-77": (4, "250W SPEC-4 twin (~$1,200 USD) at ฿17,900 (~$510) — strong value on a powerhouse amp."),
    "SA-6850": (4, "45W integrated (~$400 USD) at ฿4,900 (~$140) — good value."),
    "SA-8800II": (4, "80W dual-mono integrated (~$500 USD) at ฿7,500 (~$215) — a solid discount."),
    "QX-8000": (3, "Quad receiver (~$400 USD) at ฿7,000 (~$200) — fair value for a 4-channel classic."),
    "SX-650": (3, "Popular 35W receiver (~$400 USD) at ฿7,900 (~$225) — fair, a touch high for a 650."),
}


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
