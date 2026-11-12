"""Apply USE/MIXED rows from sonic_review.tsv to the brand data files.

Dry-run by default; pass --apply to write. Replaces family-level
sonic_signature/sonic_source with model-specific owner/reviewer text.
"""
import csv, json, sys, os

ROOT = r"C:\Users\Wayne\Documents\WoW Audio"
APPLY = "--apply" in sys.argv

rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "scripts", "sonic_review.tsv"), encoding="utf-8"), delimiter="\t")
        if r["verdict"] in ("USE", "MIXED")]

by_brand = {}
for r in rows:
    by_brand.setdefault(r["brand"].lower(), []).append(r)

total = 0
for brand, items in by_brand.items():
    path = os.path.join(ROOT, "data", brand + ".json")
    data = json.load(open(path, encoding="utf-8-sig"))
    for r in items:
        hits = [d for d in data if r["model"] in (d.get("jdm_model"), d.get("int_model"))
                and d.get("thb_status") == "For sale"]
        if len(hits) != 1:
            print(f"!! {brand} {r['model']}: {len(hits)} matches - skipped")
            continue
        d = hits[0]
        src = r["source"]
        if r["verdict"] == "MIXED":
            src += " (owners disagree - both views given)"
        print(f"{brand} {r['model']}: [{(d.get('sonic_source') or '')[:40]}] -> {r['verdict']}")
        d["sonic_signature"] = r["proposed_sonic_signature"]
        d["sonic_source"] = "Model-specific, owner/reviewer impressions: " + src
        total += 1
    if APPLY:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        json.load(open(path, encoding="utf-8-sig"))  # validate
print(("APPLIED " if APPLY else "DRY RUN ") + str(total) + " records")
