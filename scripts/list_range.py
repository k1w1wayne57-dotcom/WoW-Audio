import json, sys
lo, hi = int(sys.argv[1]), int(sys.argv[2])
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
SPEC = ['watts_per_channel','freq_response_hz','thd_percent','amp_circuit','weight_kg']
rows = []
for e in db:
    y = e.get('year_start') or 0
    if lo <= y <= hi:
        miss = [f for f in SPEC if e.get(f) in (None,'')]
        if miss:
            rows.append((y, e['jdm_model'], e.get('type',''), miss))
rows.sort()
for y, jm, t, miss in rows:
    print(f"{y} {jm:12s} {t:14s} missing: {','.join(m.split('_')[0] for m in miss)}")
print(f"\n{len(rows)} incomplete in {lo}-{hi}")
