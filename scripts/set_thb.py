"""Set (or clear) the Thai Baht current-find price for a model.

Usage:
    python scripts/set_thb.py "AU-607" 6500
    python scripts/set_thb.py "AU-607" none      <- clears the price
    python scripts/set_thb.py "AU-607"           <- shows the current price

Matches jdm_model case-insensitively, ignoring spaces/hyphens (so "au607",
"AU 607" and "AU-607" all work). Updates last_price_check to today.
"""
import json
import re
import sys
import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sansui.json"

def norm(s):
    return re.sub(r"[\s\-_.]", "", str(s)).upper()

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

    if len(sys.argv) < 3:
        print(f"{e['jdm_model']}: avg_price_thb_3yr = {e.get('avg_price_thb_3yr')} "
              f"(last check {e.get('last_price_check')})")
        return

    raw = sys.argv[2].replace(",", "").replace("฿", "")
    old = e.get("avg_price_thb_3yr")
    if raw.lower() in ("none", "null", "clear", "-"):
        e["avg_price_thb_3yr"] = None
    else:
        e["avg_price_thb_3yr"] = int(float(raw))
    e["last_price_check"] = datetime.date.today().strftime("%Y-%m")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"{e['jdm_model']}: {old} -> {e['avg_price_thb_3yr']}  (last_price_check {e['last_price_check']})")
    print('Now publish with:  git add data/sansui.json && git commit -m "THB price update" && git push')

if __name__ == "__main__":
    main()
