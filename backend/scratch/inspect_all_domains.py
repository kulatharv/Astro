import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
from modules.kundali.engine import calculate_kundali
from modules.prediction.engine import analyse_all_domains

k = calculate_kundali(
    year=2004, month=11, day=2,
    hour=16, minute=15,
    lat=19.8762, lon=75.3433,
    timezone_offset=5.5, tz_name="Asia/Kolkata"
)

res = analyse_all_domains(k)

with open("scratch/domains_raw.json", "w", encoding="utf-8") as f:
    json.dump(res["domains"], f, indent=2, default=str)

for d, v in res["domains"].items():
    print(f"==================== {d.upper()} ====================")
    for key, val in v.items():
        if key in ["remedies", "rule_evidence", "timing_legacy"]:
            continue
        if isinstance(val, (str, int, float, bool)) or (isinstance(val, list) and len(val) <= 5):
            print(f"  {key}: {val}")
        elif isinstance(val, dict) and key in ["timing", "peak_window"]:
            print(f"  {key}: {val}")
    print()
