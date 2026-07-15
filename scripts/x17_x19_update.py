"""Add sonic_signature + collector_ranking for the AU-x17 / AU-x19 families and their
JDM counterparts. Twins share the same signature/rank (same amp, different market badge).
Sources: AudioKarma, audioreview, HiFi Collector, sansui.us.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

WARM_517 = ("Classic warm Sansui: sweet, full and rich with an organic, forgiving presentation - "
            "a touch warmer and more forgiving than the AU-717. Non-fatiguing over long sessions "
            "while keeping real power and clarity.")
WARM_717 = ("The definitive 'classic Sansui sound': warm, full and balanced - but warm never means "
            "dull; the detail is all there, with hard-hitting bass, a great soundstage and high "
            "musicality.")
TRANS_919 = ("A generation ahead in sophistication and accuracy: leaves the warm Sansui house voice "
             "behind for a transparent, uncoloured presentation with incredible detail and a "
             "remarkably wide soundstage.")
TRANS_819 = ("Diamond Differential transparency: uncoloured and highly detailed with a wide "
             "soundstage - the neutral, accurate side of Sansui rather than the warm classic voice.")
TRANS_719 = ("Diamond Differential circuitry borrowed from its big brother the AU-919 - sonically "
             "much closer to the 919's transparent, detailed neutrality than to the warmer AU-717.")
TRANS_519 = ("An evolution of the AU-517: similar in design to the AU-717 (slightly more power) but "
             "voiced closer to the AU-919 - more transparent and uncoloured than the warm 17-series.")
WARM_417 = ("Essentially an AU-517 with a single power supply rather than dual-mono - the same warm, "
            "full 17-series voice with a little less grip and drive.")
FAMILY_17 = ("17-series family character: the warm, musical Sansui house voice in a lighter, "
             "lower-powered package - forgiving and easy to listen to rather than analytical. "
             "(Family-level description; no model-specific reviews found.)")

# model -> (sonic_signature, collector_ranking)
DATA = {
    # --- x17 (export) + JDM twins: the warm classic voice ---
    "AU-717":   (WARM_717, "Top 10"),
    "AU-707":   (WARM_717, "Top 10"),        # JDM twin of AU-717
    "AU-517":   (WARM_517, "Top 10-20"),
    "AU-607":   (WARM_517, "Top 10-20"),     # JDM twin of AU-517
    "AU-417":   (WARM_417, "Top 20-30"),
    "AU-317":   (FAMILY_17, "Top 30-40"),
    "AU-317II": (FAMILY_17, "Top 30-40"),
    "AU-217":   (FAMILY_17, "Top 40-50"),
    "AU-217II": (FAMILY_17, "Top 40-50"),
    "AU-117":   (FAMILY_17, "Top 40-50"),
    "AU-117II": (FAMILY_17, "Top 40-50"),
    # --- x19 (export) + JDM twins: Diamond Differential transparency ---
    "AU-919":   (TRANS_919, "Top 10"),
    "AU-D907":  (TRANS_919, "Top 10"),       # JDM twin of AU-919
    "AU-819":   (TRANS_819, "Top 10-20"),
    "AU-D707":  (TRANS_819, "Top 10-20"),    # JDM twin of AU-819
    "AU-719":   (TRANS_719, "Top 10-20"),
    "AU-519":   (TRANS_519, "Top 20-30"),
}

for jm, (sig, rank) in DATA.items():
    e = by.get(jm)
    if not e:
        print("  !! not found:", jm); continue
    e["sonic_signature"] = sig
    old = e.get("collector_ranking")
    e["collector_ranking"] = rank
    print(f"  {jm:9s} rank {str(old):12s} -> {rank}")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"\nsonic_signature set on {len(DATA)} models.")
