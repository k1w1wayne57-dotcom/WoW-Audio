"""Manage Thai Baht listing prices for a model. Each price = one listing; never averaged.

Usage:
    python scripts/set_thb.py "AU-607"               <- show current listings
    python scripts/set_thb.py "AU-607" add 6500      <- add a listing
    python scripts/set_thb.py "AU-607" set 6500 9900 <- replace all listings with these
    python scripts/set_thb.py "AU-607" clear         <- remove all listings

Matches jdm_model case-insensitively, ignoring spaces/hyphens. Updates
last_price_check to today on any change.
"""
import json
import re
import sys
import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # allow the ฿ symbol on Windows consoles
except Exception:
    pass

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sansui.json"

def norm(s):
    return re.sub(r"[\s\-_.]", "", str(s)).upper()

def to_int(raw):
    return int(float(raw.replace(",", "").replace("฿", "")))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    model = sys.argv[1]
    db = json.load(open(DB_PATH, encoding="utf-8-sig"))
    hits = [e for e in db if norm(e["jdm_model"]) == norm(model)]
    if not hits:
        partial = [e["jdm_model"] for e in db if norm(model) in norm(e["jdm_model"])]
        print(f"No exact match for '{model}'.")
        if partial:
            print("Did you mean:", ", ".join(partial[:10]))
        return
    e = hits[0]
    listings = e.setdefault("price_thb_listings", [])

    if len(sys.argv) < 3:
        shown = " / ".join(f"฿{v:,}" for v in listings) if listings else "(none)"
        print(f"{e['jdm_model']}: {shown}  (last check {e.get('last_price_check')})")
        return

    cmd = sys.argv[2].lower()
    old = list(listings)
    if cmd == "add":
        listings.extend(to_int(a) for a in sys.argv[3:])
    elif cmd == "set":
        e["price_thb_listings"] = [to_int(a) for a in sys.argv[3:]]
    elif cmd in ("clear", "none", "null"):
        e["price_thb_listings"] = []
    else:
        # bare number(s) = add
        try:
            listings.extend(to_int(a) for a in sys.argv[2:])
        except ValueError:
            print(f"Unknown command '{cmd}'. Use add / set / clear.")
            return
    e["last_price_check"] = datetime.date.today().strftime("%Y-%m")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"{e['jdm_model']}: {old} -> {e['price_thb_listings']}")
    print('Publish with:  git add data/sansui.json && git commit -m "THB listing update" && git push')

if __name__ == "__main__":
    main()
