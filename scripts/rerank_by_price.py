"""Collector ranking by avg_price_usd_3mo, descending, in bands of ten
(Top 10, Top 10-20, Top 20-30, Top 30-40, Top 40-50; below 50 = Unranked).
Market twins (paired JDM/export records that reference each other) share one
rank slot. Models with no price can't be ranked by value and stay Unranked.

Two rankings are written:
  collector_ranking  -- within each brand (each brand gets its own top 50)
  global_ranking     -- across the whole archive (one top 50, all brands pooled)

The app shows the global band in the All-brands view and the per-brand band
when a single brand is selected. Supersedes rank_unranked.py's score buckets.
Run after price updates.

    py "<abs path>/scripts/rerank_by_price.py"           # dry-run
    py "<abs path>/scripts/rerank_by_price.py" --apply    # write
"""
import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
APPLY = "--apply" in sys.argv
BRANDS = ["sansui", "marantz", "pioneer"]
BANDS = ["Top 10", "Top 10-20", "Top 20-30", "Top 30-40", "Top 40-50"]

def band_for(i):
    return BANDS[i // 10] if i < 50 else "Unranked"

def build_units(db):
    """Group records into ranking units; a mutual JDM/export twin pair is one."""
    by = {e["jdm_model"]: e for e in db}
    seen, units = set(), []
    for e in db:
        jm = e["jdm_model"]
        if jm in seen:
            continue
        tw = by.get(e.get("int_model"))
        if tw and tw is not e and by.get(tw.get("int_model")) is e:
            units.append([e, tw]); seen.add(jm); seen.add(tw["jdm_model"])
        else:
            units.append([e]); seen.add(jm)
    return units

def unit_price(u):
    ps = [m.get("avg_price_usd_3mo") for m in u if m.get("avg_price_usd_3mo")]
    return max(ps) if ps else None

def rank_units(units, field):
    priced = [u for u in units if unit_price(u) is not None]
    priced.sort(key=lambda u: (-unit_price(u), u[0]["jdm_model"]))
    for i, u in enumerate(priced):
        r = band_for(i)
        for m in u:
            m[field] = r
    for u in units:
        if unit_price(u) is None:
            for m in u:
                m[field] = "Unranked"
    return priced

def label(u):
    return u[0]["jdm_model"] if len(u) == 1 else "+".join(m["jdm_model"] for m in u)

paths = {b: rf"C:/Users/Wayne/Documents/WoW Audio/data/{b}.json" for b in BRANDS}
dbs = {b: json.load(open(paths[b], encoding="utf-8-sig")) for b in BRANDS}

# Pass 1: per-brand.
all_units = []
for b in BRANDS:
    units = build_units(dbs[b])
    priced = rank_units(units, "collector_ranking")
    for u in units:
        u[0].setdefault("_brand", b)  # tag for the global report only
    all_units += units
    dist = Counter(m["collector_ranking"] for e in dbs[b] for m in [e])
    print(f"\n=== {b} (per-brand) ===  priced units {len(priced)}")
    print("  bands:", {x: dist.get(x, 0) for x in BANDS + ['Unranked']})
    print("  top 10:", [label(u) for u in priced[:10]])

# Pass 2: global across all brands (same unit objects, twins already grouped).
gp = rank_units(all_units, "global_ranking")
gdist = Counter(m["global_ranking"] for b in BRANDS for m in dbs[b])
print(f"\n=== GLOBAL (all brands) ===  priced units {len(gp)}")
print("  bands:", {x: gdist.get(x, 0) for x in BANDS + ['Unranked']})
print("  global top 12:", [(label(u), u[0].get('_brand'), unit_price(u)) for u in gp[:12]])

for b in BRANDS:
    for e in dbs[b]:
        e.pop("_brand", None)

if APPLY:
    for b in BRANDS:
        with open(paths[b], "w", encoding="utf-8") as f:
            json.dump(dbs[b], f, ensure_ascii=False, indent=2)
        json.load(open(paths[b], encoding="utf-8-sig"))  # validate
    print("\nWRITTEN + validated.")
else:
    print("\n(dry-run -- rerun with --apply to write)")
