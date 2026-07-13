import json
from pathlib import Path
DB_PATH = Path("data/sansui.json")
db = json.load(open(DB_PATH, encoding="utf-8-sig"))
by = {e["jdm_model"]: e for e in db}

# 1) watts corrections (Wayne's authoritative list)
for jm, w in {"G-5000": 45, "G-7000": 85, "G-8700DB": 160}.items():
    old = by[jm].get("watts_per_channel")
    by[jm]["watts_per_channel"] = w
    print(f"  {jm}: watts {old} -> {w}")

# 2) export (Euro) model names -> int_model
INT = {"G-3000": "G-301", "G-5000": "G-501", "G-6000": "G-601", "G-7000": "G-701",
       "G-8000": "G-801", "G-9000": "G-901", "G-8700DB": "G-871DB"}
for jm, ex in INT.items():
    by[jm]["int_model"] = ex

# 3) generation tags -> special_features
GEN = {
    "1st generation (1977-79, silver-face)": ["G-2000","G-3000","G-5000","G-6000","G-7000","G-8000","G-9000","G-9000DB"],
    "'Monster' two-piece Super-Power unit (1978-81)": ["G-22000","G-33000"],
    "2nd generation, G-x500 series (1978-80)": ["G-3500","G-4500","G-5500"],
    "3rd generation, Pure Power DC (1979-82, digital readout)": ["G-4700","G-5700","G-6700","G-7700","G-8700DB","G-9700"],
}
for label, models in GEN.items():
    tag = "G-series " + label
    for jm in models:
        e = by.get(jm)
        if not e:
            print("  !! not found:", jm); continue
        sf = e.get("special_features")
        if not sf:
            e["special_features"] = tag
        elif "G-series" not in sf:
            e["special_features"] = f"{tag}. {sf}"

with open(DB_PATH, "w", encoding="utf-8") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
print("\nint_model set for", len(INT), "export names; generation tags applied.")
