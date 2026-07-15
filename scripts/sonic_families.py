"""Apply family/era-level sonic signatures where Sansui's character is documented.
Never overwrites the model-specific signatures already set (the x17/x19 families).
Each family text is explicitly labelled family-level so it isn't mistaken for a
model-specific listening report. Groups with no documented character are skipped.
Sources: AudioKarma, audioreview, hifi-wiki, thevintageknob, ecoustics, Wayne's G-series notes.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

ALPHA = ("Alpha-series voicing: a move to a more neutral tone with very good clarity and detail "
         "while staying musically involving - refined, with layers of depth, pinpoint imaging and "
         "crisper, more refined highs than the older warm Sansuis. The 907 tier adds a beefier "
         "supply and the most even tonal balance. (Family-level: alpha-X Balanced series.)")
XBAL = ("X-Balanced voicing: brighter and more resolving than the older Sansuis, which carry more "
        "tone and warmth - the fully balanced topology trades the classic house warmth for speed, "
        "grip and resolution. (Family-level: X-Balanced series.)")
SFF = ("Super Feedforward voicing: clean and low in distortion, notably good with strings, but with "
       "slightly less punch and bottom-end weight than the earlier warm Sansuis. "
       "(Family-level: Super Feedforward D-series.)")
CLASSIC = ("Classic-era Sansui: warm, organic midrange with smooth clarity - often described as "
           "'tube-like', with a lush, engaging presentation and a smooth top end. "
           "(Family-level: late-60s/early-70s AU line.)")
MONSTER = ("Monster-receiver voicing: warm, full-bodied and powerful with exceptional clarity - very "
           "musical, clear vocals and strong bass; rich enough that it doesn't need volume to come "
           "alive. (Family-level: 8080/9090-era receivers.)")
TUBE = ("Tube-era Sansui: the warm, rich valve presentation - smooth top end and a full, engaging "
        "midrange. (Family-level: tube era.)")
G1 = ("G-series 1st generation: the classic silver-face voicing - warm and musical. "
      "(Family-level: G-series 1st gen.)")
G3 = ("G-series Pure Power DC: high-speed direct-coupled circuitry for lower distortion - cleaner "
      "and tighter than the warm first-generation G receivers. (Family-level: G-series 3rd gen.)")

MONSTERS = {"9090", "9090DB", "8080", "8080DB", "7070", "6060", "5050"}
ACCESSORY = ("Tuner", "Tape Deck", "Quad Synth", "Quad Decoder", "Reverb Unit", "Equalizer")

def pick(e):
    if e.get("sonic_signature"):
        return None                      # model-specific already set - leave it
    jm = e["jdm_model"]; typ = e.get("type") or ""
    ac = (e.get("amp_circuit") or "").lower()
    sf = (e.get("special_features") or "")
    series = e.get("series") or ""
    yr = e.get("year_start") or 0
    if typ in ACCESSORY:
        return None                      # a tuner/deck has no amp voicing to describe
    if "alpha-x balanc" in ac: return ALPHA
    if "x balanc" in ac or "x-balanc" in ac: return XBAL
    if "super feedforward" in ac or "super ff" in ac: return SFF
    if series == "Tube Era" or typ.startswith("Tube"): return TUBE
    if jm.upper().startswith("G-"):
        if "1st generation" in sf: return G1
        if "3rd generation" in sf: return G3
        return None                      # 2nd-gen / monsters: no documented voicing
    if jm in MONSTERS: return MONSTER
    if typ in ("Integrated", "Receiver") and 1966 <= yr <= 1973: return CLASSIC
    return None

added = 0
for e in db:
    s = pick(e)
    if s:
        e["sonic_signature"] = s
        added += 1

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

total = sum(1 for e in db if e.get("sonic_signature"))
print(f"Added family-level signatures: {added}")
print(f"Models with a sonic_signature now: {total} / {len(db)}")
from collections import Counter
missing = [e["jdm_model"] for e in db if not e.get("sonic_signature")]
print(f"Still none: {len(missing)}")
print("  by type:", dict(Counter(next(x['type'] for x in db if x['jdm_model']==m) for m in missing)))
