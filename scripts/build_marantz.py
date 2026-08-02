"""Build data/marantz.json from Wayne's roadmap + Thai price lists.

Source: Facebook / YouTube listings supplied by Wayne — UNVERIFIED.
Discipline (same as Sansui data): never guess specs. Watts/THD/weight/freq/circuit
are left null until properly sourced. Every record is verified=false and Unranked.
Re-run to regenerate: python scripts/build_marantz.py
"""
import json, re, os

SOURCE_NOTE = ("Unverified — model and/or Thai price observed on Facebook and YouTube "
               "listings; not independently confirmed.")
LAST_CHECK = "2026-08"

# model, type, year_start, year_end, series, thb_listings, usd_price, extra_note
DATA = [
    # --- Tube era ---
    ("Model 8",  "Tube Power Amp", 1960, 1964, "Tube Era", None, None, None),
    ("Model 9",  "Tube Power Amp", 1960, 1964, "Tube Era", None, None, None),
    # --- Early solid-state ---
    ("Model 14", None, 1966, 1969, "Early Solid-State", None, None, "Early solid-state; type unconfirmed"),
    ("Model 15", None, 1966, 1969, "Early Solid-State", None, None, "Early solid-state; type unconfirmed"),
    ("Model 16", None, 1966, 1969, "Early Solid-State", None, None, "Early solid-state; type unconfirmed"),
    ("Superscope BLA-530", None, 1967, 1971, "Superscope", None, None, "Superscope budget line; details unconfirmed"),
    # --- Japan-market models ---
    ("Model 18", "Receiver", None, None, "Japan-market", None, None, None),
    ("Model 19", "Receiver", None, None, "Japan-market", None, None, None),
    ("Model 22", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 25", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 26", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 27", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    # --- Integrated amps 10xx/12xx ---
    ("1015",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1030",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1060",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1070",  "Integrated", 1971, 1978, "10xx/12xx Integrated", [5900], None, None),
    ("1090",  "Integrated", 1971, 1978, "10xx/12xx Integrated", [9000], None, None),
    ("1150",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1200",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1200B", "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1250",  "Integrated", 1971, 1978, "10xx/12xx Integrated", None, None, None),
    ("1300 DC",   "Integrated", 1977, 1980, "Flagship DC Integrated", None, None, "Flagship DC integrated"),
    ("PM-710 DC", "Integrated", 1977, 1980, "Flagship DC Integrated", [6900], None, None),
    # --- 22XX receivers ---
    ("2210",  "Receiver", None, None, "22XX Receiver", None, None, None),
    ("2215",  "Receiver", 1971, 1974, "22XX Receiver (1st gen)", None, None, None),
    ("2215B", "Receiver", 1974, 1977, "22XX B Receiver", [5200], None, None),
    ("2216B", "Receiver", 1974, 1977, "22XX B Receiver", [7000], None, None),
    ("2218",  "Receiver", None, None, "22XX Receiver", [8200], None, None),
    ("2220B", "Receiver", 1974, 1977, "22XX B Receiver", None, None, None),
    ("2230",  "Receiver", 1971, 1974, "22XX Receiver (1st gen)", None, None, None),
    ("2235B", "Receiver", 1974, 1977, "22XX B Receiver", None, None, None),
    ("2238B", "Receiver", 1974, 1977, "22XX B Receiver", [16500], None, None),
    ("2245",  "Receiver", 1971, 1974, "22XX Receiver (1st gen)", None, None, None),
    ("2250",  "Receiver", None, None, "22XX Receiver", None, None, None),
    ("2250B", "Receiver", 1974, 1977, "22XX B Receiver", None, None, None),
    ("2260",  "Receiver", None, None, "22XX Receiver", None, None, None),
    ("2265",  "Receiver", None, None, "22XX Receiver", [27800], None, None),
    ("2270",  "Receiver", 1971, 1974, "22XX Receiver (1st gen)", None, None, None),
    ("2285B", "Receiver", None, None, "22XX Heavyweight", None, None, None),
    # --- 23XX heavyweight receivers ---
    ("2325",  "Receiver", None, None, "23XX Heavyweight", None, None, None),
    ("2330B", "Receiver", None, None, "23XX Heavyweight", None, None, None),
    ("2385",  "Receiver", None, None, "23XX Heavyweight", None, None, None),
    # --- Champagne / Monster receiver era ---
    ("2500",  "Receiver", 1978, 1980, "Champagne / Monster Receiver", None, None, None),
    ("2600",  "Receiver", 1978, 1980, "Champagne / Monster Receiver", None, None, None),
    # --- Quadradial 4-channel ---
    ("3300",  None,          1972, 1976, "Quadradial 4-channel", None, None,
        "Source lists under Quad; the Marantz 3300 is commonly a stereo preamp — verify type"),
    ("4230",  "Receiver 4-ch", 1972, 1976, "Quadradial 4-channel", [15000], 575, None),
    ("4270",  "Receiver 4-ch", 1972, 1976, "Quadradial 4-channel", [34000], None, None),
    ("4300",  "Receiver 4-ch", 1972, 1976, "Quadradial 4-channel", None, None, None),
    ("4400",  "Receiver 4-ch", 1972, 1976, "Quadradial 4-channel", [39000], None, None),
    # --- High-end PM amps ---
    ("PM-5 Esotec", "Integrated", 1980, 1982, "Esotec", [18500, 16500], None, "Class A; one Thai listing noted as 220V"),
    ("PM 500", "Integrated", None, None, "PM Series", [8500], None, None),
    ("PM-54",  "Integrated", 1983, 1987, "PM Digital-Ready", None, None, None),
    ("PM-84",  "Integrated", 1983, 1987, "PM Digital-Ready", None, None, None),
    ("PM-80",  "Integrated", 1987, 1990, "Quarter-A / High-End PM", None, None, None),
    ("PM-94",  "Integrated", 1987, 1990, "Quarter-A / High-End PM", None, None, None),
    ("PM66 KI Signature", "Integrated", 1998, 1998, "KI Signature", None, None, "Ken Ishiwata Signature"),
]


# Sourced specs (still verified=false — for Wayne to confirm). Japan-market figures where the
# source is audio-database.com; US figures from classicreceivers.com / vintageaudioexchange.
# w=watts/ch into 8ohm, thd=%, fr=freq response Hz, wt=weight kg, yen=price in thousands of yen.
# ys/ye override the roadmap years only when the source gives a firmer figure.
SPECS = {
    # --- Integrated / PM (audio-database.com, Japan-market) ---
    "1030":   dict(ys=1972, w=15,  thd=0.5,   fr="15-40000", wt=7.7,  yen=39.9,  ckt="Entry pre-main; simplified Marantz design", src="audio-database.com"),
    "1060":   dict(ys=1972, w=30,  thd=0.5,   fr="20-20000", wt=8.4,  yen=54.9,  ckt="Quasi-complementary; 3-stage direct-coupled NF equalizer", src="audio-database.com"),
    "1070":   dict(ys=1975, w=40,  thd=0.3,   fr="20-20000", wt=8.4,  yen=69.9,  ckt="Inverting Darlington; mid-range tone control; speaker matrix", src="audio-database.com"),
    "1150":   dict(ys=1975, w=80,  thd=0.1,   fr="20-20000", wt=15.0, yen=125.0, ckt="Direct-coupled push-pull, inverted Darlington output", src="audio-database.com"),
    "1200":   dict(ys=1972, w=100, thd=0.15,  fr="6-80000",  wt=14.1, yen=295.0, ckt="Differential input, pure-complementary all-stage direct-coupled OCL, Class AB", src="audio-database.com"),
    "1200B":  dict(ys=1974, w=100, thd=0.15,  fr="20-20000", wt=14.1, yen=325.0, ckt="Model 3300 preamp + Model 240 power amp in one; variable overlap drive", src="audio-database.com"),
    "1250":   dict(ys=1976, w=130, thd=0.1,   fr="20-20000", wt=18.5, yen=195.0, ckt="3-stage direct-coupled NF differential equalizer; tri-circuit routing", src="audio-database.com"),
    "PM-5 Esotec": dict(w=80, thd=0.015, fr="20-20000", wt=13.0, yen=100.0, ckt="Switchable pure Class A (20W) / Class AB (80W); complete push-pull DC amplifier", src="audio-database.com"),
    "PM-54":  dict(ys=1984, w=80,  thd=0.015, fr="20-20000", wt=8.8,  yen=62.0,  ckt="AVSS (Auto Voltage Shift Supply)", src="audio-database.com"),
    "PM-84":  dict(ys=1983, w=120, thd=0.015, fr="20-20000", wt=18.0, yen=125.0, ckt="Quarter-A circuit + AVSS; pure Class A to 1/4 power", src="audio-database.com"),
    "PM-80":  dict(ys=1989, w=100, thd=0.0008, fr="10-100000", wt=17.5, yen=65.0, ckt="Parallel push-pull, 3-stage Darlington; Class A (20W) / AB (100W) switchable", src="audio-database.com"),
    "PM-94":  dict(ys=1985, w=140, thd=0.005, fr="20-20000", wt=23.0, yen=228.0, ckt="Triple push-pull MOS-FET; Quarter-A circuit; Class A (35W) / AB (140W)", src="audio-database.com"),
    "PM66 KI Signature": dict(w=50, thd=0.03, fr="10-100000", wt=6.6, ckt="Ken Ishiwata Signature; figures from base PM-66SE (KI edition may differ)", src="audio-database.com"),
    # --- US receivers / quad (classicreceivers.com, vintageaudioexchange) ---
    "2215":  dict(w=15, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2230":  dict(w=30, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2245":  dict(w=45, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2270":  dict(ys=1971, ye=1976, w=70, thd=0.3, wt=17.5, ckt="Stereophonic solid-state receiver", src="classicreceivers.com"),
    "2265":  dict(w=65, ckt="Stereophonic solid-state receiver", src="classicreceivers.com"),
    "2215B": dict(w=15, ckt="Stereophonic solid-state receiver", src="hqaudios/classicreceivers"),
    "4230":  dict(ys=1973, ye=1978, w=30,  wt=14.2, ckt="Quadradial 2+4 receiver; 30W/ch stereo, 12W/ch quad (8ohm)", src="classicreceivers.com"),
    "4270":  dict(ys=1974, w=70,  wt=18.4, ckt="Quadradial 2+4 receiver; 70W/ch stereo, 25W/ch quad (8ohm)", src="classicreceivers.com"),
    "4400":  dict(ys=1974, ye=1978, w=125, ckt="Quadradial 2+4 receiver; 125W/ch stereo, 50W/ch quad", src="classicreceivers.com"),
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
            note += f" Specs sourced from {sp['src']} (still unverified)."
        rec = {
            "id": f"marantz-{slug(model)}" + (f"-{ys}" if ys else ""),
            "brand": "Marantz",
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
            "ps_type": None,
            "amp_circuit": sp.get("ckt"),
            "weight_kg": sp.get("wt"),
            "special_features": None,
            "pros": None,
            "cons": None,
            "collector_ranking": "Unranked",
            "price_confidence": "Low" if has_price else "None",
            "last_price_check": LAST_CHECK if has_price else None,
            "collector_info": {"known_issues": None, "collector_notes": None},
            "restorer_info": {
                "known_failure_points": [],
                "bias_spec_mv": None,
                "service_manual_link": None,
                "recap_difficulty": None,
                "recap_notes": None,
                "estimated_recap_cost_usd": None,
                "common_faults": [],
            },
            "best_buy": {"rating": None, "reason": None},
            "capacitors": [],
            "links": {"audio_database": None, "hifi_engine": None, "sansui_us": None},
            "notes": note,
            "verified": False,
            "avg_price_usd_3mo": usd,
            "price_basis": None,
            "year_source": sp.get("src", "wayne-list (FB/YouTube, unverified)"),
            "price_thb_listings": thb or [],
            "usd_msrp": None,
            "market": None,
            "sonic_signature": None,
            "thb_status": None,
        }
        records.append(rec)
    return records


if __name__ == "__main__":
    recs = build()
    out = os.path.join(os.path.dirname(__file__), "..", "data", "marantz.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
        f.write("\n")
    ids = [r["id"] for r in recs]
    assert len(ids) == len(set(ids)), "duplicate ids: " + str([i for i in ids if ids.count(i) > 1])
    priced = sum(1 for r in recs if r["price_thb_listings"] or r["avg_price_usd_3mo"] is not None)
    print(f"wrote {len(recs)} Marantz records ({priced} with a price) -> data/marantz.json")
