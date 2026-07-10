import json
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
SPEC = ['watts_per_channel','freq_response_hz','thd_percent','amp_circuit','weight_kg']
def complete(e): return all(e.get(f) not in (None,'') for f in SPEC)
total = len(db)
done = sum(1 for e in db if complete(e))
print(f"Models with all 5 core specs: {done}/{total}  ({round(100*done/total)}%)")
# remaining by decade
from collections import Counter
c = Counter()
for e in db:
    if not complete(e):
        y = e.get('year_start') or 0
        dec = f"{(y//10)*10}s" if y else "unknown"
        c[dec]+=1
print("Remaining (missing >=1 core spec) by decade:")
for d in sorted(c):
    print(f"  {d}: {c[d]}")
# next oldest 15 still incomplete
inc = [e for e in db if not complete(e)]
inc.sort(key=lambda e:(e.get('year_start') or 9999, e['jdm_model']))
print("\nNext oldest incomplete:")
for e in inc[:15]:
    print(f"  {e.get('year_start')} {e['jdm_model']:12s} {e.get('type','')}")
