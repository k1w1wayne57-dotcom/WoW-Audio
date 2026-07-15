"""Assign collector_ranking to the unranked models.
Ranking = collector DESIRABILITY (build tier, power, price positioning, type, era) -
deliberately different from best_buy, which measures value-for-money.
Only touches entries currently Unranked/null; never overwrites an existing rank.
Models with too little data to judge stay Unranked rather than being guessed at.
"""
import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))

ACCESSORY = ("Tuner", "Tape Deck", "Quad Synth", "Quad Decoder", "Reverb Unit")

def score(e):
    w = e.get("watts_per_channel") or 0
    wt = e.get("weight_kg") or 0
    thd = e.get("thd_percent")
    jp = e.get("japan_price_kyen") or 0
    usd = e.get("usd_msrp") or 0
    typ = e.get("type") or ""
    yr = e.get("year_start") or 0
    if not wt and not w and not jp and not usd:
        return None  # nothing to judge on

    s = 0.0
    # build tier
    if wt >= 25: s += 3
    elif wt >= 18: s += 2.5
    elif wt >= 13: s += 2
    elif wt >= 9: s += 1
    # power
    if w >= 150: s += 3
    elif w >= 100: s += 2.5
    elif w >= 70: s += 2
    elif w >= 40: s += 1.5
    elif w >= 20: s += 0.5
    # price positioning (premium => desirable)
    if jp >= 150 or usd >= 600: s += 2
    elif jp >= 80 or usd >= 350: s += 1.5
    elif jp >= 45 or usd >= 200: s += 1
    # engineering
    if thd is not None and thd <= 0.01: s += 0.5
    # type
    if typ in ("Integrated", "Receiver", "Tube Integrated", "Tube Receiver"): s += 1
    elif typ in ("Power Amp", "Preamp"): s += 0.5
    elif typ in ACCESSORY: s -= 1
    # golden era
    if 1974 <= yr <= 1982: s += 0.5
    return s

def bucket(s):
    if s >= 8: return "Top 10"
    if s >= 6.5: return "Top 10-20"
    if s >= 5: return "Top 20-30"
    if s >= 3.5: return "Top 30-40"
    if s >= 2: return "Top 40-50"
    return "Unranked"

changed, skipped = [], 0
for e in db:
    if e.get("collector_ranking") not in (None, "Unranked"):
        continue
    s = score(e)
    if s is None:
        skipped += 1
        e["collector_ranking"] = "Unranked"
        continue
    r = bucket(s)
    e["collector_ranking"] = r
    if r != "Unranked":
        changed.append((e["jdm_model"], r, round(s, 1)))
    else:
        skipped += 1

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

from collections import Counter
print(f"Ranked {len(changed)}; left Unranked (too little data / not collectible): {skipped}")
print("New ranks given:", dict(Counter(r for _, r, _ in changed)))
print("\nTop of the newly-ranked:")
for jm, r, s in sorted(changed, key=lambda x: -x[2])[:12]:
    print(f"   {jm:22s} {r:10s} (score {s})")
print("\nFinal overall distribution:",
      dict(Counter(e.get("collector_ranking") for e in db)))
