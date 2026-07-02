import json
db = json.load(open('data/sansui.json', encoding='utf-8-sig'))
print('Total entries:', len(db))
print('year_source=serial-report:', sum(1 for e in db if e.get('year_source') == 'serial-report'))
print('year_end still null:', sum(1 for e in db if e.get('year_end') is None))
print('year_start still null:', sum(1 for e in db if e.get('year_start') is None))
print('\nAlpha series sample (year_end was null before):')
for e in db:
    if 'alpha' in e['jdm_model'].lower() and e.get('year_source') == 'serial-report':
        print(f"  {e['jdm_model']:26s} {e['year_start']}-{e['year_end']}")
