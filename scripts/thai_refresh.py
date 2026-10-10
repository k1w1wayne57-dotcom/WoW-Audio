"""Apply one of Wayne's Thai for-sale lists to a brand's data file.

    py scripts/thai_refresh.py --brand pioneer --list list.txt           <- dry-run
    py scripts/thai_refresh.py --brand pioneer --list list.txt --apply

The list is pasted text, one listing per line: "<model><tab or space><price>".
Each price is one listing (never averaged); repeats of a model collect.

- Matched by jdm_model (then int_model), ignoring case, punctuation, "Model"
  and "Woodcase"; α folds to "alpha". ALIAS holds Wayne-confirmed shorthands.
- Matched -> price_thb_listings = list prices, thb_status "For sale".
- Was "For sale" but absent from the list -> thb_status "Sold" (prices kept).
- Not in DB -> reported only. Adding a model is a separate, researched step.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DATA = Path(__file__).resolve().parent.parent / "data"

# list shorthand/typo -> exact jdm_model (Wayne-confirmed intent)
ALIAS = {
    "sansui": {
        "b2102mos": "B-2102 MOS Vintage",  # the MOS record, NOT the X-Balanced B-2102
        "au55f": "AU-D55F",
        "107ii": "AU-117II",  # AU-107II is the export twin; listed on the AU-117II record
        "au107ii": "AU-117II",
    },
    "marantz": {"pm5": "PM-5 Esotec", "pm710": "PM-710 DC"},
    "pioneer": {},
}


def norm(s):
    t = str(s).strip().lower().replace("α", "alpha")
    t = re.sub(r"\b(model|woodcase)\b", "", t)
    return re.sub(r"[^a-z0-9]", "", t)


def parse(text):
    listings = {}
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        name, price = line.rsplit("\t", 1) if "\t" in line else line.rsplit(None, 1)
        price = int(float(price.strip().replace(",", "").replace("฿", "")))
        k = norm(name)
        listings.setdefault(k, {"label": name.strip(), "prices": []})
        listings[k]["prices"].append(price)
    return listings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True, choices=sorted(ALIAS))
    ap.add_argument("--list", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    path = DATA / f"{a.brand}.json"
    db = json.load(open(path, encoding="utf-8-sig"))
    date = datetime.date.today().strftime("%Y-%m")
    listings = parse(Path(a.list).read_text(encoding="utf-8-sig"))

    by_jdm, by_int = {}, {}
    for e in db:
        by_jdm.setdefault(norm(e.get("jdm_model")), e)
        if e.get("int_model"):
            by_int.setdefault(norm(e["int_model"]), e)
    for k, target in ALIAS[a.brand].items():
        if norm(target) in by_jdm:
            by_jdm[k] = by_jdm[norm(target)]

    matched, via_int, unmatched, listed = [], [], [], set()
    for k, info in listings.items():
        e = by_jdm.get(k)
        bucket = matched
        if not e:
            e, bucket = by_int.get(k), via_int
        if not e:
            unmatched.append(info)
            continue
        listed.add(id(e))
        bucket.append((e, info))

    sold = [e for e in db if e.get("thb_status") == "For sale" and id(e) not in listed]

    print(f"=== {a.brand.upper()} — MATCHED ({len(matched)}) ===")
    for e, info in sorted(matched, key=lambda x: x[0]["jdm_model"]):
        print(f"  {e['jdm_model']:20s} {e.get('price_thb_listings')} ({e.get('thb_status')}) -> {info['prices']}")
    if via_int:
        print(f"\n=== MATCHED via int_model ({len(via_int)}) — check these ===")
        for e, info in via_int:
            print(f"  '{info['label']}' -> {e['jdm_model']} (int={e.get('int_model')}) {info['prices']}")
    print(f"\n=== NOT IN DB ({len(unmatched)}) — alias, typo, or new model? ===")
    for info in unmatched:
        print(f"  '{info['label']}' {info['prices']}")
    print(f"\n=== FLIP TO SOLD ({len(sold)}) ===")
    for e in sorted(sold, key=lambda x: x["jdm_model"]):
        print(f"  {e['jdm_model']:20s} was {e.get('price_thb_listings')}")

    if not a.apply:
        print("\nDRY-RUN — nothing written.")
        return
    for e, info in matched + via_int:
        e["price_thb_listings"] = info["prices"]
        e["thb_status"] = "For sale"
        e["last_price_check"] = date
    for e in sold:
        e["thb_status"] = "Sold"
        e["last_price_check"] = date
    n = len(db)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    check = json.load(open(path, encoding="utf-8-sig"))
    assert len(check) == n, f"record count changed: {n} -> {len(check)}"
    print(f"\nAPPLIED. {len(matched) + len(via_int)} updated, {len(sold)} -> Sold. "
          f"{len(check)} records, file valid.")


if __name__ == "__main__":
    main()
