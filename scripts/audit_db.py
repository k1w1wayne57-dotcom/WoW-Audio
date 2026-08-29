"""
WoW Audio — data integrity audit. READ ONLY: reports, never writes.

Finds the classes of error that keep turning up by hand — a stereo receiver
typed as 4-channel, a tuner typed as an amplifier, an Alpha-series record dated
before the Alpha series existed, an int_model that points at nothing.

    python scripts/audit_db.py                # all brands
    python scripts/audit_db.py --brand sansui
    python scripts/audit_db.py --severity high

Exit code is 1 when any HIGH finding is present, so it can gate a commit.
"""
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backfill_specs as B

EMPTY = (None, "", "—", [], {})

# Model prefix -> the types that make sense for it. Sansui/Marantz/Pioneer are
# consistent enough that a mismatch is nearly always a data error.
PREFIX_TYPES = {
    "QR": {"Receiver 4-ch", "Quad Decoder", "Quad Synth"},
    "QRX": {"Receiver 4-ch"},
    "QS": {"Quad Decoder", "Quad Synth", "Receiver 4-ch"},
    "TU": {"Tuner"},
    "CA": {"Preamp"},
    "BA": {"Power Amp", "Power Amp 4-ch"},
    "SC": {"Tape Deck"},
}
AMP_TYPES = {"Integrated", "Power Amp", "Power Amp 4-ch", "Receiver",
             "Receiver 4-ch", "Tube Integrated", "Tube Receiver"}

# series -> plausible year window (None = open ended)
SERIES_YEARS = {
    "Tube Era": (1950, 1972),
    "Alpha Series": (1986, 2001),
    "Early Transistor": (1960, 1976),
}


def prefix_of(model):
    m = re.match(r"^([A-Za-z]+)", str(model or ""))
    return m.group(1).upper() if m else ""


