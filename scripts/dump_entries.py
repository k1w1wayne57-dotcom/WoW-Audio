import json, sys
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
needles = ['AU-111', 'AU-701', 'AU-X701', 'AU-alpha607', 'AU-319', 'AU-317', 'A-M99']
for e in db:
    jm = e['jdm_model']
    if any(n.lower() == jm.lower() or n.lower() in jm.lower() for n in needles):
        print(f"id={e['id']}")
        print(f"  jdm={jm!r} int={e.get('int_model')!r} type={e.get('type')} series={e.get('series')}")
        print(f"  years={e.get('year_start')}-{e.get('year_end')} src={e.get('year_source')}")
        print(f"  amp_circuit={e.get('amp_circuit')!r}")
        print()
