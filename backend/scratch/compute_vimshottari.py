import sys
import os
sys.path.insert(0, os.path.abspath("."))

from datetime import datetime, timedelta
from modules.kundali.dasha import calculate_mahadasha, generate_dasha_timeline, generate_dasha_chain

# Moon in Mithuna 15° 54' 41" -> 2 * 30 + 15.9114 = 75.9114°
moon_long = 2 * 30.0 + 15.9114
lord, balance = calculate_mahadasha(moon_long, "Ardra")
print(f"Starting Dasha at birth: {lord} with {balance:.2f} years remaining")

timeline = generate_dasha_timeline(lord, balance)
birth_dt = datetime(2004, 11, 2, 16, 15)

print("\n=== VIMSHOTTARI MAHADASHAS TIMELINE ===")
curr_start = birth_dt
for item in timeline:
    dur_days = item["years"] * 365.25
    curr_end = curr_start + timedelta(days=dur_days)
    print(f"- {item['lord']:8s}: {curr_start.strftime('%Y-%m-%d')} to {curr_end.strftime('%Y-%m-%d')} ({item['years']:.2f} yrs)")
    curr_start = curr_end

chain = generate_dasha_chain(birth_dt, timeline, year_convention="solar_365_25")
now_str = "2026-10-19"
print("\n=== SATURN-SATURN PRATYANTARDASHA BREAKDOWN ===")
for p in chain:
    if p['md_lord'] == 'Saturn' and p['ad_lord'] == 'Saturn':
        print(f"{p['md_lord']} - {p['ad_lord']} - {p['pd_lord']:8s}: {p['start']} to {p['end']}")

