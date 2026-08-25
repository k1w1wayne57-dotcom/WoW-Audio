"""
Fix Sansui JDM<->International model mappings from the authoritative Audiokarma
"Sansui Product History: Amplifiers 1967-2000" list (JimEGR, peer-reviewed).

Only applies pairings the source explicitly states ("JDM version of X" /
"int version of JDM Y"). Sets int_model on BOTH sides and stamps `market`
(JDM / International). Anything not in the source is left as no-match.

    python scripts/fix_intl.py            # dry run
    python scripts/fix_intl.py --apply
"""
import sys
import argparse
sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
import backfill_specs as B

# JDM model -> International equivalent, verbatim from the source list.
PAIRS = {
    "AU-2000": "AU-505",
    "AU-777D": "AU-777A",
    "AU-207": "AU-217",
    "AU-307": "AU-317",
    "AU-507": "AU-417",
    "AU-607": "AU-517",
    "AU-707": "AU-717",
    "AU-D607": "AU-519",
    "AU-D707": "AU-819",
    "AU-D907": "AU-919",
    "AU-107ii": "AU-117ii",
    "AU-207ii": "AU-217ii",
    "AU-307ii": "AU-317ii",
    "AU-D55F": "AU-D33",
    "AU-a607i": "AU-X701",
    "AU-a707i": "AU-X901",
}
# Not confirmed by the source -> clear (per "assume no matches for what we don't").
CLEAR = {"sansui-au-d607f-1980": "AU-D7 (list shows AU-D7 as a separate 1982 model)"}


def norm(s):
    return B.norm_model(s)


def run(apply):
    d, meta = B.load_db("sansui")
    by_model = {}
    for r in d:
        by_model.setdefault(norm(r.get("jdm_model")), r)
    changes, missing = [], []

    def setf(rec, field, val):
        if rec.get(field) != val:
            changes.append(f"  {rec.get('jdm_model'):16} {field}: {rec.get(field)} -> {val}")
            if apply:
                rec[field] = val

    for jdm, intl in PAIRS.items():
        jrec = by_model.get(norm(jdm))
        irec = by_model.get(norm(intl))
        if jrec:
            setf(jrec, "int_model", intl)
            setf(jrec, "market", "JDM")
        else:
            missing.append(f"  JDM record not in DB: {jdm}")
        if irec:
            setf(irec, "int_model", jdm)
            setf(irec, "market", "International")
        else:
            missing.append(f"  International record not in DB: {intl}")

    for rid, why in CLEAR.items():
        rec = next((r for r in d if r.get("id") == rid), None)
        if rec and rec.get("int_model"):
            changes.append(f"  {rec.get('jdm_model'):16} int_model: {rec.get('int_model')} -> None  [{why}]")
            if apply:
                rec["int_model"] = None

    if apply:
        B.save_db(d, meta)
    print("=== CHANGES ===")
    print("\n".join(changes) if changes else "  (none)")
    print("\n=== NOT FOUND IN DB (left as no-match) ===")
    print("\n".join(missing) if missing else "  (all found)")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'} — {len(changes)} field changes")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(ap.parse_args().apply)
