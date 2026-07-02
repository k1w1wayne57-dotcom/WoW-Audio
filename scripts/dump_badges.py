import json, re
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
for badge in ['607', '707', '907', '701', '717', '719', '819', '919']:
    print(f"=== models containing {badge} ===")
    for e in db:
        jm = e['jdm_model']
        if badge in jm:
            print(f"  id={e['id']:40s} jdm={jm!r:32s} int={e.get('int_model')!r} {e.get('year_start')}-{e.get('year_end')} src={e.get('year_source')}")
    print()
