"""Parse the Sansui Serial Number Report PDF into model -> {type, min_year, max_year, n}.
We ignore the serial numbers themselves; we only want production-date year ranges per model.
"""
import fitz, re, json, sys
from pathlib import Path

PDF = Path("Service manuals/02 Sansui Serial Number Report.pdf")

MONTH_RE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December),\s*(\d{4})$")

# Lines that are page furniture and should be skipped
SKIP = {
    "Sansui Serial Number Report", "Model", "Equipment Type", "Serial",
    "Production Date", "Invalid Date Code",
}
SKIP_RE = [
    re.compile(r"^Page \d+ of \d+$"),
    re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),"),
]

def is_skip(line):
    if line in SKIP:
        return True
    for r in SKIP_RE:
        if r.match(line):
            return True
    return False

def main():
    doc = fitz.open(PDF)
    lines = []
    for page in doc:
        for raw in page.get_text().split("\n"):
            s = raw.strip()
            if not s or is_skip(s):
                continue
            lines.append(s)

    # The report is a 4-column table: Model | Equipment Type | Serial | Production Date.
    # In extracted text each cell is its own line. For the first row of a model all four
    # cells appear; subsequent rows only show Serial + Production Date (merged cells blank).
    #
    # Discriminators:
    #   DATE   = matches MONTH_RE (skipped "Invalid Date Code" already removed)
    #   TYPE   = a pure-word line (letters/spaces/&/hyphen, NO digits) e.g. "Receiver",
    #            "Integrated Amplifier", "Power Amplifier"
    #   SERIAL = alphanumeric code containing digits (e.g. TL3808, 17103758)
    #   MODEL  = the line immediately preceding a TYPE line
    # Equipment types are auto-discovered rather than hardcoded, so amplifiers etc.
    # aren't missed.
    TYPE_RE = re.compile(r"^[A-Za-z][A-Za-z &/.\-]*$")

    def is_type(line):
        # pure word line, and not absurdly long (guards against stray prose)
        return bool(TYPE_RE.match(line)) and len(line) <= 30

    models = {}  # model -> {"type":..., "years": set()}
    current = None
    # We track years attached to the current model: any date line after a model block
    # belongs to the most recent model.
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = MONTH_RE.match(line)
        if m:
            if current is not None:
                models[current]["years"].add(int(m.group(2)))
            i += 1
            continue
        # Non-date line. If the NEXT line is a type word AND this line is not itself a
        # type word (i.e. it looks like a model code), treat this as model + type.
        if i + 1 < n and is_type(lines[i + 1]) and not is_type(line):
            model = line
            typ = lines[i + 1]
            if model not in models:
                models[model] = {"type": typ, "years": set()}
            current = model
            i += 2
            continue
        # Otherwise it's a serial (or stray) belonging to current model; skip.
        i += 1

    out = {}
    for model, d in models.items():
        ys = sorted(d["years"])
        out[model] = {
            "type": d["type"],
            "min_year": ys[0] if ys else None,
            "max_year": ys[-1] if ys else None,
            "n_dates": len(ys),
            "years_list": ys,
        }

    Path("scripts").mkdir(exist_ok=True)
    with open("scripts/serials_parsed.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(out)} models.")
    dated = {k: v for k, v in out.items() if v["min_year"]}
    print(f"With production years: {len(dated)}")
    print("\nSample (first 30 with years):")
    for k in list(dated)[:30]:
        v = dated[k]
        print(f"  {k:20s} {v['type']:22s} {v['min_year']}-{v['max_year']}  ({v['n_dates']} dates)")

if __name__ == "__main__":
    main()