def audit(brand):
    data, _ = B.load_db(brand)
    out = []                      # (severity, model, check, detail)
    seen = defaultdict(list)
    by_model = {B.norm_model(r.get("jdm_model")): r for r in data}

    for r in data:
        m = r.get("jdm_model") or r.get("model") or "(unnamed)"
        t = r.get("type")
        y = r.get("year_start")
        seen[B.norm_model(m)].append(r.get("id"))

        # --- type vs model prefix ---
        pref = prefix_of(m)
        if pref in PREFIX_TYPES and t and t not in PREFIX_TYPES[pref]:
            out.append(("HIGH", m, "type/prefix",
                        f"{pref}- prefix but type={t!r}; expected {sorted(PREFIX_TYPES[pref])}"))
        # a "DB" suffix is Dolby, not 4-channel
        if str(m).upper().endswith("DB") and t == "Receiver 4-ch":
            out.append(("HIGH", m, "dolby-vs-quad",
                        "'DB' suffix means Dolby FM, not 4-channel — type should be Receiver"))

        # --- year sanity ---
        ye = r.get("year_end")
        if isinstance(y, int) and isinstance(ye, int) and ye < y:
            out.append(("HIGH", m, "year-order", f"year_end {ye} < year_start {y}"))
        if isinstance(y, int) and not (1950 <= y <= 2010):
            out.append(("HIGH", m, "year-range", f"year_start {y} out of range"))

        # --- series vs year ---
        s = r.get("series")
        # Tube reissues (AU-111 Vintage 1999, AU-111G Vintage 2001) are genuinely
        # Tube Era by technology despite the late date — not an error.
        reissue = s == "Tube Era" and re.search(r"vintage|reissue|reproduction", str(m), re.I)
        if s in SERIES_YEARS and isinstance(y, int) and not reissue:
            lo, hi = SERIES_YEARS[s]
            if not (lo <= y <= hi):
                out.append(("MED", m, "series/year",
                            f"series={s!r} but year_start={y} (expected {lo}-{hi})"))

        # --- implausible specs ---
        w = r.get("watts_per_channel")
        if w not in EMPTY and t in AMP_TYPES and not (1 <= w <= 2000):
            out.append(("HIGH", m, "watts", f"watts_per_channel={w}"))
        if w not in EMPTY and t in {"Tuner", "Preamp", "Tape Deck"}:
            out.append(("MED", m, "watts-on-nonamp", f"type={t} but watts={w}"))
        kg = r.get("weight_kg")
        if kg not in EMPTY and not (0.5 <= kg <= 120):
            out.append(("HIGH", m, "weight", f"weight_kg={kg}"))
        th = r.get("thd_percent")
        if th not in EMPTY and not (0.0001 <= th <= 10):
            out.append(("MED", m, "thd", f"thd_percent={th}"))
        fr = r.get("freq_response_hz")
        if fr not in EMPTY and not re.match(r"^(DC|\d+)-\d+$", str(fr)):
            out.append(("MED", m, "freq-format", f"freq_response_hz={fr!r}"))

        # --- price coherence ---
        p = r.get("avg_price_usd_3mo")
        if p not in EMPTY and not (10 <= p <= 60000):
            out.append(("HIGH", m, "price-range", f"avg_price_usd_3mo={p}"))
        if p in EMPTY and r.get("price_confidence") not in (None, "", "None"):
            out.append(("LOW", m, "price-confidence",
                        f"confidence={r.get('price_confidence')!r} but no price"))

        # --- missing essentials ---
        if t in AMP_TYPES and w in EMPTY:
            out.append(("LOW", m, "missing-watts", "amplifier with no watts_per_channel"))
        if y in EMPTY:
            out.append(("LOW", m, "missing-year", "no year_start"))

    # --- cross-record checks ---
    for key, ids in seen.items():
        if len(ids) > 1:
            out.append(("HIGH", key, "duplicate", f"{len(ids)} records share this model: {ids}"))
    for r in data:
        im = r.get("int_model")
        if im in EMPTY:
            continue
        m = r.get("jdm_model")
        other = by_model.get(B.norm_model(im))
        if other is None:
            out.append(("LOW", m, "int-model-orphan",
                        f"int_model={im!r} has no record of its own"))
        elif other.get("int_model") and B.norm_model(other["int_model"]) != B.norm_model(m):
            out.append(("MED", m, "int-model-mismatch",
                        f"{m} -> {im}, but {im} -> {other.get('int_model')}"))
    return out


def main():
    ap = argparse.ArgumentParser(description="Audit the brand databases for bad data.")
    ap.add_argument("--brand", choices=["sansui", "marantz", "pioneer"])
    ap.add_argument("--severity", choices=["high", "med", "low"], default="low")
    args = ap.parse_args()
    brands = [args.brand] if args.brand else ["sansui", "marantz", "pioneer"]
    floor = {"high": ["HIGH"], "med": ["HIGH", "MED"], "low": ["HIGH", "MED", "LOW"]}[args.severity]

    grand = 0
    highs = 0
    for brand in brands:
        found = [f for f in audit(brand) if f[0] in floor]
        by_check = defaultdict(list)
        for sev, m, check, detail in found:
            by_check[(sev, check)].append((m, detail))
        print(f"\n=== {brand}: {len(found)} findings ===")
        for (sev, check) in sorted(by_check, key=lambda k: (["HIGH", "MED", "LOW"].index(k[0]), k[1])):
            rows = by_check[(sev, check)]
            print(f"  [{sev:4}] {check} ({len(rows)})")
            for m, detail in rows[:6]:
                print(f"          {str(m):22} {detail[:88]}")
            if len(rows) > 6:
                print(f"          ... and {len(rows)-6} more")
        grand += len(found)
        highs += sum(1 for f in found if f[0] == "HIGH")
    print(f"\nTOTAL: {grand} findings ({highs} HIGH)")
    return 1 if highs else 0


if __name__ == "__main__":
    sys.exit(main())
