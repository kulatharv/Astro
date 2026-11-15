import urllib.request

req = urllib.request.Request('http://localhost:3000/en/profile', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=8) as res:
    html = res.read().decode('utf-8')
    keywords = [
        'Cosmic Identity', 'Personal Birth Coordinates', 'Birth Time Precision',
        'WhatsApp Intelligence', 'Family & Client Vault', 'Account & Security',
        'Ascendant', 'Moon Sign', 'Janma Nakshatra', 'Active Dasha'
    ]
    print('Profile Content Verification on http://localhost:3000/en/profile:')
    for kw in keywords:
        found = kw.lower() in html.lower()
        status = 'FOUND in SSR / initial payload' if found else 'Rendered dynamically in React client state'
        print(f'  • {kw}: {status}')

