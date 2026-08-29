"""
Parse scripts/sansui_history_raw.txt -> data/sansui_history.json

A structured, ordered reference of Sansui's amplifier history (generations +
topology headings + models) for the app's "History" timeline view. This is a
RESOURCE only — it does not add records to the main brand tables.
"""
import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(__file__).resolve().parent / "sansui_history_raw.txt"
OUT = ROOT / "data" / "sansui_history.json"

SOURCE = {
    "title": "Sansui Product History: Amplifiers 1967-2000 (JimEGR, Audiokarma)",
    "url": "https://audiokarma.org/forums/threads/sansui-product-history-amplifiers-1967-2000.1008935/",
    "note": "Community-maintained, peer-reviewed. Not a complete list. A historical "
            "reference — many models were never sold outside Japan.",
}


def infer_type(model, category, topology):
    """Give every AK-list model a type so it can merge with the DB records.

    The list is amplifiers only, split into INTEGRATED and SEPARATES; within
    SEPARATES the topology heading says pre or power. Model prefixes settle the
    rest (Sansui is consistent: CA-/C- pre, BA-/B- power, TU- tuner)."""
    m = (model or "").upper()
    topo = (topology or "").lower()
    if m.startswith(("CA-", "C-", "TC-")):
        return "Preamp"
    if m.startswith(("BA-", "B-")):
        return "Power Amp"
    if m.startswith("TU-"):
        return "Tuner"
    if "separates" in (category or "").lower():
        if "pre" in topo:
            return "Preamp"
        if "power" in topo:
            return "Power Amp"
    return "Integrated"


def parse_model(line):
    m = re.match(r"^(\d{4})\s+(.*)$", line)
    if not m:
        return None
    year = int(m.group(1))
    rest = m.group(2).strip()

    # split off trailing "(...)" note groups
    note_bits = re.findall(r"\(([^)]*)\)", rest)
    rest_no_parens = re.sub(r"\([^)]*\)", "", rest).strip()

    watts = None
    wm = re.search(r"(\d+)\s*watts?", rest_no_parens, re.I)
    if wm:
        watts = int(wm.group(1))
        model = rest_no_parens[:wm.start()].strip()
    else:
        model = rest_no_parens.strip()
    model = re.sub(r"\s{2,}", " ", model).strip(" -+")

    note = "; ".join(b.strip() for b in note_bits) if note_bits else None
    market, pair = None, None
    joined = " ".join(note_bits)
    pm = re.search(r"JDM version of\s+([A-Za-z0-9\-]+)", joined, re.I)
    im = re.search(r"int(?:ernational)? version of JDM\s+([A-Za-z0-9\-]+)", joined, re.I)
    if pm:
        market, pair = "JDM", pm.group(1)
    elif im:
        market, pair = "International", im.group(1)
    elif re.search(r"\bJDM\b", joined):
        market = "JDM"
    return {"year": year, "model": model, "watts": watts,
            "market": market, "pair": pair, "note": note}


GEN_SRC = Path(__file__).resolve().parent / "sansui_generations.txt"

# Share one normaliser with the backfill tools so 'AU-AL607', 'AU-α607' and
# 'AU-Alpha-607' all resolve to the same key.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from backfill_specs import norm_model  # noqa: E402

# Short labels for the chips — the full wording is kept for the tooltip.
# G-series patterns MUST come first: "G-Series Third Generation" also contains
# "third generation", which would otherwise mislabel receivers as 07-series.
GEN_SHORT = [
    (r"g-series first", "G 1st Gen"), (r"g-series monster", "G Monster"),
    (r"g-series second", "G 2nd Gen"), (r"g-series third", "G 3rd Gen (DC)"),
    (r"first generation", "1st Gen 07"), (r"second generation", "2nd Gen 07"),
    (r"third generation", "3rd Gen 07"), (r"fourth generation", "4th Gen 07"),
    (r"fifth generation", "5th Gen 07"), (r"sixth generation", "6th Gen 07"),
    (r"seventh generation", "7th Gen 07"), (r"eighth generation", "8th Gen 07"),
    (r"ninth generation", "9th Gen 07"), (r"tenth generation", "10th Gen 07"),
    (r"eleventh generation", "11th Gen 07"), (r"twelfth generation", "12th Gen 07"),
    (r"thirteenth generation", "13th Gen 07"), (r"fourteenth generation", "14th Gen 07"),
    (r"fifteenth generation", "15th Gen 07"),
    (r"x 1 series", "X-1 Series"), (r"limited edition-tube", "Ltd Ed · Tube"),
    (r"limited edition", "Limited Edition"), (r"one number three digit", "3-Digit"),
    (r"power amplifier", "Power Amp"), (r"pre amplifier", "Pre Amp"),
    (r"tube amplifier", "Tube Amp"),
]


def short_gen(label):
    low = (label or "").lower()
    for pat, short in GEN_SHORT:
        if re.search(pat, low):
            return short
    return None


def parse_generations():
    """Wayne's generation table -> {norm_model: {...}} plus JDM<->intl pairs."""
    out, pairs = {}, []
    if not GEN_SRC.exists():
        return out, pairs
    for raw in GEN_SRC.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        gen = parts[0] if parts else ""
        intl = parts[1] if len(parts) > 1 else ""
        jdm = parts[2] if len(parts) > 2 else ""
        # skip aggregate/no-model rows like "AU-517,AU-717"
        if "," in intl:
            intl = ""
        short = short_gen(gen)
        for name in (intl, jdm):
            if not name or name.lower().startswith("sansui au-@"):
                continue
            out[norm_model(name)] = {"generation": gen or None, "gen_short": short,
                                     "model": name}
        if intl and jdm and intl.lower() != jdm.lower() and "," not in intl:
            pairs.append({"jdm": jdm, "intl": intl, "generation": gen or None})
    return out, pairs


def main():
    category = None
    generation = None
    topology = None
    sections = []      # list of {category, generation, groups:[{topology, models:[]}]}
    cur_section = None
    cur_group = None

    def new_section():
        nonlocal cur_section, cur_group
        cur_section = {"category": category, "generation": generation, "groups": []}
        sections.append(cur_section)
        cur_group = None

    def ensure_group(topo):
        nonlocal cur_group
        if cur_section is None:
            new_section()
        if cur_group is None or cur_group["topology"] != topo:
            cur_group = {"topology": topo, "models": []}
            cur_section["groups"].append(cur_group)

    for raw in RAW.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        sec = re.match(r"^---\s*(.*?)\s*---$", line)
        if sec:
            name = sec.group(1)
            if name.upper().startswith("INTEGRATED") or name.upper().startswith("SEPARATES"):
                category = name
                generation = None
            else:
                generation = name
            topology = None
            new_section()
            continue
        if line.startswith('"') and line.endswith('"'):
            topology = line.strip('"')
            ensure_group(topology)
            continue
        rec = parse_model(line)
        if rec:
            ensure_group(topology)
            rec["type"] = infer_type(rec["model"], category, topology)
            rec["topology"] = topology        # carried through for the tooltip
            cur_group["models"].append(rec)

    # drop empty sections
    sections = [s for s in sections if any(g["models"] for g in s["groups"])]
    total = sum(len(g["models"]) for s in sections for g in s["groups"])
    gens, pairs = parse_generations()
    print(f"  generations: {len(gens)} models labelled, {len(pairs)} JDM<->intl pairs")
    OUT.write_text(json.dumps({"source": SOURCE, "sections": sections,
                               "generations": gens, "gen_pairs": pairs},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(sections)} sections, {total} models")


if __name__ == "__main__":
    main()
