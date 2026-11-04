import json

with open('scratch/validation_result.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for dom, info in d['domain_analysis'].items():
    print(f"=== {dom.upper()} (Score: {info.get('score')}) ===")
    print("Summary:", info.get('summary'))
    if info.get('positive_factors'):
        print("Positives:", info.get('positive_factors'))
    if info.get('negative_factors'):
        print("Negatives:", info.get('negative_factors'))
    if info.get('remedies'):
        print("Remedies:", info.get('remedies'))
    print("-" * 50)
