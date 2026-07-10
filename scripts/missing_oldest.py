import json
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
SPEC = ['watts_per_channel','freq_response_hz','thd_percent','amp_circuit','weight_kg','japan_price_kyen']
db.sort(key=lambda e: (e.get('year_start') or 9999, e.get('jdm_model')))
for e in db[:30]:
    miss = [f for f in SPEC if e.get(f) in (None, '')]
    print(f"{str(e.get('year_start')):>4} {e['jdm_model']:14s} {e.get('type',''):16s} missing: {', '.join(miss) if miss else 'NONE'}")
