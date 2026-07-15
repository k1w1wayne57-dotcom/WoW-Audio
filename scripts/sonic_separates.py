"""Model-specific sonic signatures for the power amps / control amps, from actual owner and
reviewer reports (AudioKarma, Audiofanzine, MyOldVintageHifi, LiQUiD AUDiO, thevintageknob,
1001hifi). These OVERRIDE the family-level labels where the family text is wrong - notably the
B-2102, which the X-Balanced family text called "brighter... trades warmth for grip" while every
actual report calls it sweet and warm.
Separates with no sourced listening impressions are deliberately left blank.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

SIG = {
 "B-2102": ("Sweet and extremely detailed - never brittle or cool. Wonderfully warm and detailed on "
            "voice, acoustic instruments and complex orchestral/choral/operatic material, with "
            "striking stereo imaging; noticeably sweeter than the B-2101 despite near-identical "
            "specs. Unusually load-tolerant for a Sansui power amp - drives speakers dipping to "
            "2 ohms, with roughly 680W/ch instantaneous at 2 ohms. Pairs best with the matching C-2102."),
 "B-2101": ("Close sibling of the B-2102 with near-identical specs, but voiced a touch less sweet - "
            "the B-2102 is the warmer, sweeter of the pair."),
 "C-2102": ("The matching partner to the B-2102. The B/C series was voiced for accurate reproduction "
            "of digital sources while keeping Sansui's musicality - aimed at listeners who "
            "appreciate sonic subtleties."),
 "BA-3000": ("Definition-series voicing: relaxed, warm and silky - gentle and delicate yet articulate, "
             "with details that jump out friskier than other amps, silky airy highs, lifelike mids "
             "and full, generous lows. Open and lush with a deep soundstage and full clarity."),
 "CA-3000": ("Definition-series voicing: relaxed, warm and silky - gentle and delicate yet articulate, "
             "with silky airy highs, lifelike mids and generous lows; open and lush with a deep "
             "soundstage and full clarity. The flagship partner to the BA-3000."),
 "B-2301": ("Enormous horsepower delivered with delicate precision - great, wide, deep, moving music "
            "where the total exceeds the sum of its parts. Needs a full warm-up: the sound becomes "
            "noticeably fuller and smoother once up to temperature."),
 "C-2301": ("Widely regarded as the masterpiece of Sansui's solid-state preamp design - balanced from "
            "input to output with a floating ground and every block isolated from the others."),
 "BA-F1": ("Neutral and clear from DC to the very top - very natural yet warm, flat in response but "
           "capable of heavy bass when pushed. Very honest and highly revealing of the recording; "
           "the most accurate of the Sansui power amps, closest to the technical ideal, with tight "
           "bass and clear highs."),
 "CA-F1": ("Very neutral - it preserves the character of whatever power amp it feeds rather than "
           "imposing its own."),
 "BA-2000": ("Fairly warm and remarkably effortless - very smooth with a holographic quality many call "
             "'the Sansui sound'; some hear it as crisp and clean against a dead-quiet background. "
             "With the matching CA-2000 the pairing turns lush rather than clinically high-end, and "
             "with the right speakers it envelops you with overwhelming force."),
 "CA-2000": ("The matching partner to the BA-2000 - together they sound lush rather than clinically "
             "'high-end', enveloping you with the right speakers."),
 "BA-5000": ("Scale and drama, sonically and visually - Sansui nicknamed it 'The Monster', and it is "
             "widely held to outperform the rest of the BA line."),
}
for jm, sig in SIG.items():
    e = by.get(jm)
    if not e:
        print("  !! not found:", jm); continue
    was_family = "(Family-level" in (e.get("sonic_signature") or "")
    e["sonic_signature"] = sig
    print(f"  {jm:9s} set" + ("  [overrode family-level label]" if was_family else ""))

# sourced restorer issue for the CA-3000
ca = by.get("CA-3000")
if ca:
    ri = ca.setdefault("restorer_info", {})
    issue = ("Primitive feed-through vias on the motherboard and filter board go intermittent with "
             "age, causing channels to drop out - a known CA-3000 weak point.")
    kfp = ri.setdefault("known_failure_points", [])
    if not any("feed-through" in x for x in kfp):
        kfp.insert(0, issue)
        print("  CA-3000: added known feed-through via failure point")

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print(f"\nsonic_signature total: {sum(1 for e in db if e.get('sonic_signature'))}/{len(db)}")
