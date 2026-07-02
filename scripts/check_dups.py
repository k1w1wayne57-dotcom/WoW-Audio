import json
from collections import Counter
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
c = Counter(e['jdm_model'] for e in db)
dups = {k: v for k, v in c.items() if v > 1}
print('Duplicate jdm_model values:', dups)
for e in db:
    if e['jdm_model'] in dups:
        print(f"  {e['jdm_model']:14s} id={e['id']:30s} {e.get('year_start')}-{e.get('year_end')} type={e.get('type')} series={e.get('series')}")
