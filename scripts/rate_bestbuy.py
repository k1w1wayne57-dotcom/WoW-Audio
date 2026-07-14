"""Algorithmic Best Buy pass: rate every model 1-5 on value = performance/build
relative to price positioning, with curated nudges for known bargains/trophies.
Stored as best_buy.rating (int) + a one-line best_buy.reason. Wayne to review.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

def tok(jm):  # normalized token for curated matching
    return jm.upper().replace(" ", "")

# Community "value sweet spots" (punch above price) and "trophies" (you pay for the name)
SWEET = {"AU-517","AU-717","AU-607","AU-707","AU-D607","AU-D707","AU-D607X","AU-D707X",
         "AU-9500","AU-7700","AU-919","AU-D907","AU-D907X","9090","8080","9090DB","8080DB",
         "G-9000","G-8000","G-7700","CA-2000","BA-2000","AU-ALPHA-607","AU-ALPHA-707",
         "AU-6600","AU-517","AU-D607F","AU-D707F"}
TROPHY = {"AU-X1","AU-X11","AU-X111MOS","AU-X1111MOS","G-22000","G-33000","BA-5000",
          "C-2301","C-2302V","B-2302V","AU-ALPHA-907LIMITED","AU-ALPHA-907IMOSLIMITED",
          "AU-111","AU-111VINTAGE","AU-111GVINTAGE","AU-07ANNIVERSARY","AU-20000",
          "AU-11000","B-209THETUBE","AU-D907LIMITED"}

def rate(e):
    w = e.get("watts_per_channel") or 0
    wt = e.get("weight_kg") or 0
    thd = e.get("thd_percent")
    jp = e.get("japan_price_kyen") or 0
    typ = e.get("type") or ""
    t = tok(e["jdm_model"])
    s = 3.2
    pos, neg = [], []

    if wt >= 15: s += 0.5; pos.append("heavyweight build")
    elif wt >= 10: s += 0.25
    if thd is not None and thd <= 0.01: s += 0.3; pos.append("very low distortion")
    if w >= 90: s += 0.25; pos.append("serious power")
    if w and w >= 30 and typ in ("Integrated", "Receiver"): s += 0.2; pos.append("capable daily-driver")
    if w and w <= 15 and wt and wt <= 6: s -= 0.4; neg.append("lightweight/low-power")

    trophy_priced = jp >= 200
    if jp >= 200: s -= 1.0; neg.append("flagship pricing")
    elif jp >= 130: s -= 0.35; neg.append("upper-tier pricing")
    elif 45 <= jp <= 129: s += 0.4; pos.append("mid-tier value sweet spot")
    elif 0 < jp < 45 and w >= 20: s += 0.4; pos.append("cheap yet capable")

    thb = e.get("price_thb_listings") or []
    if thb:
        lo = min(thb)
        if lo <= 6000 and w >= 40: s += 0.9; pos.append(f"seen cheap in TH (from THB {lo:,})")
        elif lo <= 6000: s += 0.4; pos.append(f"affordable in TH (THB {lo:,})")
        elif lo >= 15000: s -= 0.5; trophy_priced = True; neg.append("pricey on the used market")

    if typ in ("Tuner", "Tape Deck", "Quad Synth", "Quad Decoder", "Reverb Unit"):
        s -= 0.25; neg.append("accessory / narrower appeal")

    curated_trophy = t in {tok(x) for x in TROPHY}
    if t in {tok(x) for x in SWEET}: s += 0.8; pos.append("classic bang-for-buck pick")
    if curated_trophy: s -= 1.0; trophy_priced = True; neg.append("collector piece - you pay for the name")

    r = max(1, min(5, round(s)))

    def top(lst, n=2):
        return "; ".join(dict.fromkeys(lst)[:n]) if False else "; ".join(list(dict.fromkeys(lst))[:n])

    if r >= 5:
        lead, detail = "Genuine bargain", top(pos) or "strong all-round value"
    elif r == 4:
        lead, detail = "Strong value", top(pos) or "solid performer for the money"
    elif r == 3:
        lead, detail = "Fair value", (top(pos, 1) or top(neg, 1) or "average for the money")
    elif r == 2:
        lead = "Priced for collectors" if (trophy_priced or curated_trophy) else "Modest performer"
        detail = top(neg) or "limited real-world value"
    else:
        lead = "Priced for collectors" if (trophy_priced or curated_trophy) else "Limited value"
        detail = top(neg) or "little value for the outlay"
    return r, f"{lead} - {detail}."

changed = 0
for e in db:
    r, reason = rate(e)
    e["best_buy"] = {"rating": r, "reason": reason}
    changed += 1

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

from collections import Counter
dist = Counter(e["best_buy"]["rating"] for e in db)
print(f"Rated {changed} models. Distribution (stars: count):")
for r in (5, 4, 3, 2, 1):
    print(f"  {r}: {dist.get(r,0)}")
print("\nSamples:")
for jm in ["AU-717","AU-D907","9090","G-9000","AU-Alpha-607","AU-X1","G-33000",
           "AU-111 VINTAGE","AU-2200","TU-717","AU-Alpha-907NRA"]:
    e = next((x for x in db if x["jdm_model"] == jm), None)
    if e: print(f"  {jm:18s} {e['best_buy']['rating']}  {e['best_buy']['reason']}")
