import sys
import os
sys.path.insert(0, os.path.abspath("."))

import json
from modules.kundali.engine import calculate_kundali
from modules.prediction.engine import analyse_all_domains
from modules.kundali.jaimini import compute_jaimini_foundation
from shared.veda.jaimini_rules import parse_sign_index

# Compute for November 2, 2004, 16:15 Aurangabad
kundali = calculate_kundali(
    year=2004, month=11, day=2,
    hour=16, minute=15,
    lat=19.8762, lon=75.3433,
    timezone_offset=5.5, tz_name="Asia/Kolkata"
)

domains = analyse_all_domains(kundali)

# Map planet positions to absolute longitudes for Jaimini engine
planet_longitudes = {}
for p in kundali.get("planets", []):
    s_idx = parse_sign_index(p["sign"])
    deg_dec = p.get("degree_decimal", 0.0)
    abs_long = (s_idx - 1) * 30.0 + deg_dec
    planet_longitudes[p["name"]] = abs_long

# Compute Jaimini Foundation & Chara Dasha for cross-system validation
jaimini = compute_jaimini_foundation(
    lagna_sign=kundali.get("lagna"),
    planet_positions=planet_longitudes
)

output = {
    "basic": {
        "dob": "02/11/2004 (2 November 2004)",
        "time": "16:15 IST",
        "place": "Aurangabad, Maharashtra, India",
        "coordinates": "19.8762 N, 75.3433 E",
        "ayanamsha": kundali.get("ayanamsha"),
        "lagna": kundali.get("lagna"),
        "lagna_degree": kundali.get("lagna_degree")
    },
    "panchang": kundali.get("panchang"),
    "planets": kundali.get("planets"),
    "houses": kundali.get("houses"),
    "dashas": kundali.get("dashas"),
    "yogas": kundali.get("yogas"),
    "doshas": kundali.get("doshas"),
    "domain_analysis": domains.get("domains"),
    "jaimini_karakas": {k: {"planet": v.planet, "degree": v.degree_in_sign, "sign": v.sign_name} for k, v in jaimini.karakas.items()},
    "jaimini_arudhas": {k: {"final_sign": v.final_sign_name, "house_from_lagna": v.house_from_lagna} for k, v in jaimini.arudhas.items()},
    "chara_dasha_mahadashas": [
        {"order": m.order_index, "sign": m.sign_name, "duration": m.duration_years, "start": m.elapsed_start_years, "end": m.elapsed_end_years}
        for m in (jaimini.chara_dasha.mahadashas if jaimini.chara_dasha else [])
    ]
}

os.makedirs("scratch", exist_ok=True)
with open("scratch/validation_result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, default=str)

print("SUCCESS: Computed Kundali, Prediction Domains, and Jaimini for 02/11/2004 16:15 Aurangabad")
