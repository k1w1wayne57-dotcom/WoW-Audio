"""Apply researched spec and price values to blank fields only.

    py scripts/fill.py fills.json           <- dry-run diff
    py scripts/fill.py fills.json --apply

fills.json is a list; each item names one record and what was found:

    [{"brand": "pioneer", "model": "SX-800", "source": "hifi-wiki",
      "fields": {"freq_response_hz": "20-20000", "thd_percent": 1.0}},
     {"brand": "pioneer", "model": "SX-800",
      "price": {"usd": 450, "confidence": "Medium",
                "basis": "eBay asking $250-805 (serviced), typ ~$450 - listings, not confirmed sales"}}]

- A field that already holds a value is kept and reported, never overwritten.
- Filled spec fields are stamped in auto_specs {source, date, fields}; an
  existing stamp is kept, and auto_specs becomes a list of stamps.
- A price fills only when avg_price_usd_3mo is blank, and then sets
  price_confidence and price_basis with it.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DATA = Path(__file__).resolve().parent.parent / "data"
EMPTY = (None, "", [], 0)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("α", "alpha"))


def find(db, model):
    exact = [e for e in db if e["jdm_model"] == model]
    if exact:
        return exact[0]
    loose = [e for e in db if norm(e["jdm_model"]) == norm(model)]
    return loose[0] if len(loose) == 1 else None


def stamp(e, source, date, fields):
    new = {"source": source, "date": date, "fields": fields}
    old = e.get("auto_specs")
    if not old:
        e["auto_specs"] = new
    else:
        e["auto_specs"] = (old if isinstance(old, list) else [old]) + [new]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fills")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    date = datetime.date.today().strftime("%Y-%m")
    items = json.loads(Path(a.fills).read_text(encoding="utf-8-sig"))
    dbs, touched, n_filled, n_kept, problems = {}, set(), 0, 0, []

    for it in items:
        brand, model = it["brand"], it["model"]
        if brand not in dbs:
            dbs[brand] = json.load(open(DATA / f"{brand}.json", encoding="utf-8-sig"))
        e = find(dbs[brand], model)
        if not e:
            problems.append(f"{brand}/{model}: no such record")
            continue
        tag = f"{brand[:3]} {e['jdm_model']:18s}"

        if it.get("fields"):
            if not it.get("source"):
                problems.append(f"{brand}/{model}: fields given without a source")
                continue
            filled = []
            for k, v in it["fields"].items():
                if k not in e:
                    problems.append(f"{brand}/{model}: unknown field '{k}'")
                elif e[k] in EMPTY:
                    print(f"  {tag} {k:20s} {e[k]!r} -> {v!r}")
                    filled.append(k)
                    if a.apply:
                        e[k] = v
                else:
                    print(f"  {tag} {k:20s} kept {e[k]!r} (offered {v!r})")
                    n_kept += 1
            if filled:
                n_filled += len(filled)
                touched.add(brand)
                if a.apply:
                    stamp(e, it["source"], date, filled)

        p = it.get("price")
        if p:
            if not p.get("basis"):
                problems.append(f"{brand}/{model}: price without a basis")
            elif e.get("avg_price_usd_3mo") in EMPTY:
                print(f"  {tag} {'price':20s} None -> ${p['usd']} ({p['confidence']}) {p['basis']}")
                n_filled += 1
                touched.add(brand)
                if a.apply:
                    e["avg_price_usd_3mo"] = p["usd"]
                    e["price_confidence"] = p["confidence"]
                    e["price_basis"] = p["basis"]
            else:
                print(f"  {tag} {'price':20s} kept ${e['avg_price_usd_3mo']} (offered ${p['usd']})")
                n_kept += 1

    for msg in problems:
        print(f"  !! {msg}")
    print(f"\n{n_filled} to fill, {n_kept} kept (already set), {len(problems)} problems.")

    if not a.apply:
        print("DRY-RUN — nothing written.")
        return
    for brand in touched:
        path = DATA / f"{brand}.json"
        n = len(dbs[brand])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dbs[brand], f, indent=2, ensure_ascii=False)
        check = json.load(open(path, encoding="utf-8-sig"))
        assert len(check) == n, f"{brand}: record count changed {n} -> {len(check)}"
        print(f"APPLIED {brand}: {n} records, file valid.")


if __name__ == "__main__":
    main()
