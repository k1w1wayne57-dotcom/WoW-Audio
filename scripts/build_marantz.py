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
    ("Model 16", None, 1966, 1969, "Early Solid-State", None, None, "Two variants exist - US ~80W (35 lb) and a 100W version; specs shown are the 100W audio-database listing"),
    ("Superscope BLA-530", None, 1967, 1971, "Superscope", None, None, None),
    # --- Japan-market models ---
    ("Model 18", "Receiver", None, None, "Japan-market", None, None, None),
    ("Model 19", "Receiver", None, None, "Japan-market", None, None, None),
    ("Model 22", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 25", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 26", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    ("Model 27", "Receiver", 1969, 1971, "Japan-market", None, None, None),
    # --- Integrated amps 10xx/12xx ---
    ("1015",  "Tape Deck", 1980, 1980, "Cassette Deck", None, None, "Full model is Marantz SD-1015"),
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
    ("3300",  None,          1975, 1977, "Preamp / Control", None, None,
        "Stereo control preamplifier (Wayne's list had it under Quad; confirmed a preamp via the Model 1200B, which pairs it with the Model 240 power amp)"),
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
    # --- Notable models added from HiFiShark sweep (grails + mainstream 22xx we'd skipped) ---
    ("Model 7", "Preamp", 1958, 1967, "Tube Era", None, None, "Model 7/7C tube control preamp — the definitive vintage tube preamp"),
    ("Model 10B", "Tuner", 1964, 1968, "Tube Era", None, None, "Tube FM tuner with CRT scope — regarded a top-3 vintage tuner"),
    ("Model 250", "Power Amp", 1971, 1973, "Separates", None, None, "Pairs with the Model 3300 preamp"),
    ("2240", "Receiver", 1974, 1975, "22XX Receiver (1st gen)", None, None, None),
    ("2275", "Receiver", 1975, 1977, "22XX Heavyweight", None, None, None),
    ("2252B", "Receiver", 1977, 1979, "22XX B Receiver", None, None, None),
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
    "Model 16": dict(ys=1969, ye=1973, type="Power Amp", w=100, thd=0.1, fr="10-60000", wt=14.5, ps="Dual Mono", yen=195.0, ckt="Solid-state stereo power amp; fully dual-mono (independent L/R power)", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model16.html"),
    "Superscope BLA-530": dict(ys=1978, ye=None, type="Integrated", thd=0.1, fr="20-50000", ckt="Superscope (Marantz budget division) stereo integrated amp; 30W/ch into 4ohm, damping 45", src="hifiengine.com", url="https://www.hifiengine.com/manual_library/superscope/bla-530.shtml"),
    "Model 22": dict(ys=1969, w=40, thd=0.3, wt=16.8, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-model-22"),
    "Model 25": dict(ys=1969, w=30, thd=0.3, fr="20-20000", ckt="Stereophonic solid-state receiver", src="hifiengine/reverb", url="https://www.hifiengine.com/manual_library/marantz/model-25.shtml"),
    "Model 26": dict(ys=1970, w=14, ckt="Stereophonic solid-state receiver (smallest of the early series)", src="hifiengine/reverb", url="https://www.hifiengine.com/manual_library/marantz/model-26.shtml"),
    "Model 27": dict(ys=1970, w=30, thd=0.3, fr="20-20000", wt=6.4, ckt="Stereophonic solid-state receiver", src="hifiengine/reverb", url="https://www.hifiengine.com/manual_library/marantz/model-27.shtml"),
    "Model 18": dict(ys=1968, w=40, thd=0.2, fr="20-20000", ckt="First Marantz receiver; solid-state with tube oscilloscope tuning display", src="soundandvision/classicreceivers", url="https://www.hifiengine.com/manual_library/marantz/model-18.shtml"),
    "Model 19": dict(ys=1973, ye=1974, w=50, thd=0.15, fr="20-20000", wt=20.9, ckt="Solid-state receiver with built-in oscilloscope tuning display", src="marantz.com/reverb", url="https://www.hifiengine.com/manual_library/marantz/model-19.shtml"),
    "3300":   dict(type="Preamp", ckt="Stereo control preamplifier; paired with the Model 240 power amp in the 1200B", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model3300-e.html"),
    "1015":   dict(ys=1980, type="Tape Deck", fr="35-17000", wt=5.7, ckt="SD-1015 2-head stereo cassette deck; Dolby-B, normal/chrome/metal tape", src="radiomuseum/cassettedeck.org", url="https://www.hifiengine.com/manual_library/marantz/sd1015.shtml"),
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
    "1300 DC":   dict(ys=1978, ye=1982, w=150, thd=0.03, fr="20-20000", wt=24.5, ckt="Flagship DC integrated; direct-coupled, high-current output", src="hifi-wiki/reverb", url="https://www.hifiengine.com/manual_library/marantz/1300dc.shtml"),
    "PM-710 DC": dict(ys=1981, ye=1983, w=80, thd=0.03, fr="10-60000", wt=15.0, ckt="Console DC integrated amplifier", src="radiomuseum/hifi-wiki", url="https://www.hifiengine.com/manual_library/marantz/pm710dc.shtml"),
    "PM 500":    dict(ys=1980, ye=1981, w=50, thd=0.03, fr="10-60000", wt=13.0, ckt="Console integrated amplifier (built-in EQ)", src="radiomuseum/hifiengine", url="https://www.hifiengine.com/manual_library/marantz/pm500.shtml"),
    # --- US receivers / quad (classicreceivers.com, vintageaudioexchange) ---
    "2215":  dict(w=15, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2230":  dict(w=30, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2245":  dict(w=45, ckt="Stereophonic solid-state receiver", src="Marantz 22xx convention (2270/2265/2215B corroborated)"),
    "2270":  dict(ys=1971, ye=1976, w=70, thd=0.3, wt=17.5, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2270"),
    "2265":  dict(w=65, ckt="Stereophonic solid-state receiver", src="classicreceivers.com"),
    "2215B": dict(w=15, ckt="Stereophonic solid-state receiver", src="hqaudios/classicreceivers"),
    "4230":  dict(ys=1973, ye=1978, w=30,  wt=14.2, ckt="Quadradial 2+4 receiver; 30W/ch stereo, 12W/ch quad (8ohm)", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4230"),
    "4270":  dict(ys=1974, w=70,  wt=18.4, ckt="Quadradial 2+4 receiver; 70W/ch stereo, 25W/ch quad (8ohm)", src="classicreceivers.com", url=["https://classicreceivers.com/marantz-4270-quad", "https://www.hifiengine.com/manual_library/marantz/4270.shtml"]),
    "4300":  dict(ys=1972, ye=1978, w=100, ckt="Quadradial 2+4 receiver; 100W/ch stereo", src="classicreceivers.com", url="https://classicreceivers.com/marantz-4300"),
    "4400":  dict(ys=1976, ye=1977, w=125, thd=0.15, fr="20-20000", wt=23.4, ckt="Quadradial 2+4 receiver; 125W/ch stereo, 50W/ch quad; damping 40", src="hifiengine/classicreceivers", url=["https://classicreceivers.com/marantz-4400", "https://www.hifiengine.com/manual_library/marantz/4400.shtml"]),
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
    # --- Added models (HiFiShark sweep) ---
    "Model 7": dict(ys=1958, ye=1967, type="Preamp", wt=6.8, ckt="Tube control preamplifier; 3x 12AX7 per channel; ~130,000 made", src="theabsolutesound/VTA", url="https://vintagetechnologyarchive.com/audio/marantz/model-7c/"),
    "Model 10B": dict(ys=1964, ye=1968, type="Tuner", ckt="Tube FM stereo tuner; 22 tubes, CRT tuning scope; a top-3 vintage tuner", src="radiomuseum/VTA", url="https://www.radiomuseum.org/r/marantz_stereo_fm_tuner_10b.html"),
    "Model 250": dict(ys=1971, ye=1973, type="Power Amp", w=125, ckt="Solid-state stereo power amp; 125W (8ohm) / 150W (4ohm); dual VU meters", src="audio-database.com", url="https://audio-database.com/MARANTZ/amp/model250-e.html"),
    "2240": dict(ys=1974, w=40, thd=0.25, fr="20-20000", wt=14.0, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2240"),
    "2275": dict(ys=1975, ye=1977, w=75, thd=0.25, fr="20-20000", wt=17.7, ckt="Stereophonic solid-state receiver", src="classicreceivers.com", url="https://classicreceivers.com/marantz-2275"),
    "2252B": dict(ys=1977, ye=1979, w=52, fr="20-20000", wt=14.2, ckt="Stereophonic solid-state receiver", src="radiomuseum/VTA", url="https://vintagetechnologyarchive.com/audio/marantz/2252b/"),
}


# Per-brand collector ranking (Sansui-style bands), ordered by HiFiShark market price
# (Wayne's rule: price approximates collectability). Models without a reliable price are placed
# by estimate/type and noted. Adjustable — a beloved-but-common model like the 2270 sits by its
# price, not its fame; say the word to hand-boost any.
RANKINGS = {
    # Top 10 — grails ($3k+ market)
    "2600": "Top 10", "Model 9": "Top 10", "2500": "Top 10", "2385": "Top 10", "1300 DC": "Top 10",
    "2330B": "Top 10", "4400": "Top 10", "Model 8": "Top 10", "2325": "Top 10", "Model 19": "Top 10",
    # Top 10-20 — ~$1.1k-2k
    "4270": "Top 10-20", "2285B": "Top 10-20", "1250": "Top 10-20", "4300": "Top 10-20",
    "2265": "Top 10-20", "PM-94": "Top 10-20", "2270": "Top 10-20", "1200B": "Top 10-20",
    "Model 15": "Top 10-20", "2245": "Top 10-20",
    # Top 20-30 — ~$800-1k
    "2250": "Top 20-30", "2250B": "Top 20-30", "Model 18": "Top 20-30", "3300": "Top 20-30",
    "PM-84": "Top 20-30", "1150": "Top 20-30", "2260": "Top 20-30", "2238B": "Top 20-30",
    "Model 16": "Top 20-30", "4230": "Top 20-30",
    # Top 30-40 — ~$550-790
    "PM-5 Esotec": "Top 30-40", "Model 22": "Top 30-40", "1200": "Top 30-40", "PM-710 DC": "Top 30-40",
    "2235B": "Top 30-40", "2216B": "Top 30-40", "Model 25": "Top 30-40", "Model 14": "Top 30-40",
    "Model 27": "Top 30-40", "PM-80": "Top 30-40",
    # Top 40-50 — ~$350-490
    "PM66 KI Signature": "Top 40-50", "2230": "Top 40-50", "2215": "Top 40-50", "2215B": "Top 40-50",
    "2220B": "Top 40-50", "1090": "Top 40-50", "2218": "Top 40-50", "PM-54": "Top 40-50",
    "1070": "Top 40-50", "1060": "Top 40-50",
    # Unranked — budget / cassette / lowest market
    "Model 26": "Unranked", "2210": "Unranked", "1030": "Unranked",
    "PM 500": "Unranked", "1015": "Unranked", "Superscope BLA-530": "Unranked",
    # Added models (placed by price tier)
    "Model 10B": "Top 10",
    "2275": "Top 10-20", "Model 7": "Top 10-20", "Model 250": "Top 10-20", "2240": "Top 10-20",
    "2252B": "Top 20-30",
}


# Latest USD market price (HiFiShark median, ~2026), approximates collectability. EUR->USD ~1.08.
PRICES = {
    "2600": 13000, "Model 9": 12000, "2500": 9000, "2385": 4900, "1300 DC": 4300,
    "2330B": 3300, "4400": 3300, "Model 8": 3100, "2325": 3000,
    "4270": 1950, "2285B": 1900, "1250": 1650, "4300": 1400, "2265": 1200, "PM-94": 1200,
    "2270": 1135, "1200B": 1100, "Model 15": 1100, "2245": 1100, "2250": 1000, "Model 18": 1000,
    "3300": 925, "PM-84": 925, "1150": 925, "2238B": 870, "Model 16": 800, "4230": 790,
    "PM-5 Esotec": 790, "Model 22": 650, "1200": 650, "PM-710 DC": 630, "2216B": 565,
    "Model 27": 500, "2230": 490, "2215": 490, "2215B": 490, "PM-80": 450, "PM66 KI Signature": 400,
    "1090": 400, "2218": 400, "1070": 380, "PM 500": 300,
    "Model 10B": 3400, "2275": 2400, "Model 7": 2000, "Model 250": 1950, "2240": 1420, "2252B": 870,
}

# Best Buy (1-5 stars) = collectability (USD price) AND how cheap the Thai baht price is vs USD.
# Only the Thai-priced models can be scored (needs both a Thai price and a USD market price).
BESTBUY = {
    "4400": (5, "Grail quadradial (~$3,300 USD) turning up in Thailand near ฿39k (~$1,100) — exceptional value for a flagship."),
    "4270": (4, "Sought-after quad (~$1,950 USD) at ~฿34k (~$970) — strong value on a collectable receiver."),
    "2238B": (4, "38W receiver (~$870 USD) around ฿16.5k (~$470) — a good discount to the global market."),
    "2216B": (4, "~$565 USD abroad vs ~฿7k (~$200) locally — well under market."),
    "2215B": (4, "Entry blue-dial 22xx (~$490 USD) at ฿5.2k (~$150) — a cheap way into the line."),
    "PM-710 DC": (4, "DC integrated (~$630 USD) at ฿6.9k (~$200) — a big discount to overseas prices."),
    "4230": (4, "Quad receiver (~$790 USD) at ฿15k (~$430) — good value entry to Quadradial."),
    "2265": (3, "Collectable 65W (~$1,200 USD), but ฿27.8k (~$790) is close to global pricing."),
    "1070": (3, "Modest integrated (~$380 USD) at ฿5.9k (~$170) — fair value."),
    "PM-5 Esotec": (3, "Class-A Esotec (~$790 USD) at ฿16.5–18.5k (~$470–530) — reasonable."),
    "2218": (3, "18W receiver (~$400 USD) at ฿8.2k (~$235) — modest value."),
    "1090": (2, "45W integrated (~$400 USD) at ฿9k (~$260) — only a small discount."),
    "PM 500": (2, "Budget-era console (~$300 USD) at ฿8.5k (~$245) — little upside."),
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
            "collector_ranking": RANKINGS.get(model, "Unranked"),
            "price_confidence": "Medium" if model in PRICES else ("Low" if has_price else "None"),
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
            "best_buy": {"rating": BESTBUY.get(model, (None,))[0],
                         "reason": BESTBUY[model][1] if model in BESTBUY else None},
            "capacitors": [],
            "links": links,
            "notes": note,
            "verified": False,
            "verification": verification,
            "avg_price_usd_3mo": PRICES.get(model, usd),
            "price_basis": "hifishark median 2026" if model in PRICES else None,
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
