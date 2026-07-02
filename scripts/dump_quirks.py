import json, re
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
print("=== Names with '/', 'gen', or parentheses ===")
for e in db:
    jm = e['jdm_model']
    if '/' in jm or re.search(r'gen', jm, re.I) or '(' in jm:
        print(f"  id={e['id']:38s} jdm={jm!r:40s} int={e.get('int_model')!r} {e.get('year_start')}-{e.get('year_end')} src={e.get('year_source')}")
print("\n=== All AU-D* and AU-alpha* (to see the family) ===")
for e in db:
    jm = e['jdm_model']
    if jm.upper().startswith('AU-D') or 'alpha' in jm.lower():
        print(f"  id={e['id']:40s} jdm={jm!r:34s} int={e.get('int_model')!r} {e.get('year_start')}-{e.get('year_end')}")
