import json
with open('scratch/validation_result.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== DOSHAS ===")
if isinstance(d.get('doshas'), list):
    for item in d['doshas']:
        if isinstance(item, dict):
            print(f"- {item.get('name', 'Dosha')}: present={item.get('present')} ({item.get('intensity', '')}) - {item.get('description', '')}")
        else:
            print(f"- {item}")
elif isinstance(d.get('doshas'), dict):
    for dosha, val in d['doshas'].items():
        print(f"- {dosha}: {val}")

print("\n=== DOMAINS ANALYSIS ===")
for dom, info in d['domain_analysis'].items():
    print(f"- {dom.upper()}: Score={info.get('score')} ({info.get('level')})")
    pos = info.get('positive_factors', [])
    neg = info.get('negative_factors', [])
    if pos:
        print(f"    Key Positive: {pos[0]}")
    if neg:
        print(f"    Key Negative: {neg[0]}")

print("\n=== JAIMINI CHARA KARAKAS (7-Karaka Scheme) ===")
for k, v in d['jaimini_karakas'].items():
    print(f"- {k:4s}: {v['planet']:8s} ({v['degree']:.2f}° in {v['sign']})")

print("\n=== JAIMINI ARUDHAS ===")
for k, v in d['jaimini_arudhas'].items():
    print(f"- {k:4s}: Sign {v['final_sign']} (House {v['house_from_lagna']} from Lagna)")

print("\n=== CHARA DASHA (MAHADASHA PROGRESSION) ===")
for cd in d['chara_dasha_mahadashas']:
    print(f"- Order {cd['order']:2d}: {cd['sign']:12s} Duration: {cd['duration']:2d} yrs (Elapsed: {cd['start']:5.1f} -> {cd['end']:5.1f} yrs)")
