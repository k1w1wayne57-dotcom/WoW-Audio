import json
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
FIELDS = ["year_start", "watts_per_channel", "freq_response_hz", "thd_percent",
          "weight_kg", "amp_circuit", "ps_type", "collector_ranking", "japan_price_kyen"]
rows = [e for e in db if e.get("price_thb_listings")]
rows.sort(key=lambda e: e["jdm_model"])
print(f"{len(rows)} models have a Thai price.\n")
complete, gappy = [], []
for e in rows:
    miss = [f for f in FIELDS if e.get(f) in (None, "")]
    if not e.get("links", {}).get("audio_database"): miss.append("adb_link")
    if e.get("collector_ranking") == "Unranked": miss.append("ranking(Unranked)")
    thb = "/".join(f"{v:,}" for v in e["price_thb_listings"])
    if miss:
        gappy.append((e["jdm_model"], thb, miss))
    else:
        complete.append((e["jdm_model"], thb))

print("=== MODELS WITH GAPS ===")
for jm, thb, miss in gappy:
    short = ",".join(m.split("_")[0] if "_" in m else m for m in miss)
    print(f"  {jm:20s} THB {thb:16s} missing: {short}")
print(f"\n=== COMPLETE ({len(complete)}) ===")
print("  " + ", ".join(jm for jm, _ in complete))
