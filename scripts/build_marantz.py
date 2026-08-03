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
    ("Model 14", None, 1966, 1969, "Early Solid-State", None, None, None),
    ("Model 15", None, 1966, 1969, "Early Solid-State", None, None, None),
    ("Model 16", None, 1966, 1969, "Early Solid-State", None, None, "Early solid-state; type unconfirmed"),
    ("Superscope BLA-530", None, 1967, 1971, "Superscope", None, None, None),
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
CONV = "Marantz 22xx model-number convention (last two digits = W/ch; corroborated by 8+ sourced models)"
SPECS = {
    # --- Tube era (radiomuseum / stereophile / hifiengine) ---
    "Model 8": dict(ys=1959, ye=1962, w=30, ckt="Stereo tube power amp; 2x30W, EL34/6CA7 output (8 tubes); revised as Model 8B", src="radiomuseum.org", url="https://www.radiomuseum.org/r/marantz_model_8.html"),
    "Model 9": dict(ys=1961, ye=1968, w=70, fr="12-40000", ckt="Mono tube monoblock (EL34 push-pull); 40W triode-switchable; pair for stereo", src="radiomuseum.org", url="https://www.radiomuseum.org/r/marantz_model_9.html"),
    "Model 14": dict(ys=1968, type="Power Amp", w=60, thd=0.1, fr="10-60000", wt=8.17, ckt="Solid-state mono (single-channel) power amp; 60W into 8ohm / 70W into 4ohm", src="radiomuseum.org", url="https://www.radiomuseum.org/r/marantz_single_channel_amplifier_model_fourteen_14.html"),
    "Model 15": dict(ys=1966, type="Power Amp", w=60, thd=0.1, fr="10-60000", wt=15.4, ps="Dual Mono", ckt="Solid-state stereo power amp; dual-mono (separate power supply per channel); 60W into 8ohm / 70W into 4ohm", src="hifiengine.com", url="https://www.hifiengine.com/manual_library/marantz/15.shtml"),
    "Superscope BLA-530": dict(ys=1978, ye=None, type="Integrated", thd=0.1, fr="20-50000", ckt="Superscope (Marantz budget division) stereo integrated amp; 30W/ch into 4ohm, damping 45", src="hifiengine.com", url="https://www.hifiengine.com/manual_library/superscope/bla-530.shtml"),
    "Model 22": dict(ys=1969, w=40, thd=0.3, wt=16.8, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-model-22"),
    # --- Integrated / PM (audio-database.com, Japan-market) ---
    "1030":   dict(ys=1972, w=15,  thd=0.5,   fr="15-40000", wt=7.7,  yen=39.9,  ckt="Entry pre-main; simplified Marantz design", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1030-e.html"),
    "1090":   dict(ys=1977, w=45,  thd=0.1,   fr="10-60000", wt=9.5,  ckt="Console stereo integrated amplifier", src="hifivintage.eu", url="https://hifivintage.eu/en/amplifiers/5595-marantz-model-1090.html"),
    "1060":   dict(ys=1972, w=30,  thd=0.5,   fr="20-20000", wt=8.4,  yen=54.9,  ckt="Quasi-complementary; 3-stage direct-coupled NF equalizer", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1060-e.html"),
    "1070":   dict(ys=1975, w=40,  thd=0.3,   fr="20-20000", wt=8.4,  yen=69.9,  ckt="Inverting Darlington; mid-range tone control; speaker matrix", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1070.html"),
    "1150":   dict(ys=1975, w=80,  thd=0.1,   fr="20-20000", wt=15.0, yen=125.0, ckt="Direct-coupled push-pull, inverted Darlington output", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1150-e.html"),
    "1200":   dict(ys=1972, w=100, thd=0.15,  fr="6-80000",  wt=14.1, yen=295.0, ckt="Differential input, pure-complementary all-stage direct-coupled OCL, Class AB", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1200-e.html"),
    "1200B":  dict(ys=1974, w=100, thd=0.15,  fr="20-20000", wt=14.1, yen=325.0, ckt="Model 3300 preamp + Model 240 power amp in one; variable overlap drive", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1200b.html"),
    "1250":   dict(ys=1976, w=130, thd=0.1,   fr="20-20000", wt=18.5, yen=195.0, ckt="3-stage direct-coupled NF differential equalizer; tri-circuit routing", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model1250-e.html"),
    "PM-5 Esotec": dict(w=80, thd=0.015, fr="20-20000", wt=13.0, yen=100.0, ckt="Switchable pure Class A (20W) / Class AB (80W); complete push-pull DC amplifier", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-5-e.html"),
    "PM-54":  dict(ys=1984, w=80,  thd=0.015, fr="20-20000", wt=8.8,  yen=62.0,  ckt="AVSS (Auto Voltage Shift Supply)", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-54-e.html"),
    "PM-84":  dict(ys=1983, w=120, thd=0.015, fr="20-20000", wt=18.0, yen=125.0, ckt="Quarter-A circuit + AVSS; pure Class A to 1/4 power", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-84-e.html"),
    "PM-80":  dict(ys=1989, w=100, thd=0.0008, fr="10-100000", wt=17.5, yen=65.0, ckt="Parallel push-pull, 3-stage Darlington; Class A (20W) / AB (100W) switchable", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-80-e.html"),
    "PM-94":  dict(ys=1985, w=140, thd=0.005, fr="20-20000", wt=23.0, yen=228.0, ckt="Triple push-pull MOS-FET; Quarter-A circuit; Class A (35W) / AB (140W)", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-94-e.html"),
    "PM66 KI Signature": dict(w=50, thd=0.03, fr="10-100000", wt=6.6, ckt="Ken Ishiwata Signature; figures from base PM-66SE (KI edition may differ)", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/pm-66sev-e.html"),
    # --- US receivers / quad (classicreceivers.com, vintageaudioexchange) ---
    "2215":  dict(w=15, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2230":  dict(w=30, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2245":  dict(w=45, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2270":  dict(ys=1971, ye=1976, w=70, thd=0.3, wt=17.5, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2270"),
    "2265":  dict(w=65, ckt="Stereophonic solid-state receiver", src="classicreceivers.com"),
    "2215B": dict(w=15, ckt="Stereophonic solid-state receiver", src="hqaudios/classicreceivers"),
    "4230":  dict(ys=1973, ye=1978, w=30,  wt=14.2, ckt="Quadradial 2+4 receiver; 30W/ch stereo, 12W/ch quad (8ohm)", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4230"),
    "4270":  dict(ys=1974, w=70,  wt=18.4, ckt="Quadradial 2+4 receiver; 70W/ch stereo, 25W/ch quad (8ohm)", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4270-quad"),
    "4300":  dict(ys=1972, ye=1978, w=100, ckt="Quadradial 2+4 receiver; 100W/ch stereo", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4300"),
    "4400":  dict(ys=1974, ye=1978, w=125, ckt="Quadradial 2+4 receiver; 125W/ch stereo, 50W/ch quad", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4400"),
    # --- 22xx B-models: watts from Marantz naming convention (year/weight not sourced) ---
    "2210":  dict(w=10, ckt="Stereophonic solid-state receiver", src=CONV),
    "2216B": dict(w=16, ckt="Stereophonic solid-state receiver", src=CONV),
    "2218":  dict(w=18, ckt="Stereophonic solid-state receiver", src=CONV),
    "2220B": dict(w=20, ckt="Stereophonic solid-state receiver", src=CONV),
    "2235B": dict(w=35, ckt="Stereophonic solid-state receiver", src=CONV),
    "2238B": dict(ys=1977, w=38, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2238b"),
    "2250":  dict(w=50, ckt="Stereophonic solid-state receiver", src=CONV),
    "2250B": dict(w=50, ckt="Stereophonic solid-state receiver", src=CONV),
    "2260":  dict(w=60, ckt="Stereophonic solid-state receiver", src=CONV),
    "2285B": dict(ys=1977, w=85, ckt="Stereophonic solid-state receiver (heavyweight 22xx)", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2285b"),
    # --- 23xx heavyweight receivers ---
    "2325":  dict(ys=1974, ye=1976, w=125, thd=0.1,  wt=22.5, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2325"),
    "2330B": dict(ys=1977, ye=1979, w=130, thd=0.07, wt=22.5, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2330"),
    "2385":  dict(ys=1977, ye=1980, w=185, wt=26.0,  ckt="Stereophonic solid-state receiver (flagship 23xx)", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2385"),
    # --- Champagne / Monster receiver era ---
    "2500":  dict(ys=1977, ye=1979, w=250, thd=0.05, wt=27.0, ckt="Monster-era flagship receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2500"),
    "2600":  dict(ys=1978, w=300, ckt="Flagship monster receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2600"),
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
        # Trust tier: "sourced" if backed by a reference DB / spec sheet. Convention-derived
        # wattages and roadmap/FB-only records are "unconfirmed". "verified" is reserved for
        # Wayne's own confirmation.
        src_str = sp.get("src", "")
        if sp and "convention" not in src_str.lower():
            verification = "sourced"
        else:
            verification = "unconfirmed"
        # Route the source page URL into the links block for a clickable provenance link.
        links = {"audio_database": None, "hifi_engine": None, "sansui_us": None, "source": None}
        src_url = sp.get("url")
        if src_url:
            if "audio-database.com" in src_url:
                links["audio_database"] = src_url
            elif "hifiengine.com" in src_url:
                links["hifi_engine"] = src_url
            else:
                links["source"] = src_url
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
            "ps_type": sp.get("ps"),
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
            "links": links,
            "notes": note,
            "verified": False,
            "verification": verification,
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
