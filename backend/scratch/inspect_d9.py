import sys
import os
sys.path.insert(0, os.path.abspath("."))

from modules.kundali.engine import calculate_kundali

k = calculate_kundali(year=2004, month=11, day=2, hour=16, minute=15, lat=19.8762, lon=75.3433, timezone_offset=5.5, tz_name="Asia/Kolkata")
print("D1 Lagna:", k["lagna"], k["lagna_degree"])
print("D9 Lagna:", k["d9_lagna"])
print("D9 Houses:")
for h, planets in k["d9_houses"].items():
    print(f"  H{h}: {planets}")
print("\nD9 Planet Signs:")
for p in k["planets"]:
    print(f"  {p['name']:8s}: D1={p['sign']:10s} ({p['degree']:12s}) -> D9 Navamsha={p['navamsa']:10s}")
