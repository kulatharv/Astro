import sys, os
sys.path.insert(0, os.path.abspath("."))
import re
from modules.kundali.engine import calculate_kundali
from modules.kundali.varga import calculate_navamsa

res = calculate_kundali(2004, 11, 2, 16, 15, 19.8762, 75.3433, tz_name='Asia/Kolkata')
nums = [float(x) for x in re.findall(r'\d+', res['lagna_degree'])]
deg_in_sign = nums[0] + nums[1]/60.0 + nums[2]/3600.0
signs = ['Mesha','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrischika','Dhanu','Makara','Kumbha','Meena']
lagna_lon = signs.index(res['lagna']) * 30.0 + deg_in_sign
print("Lagna absolute lon:", lagna_lon, "deg in Meena:", deg_in_sign)
d9_lagna = calculate_navamsa(lagna_lon)
print("D9 Lagna:", d9_lagna)
for p in res['planets']:
    deg = float(p.get('degree_decimal', p.get('degree')))
    p_lon = signs.index(p['sign']) * 30.0 + deg
    print(p['name'], "D1:", p['sign'], round(deg, 2), "D9:", calculate_navamsa(p_lon))
