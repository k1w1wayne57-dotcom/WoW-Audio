import json
s = json.load(open('scripts/serials_parsed.json', encoding='utf-8'))
def norm(k): return k.upper().replace(' ','')
for want in ['AU-D707','AU-D907','AU-D707F','AU-D9','AU-819','AU-919']:
    hit = None
    for k,v in s.items():
        if norm(k)==norm(want):
            hit=(k,v['min_year'],v['max_year'],v['n_dates']); break
    print(f"{want:10s} -> {hit}")
