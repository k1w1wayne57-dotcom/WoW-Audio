"""
WoW Audio — drop non-component entries (modular music-centres / all-in-one
systems) that get scraped off for-sale lists and do not belong in a components
database. The signal is a blank `type`: every real separate, tube and quad gear
included, carries one. Golden-era separates and tube pieces are always kept.

    python scripts/drop_noncomponents.py            # dry-run: list what would go
    python scripts/drop_noncomponents.py --apply     # remove them and rewrite

Read-only until --apply. Prints before/after counts so the write is verifiable.
"""
import json
import sys
import argparse
from pathlib import Path

BRANDS = ["sansui", "marantz", "pioneer"]
EMPTY = (None, "", "—")


def load(brand):
    return Path(f"data/{brand}.json"), json.load(
        open(f"data/{brand}.json", encoding="utf-8-sig"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the change")
    args = ap.parse_args()

    total_dropped = 0
    for brand in BRANDS:
        path, db = load(brand)
        drop = [e for e in db if e.get("type") in EMPTY]
        keep = [e for e in db if e.get("type") not in EMPTY]
        if not drop:
            print(f"{brand}: nothing to drop ({len(db)} entries)")
            continue
        print(f"\n{brand}: {len(drop)} non-component entr{'y' if len(drop)==1 else 'ies'} "
              f"-> {len(db)} would become {len(keep)}")
        for e in drop:
            print(f"    DROP {e.get('jdm_model'):16s} type={e.get('type')!r} "
                  f"thb={e.get('price_thb_listings')} {e.get('thb_status')}")
        total_dropped += len(drop)
        if args.apply:
            json.dump(keep, open(path, "w", encoding="utf-8"),
                      indent=2, ensure_ascii=False)
            json.load(open(path, encoding="utf-8-sig"))  # validate
            print(f"    written: {len(keep)} entries (valid)")

    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: "
          f"{total_dropped} entr{'y' if total_dropped==1 else 'ies'} "
          f"{'dropped' if args.apply else 'would be dropped'}")


if __name__ == "__main__":
    main()
