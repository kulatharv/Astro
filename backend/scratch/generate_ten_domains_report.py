import json

with open("scratch/domains_raw.json", "r", encoding="utf-8") as f:
    domains = json.load(f)

domain_keys = [
    "marriage", "career", "wealth", "health", "children",
    "education", "property", "challenges", "travel", "spirituality"
]

report_lines = []

for d in domain_keys:
    data = domains.get(d, {})
    title = data.get("domain", d.title())
    score = data.get("score", 0)
    
    report_lines.append(f"## {title} (Score: {score}/100)")
    
    # Specific attributes
    for k, v in data.items():
        if k in ["domain", "icon", "score", "timing", "timing_windows", "timing_legacy", "rule_evidence", "remedies", "peak_window", "next_12_months_summary", "timing_methodology", "timing_engine"]:
            continue
        if isinstance(v, (str, int, float, bool)) and v != "":
            report_lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
        elif isinstance(v, list) and v:
            items_str = ", ".join(str(x) for x in v)
            report_lines.append(f"- **{k.replace('_', ' ').title()}:** {items_str}")
            
    # Peak window
    pw = data.get("peak_window")
    if pw and isinstance(pw, dict):
        report_lines.append(f"- **Peak Timing Window:** {pw.get('start')} to {pw.get('end')} (Peak: {pw.get('peak_date')}, Confidence: {pw.get('confidence')})")
        if pw.get("drivers"):
            report_lines.append(f"  - *Drivers:* {'; '.join(pw.get('drivers'))}")

    # Remedies
    rem = data.get("remedies", {})
    if rem:
        ritual = rem.get("ritual")
        if ritual:
            report_lines.append(f"- **Prescribed Ritual:** {ritual}")
        planets_rem = rem.get("planet_remedies", [])
        if planets_rem:
            p_items = [f"{pr.get('planet')}: Mantra '{pr.get('mantra')}', Gem: {pr.get('gem')}, Donate: {pr.get('donate')}" for pr in planets_rem[:2]]
            report_lines.append(f"- **Planetary Remedies:** {'; '.join(p_items)}")

    report_lines.append("\n" + "-"*40 + "\n")

with open("scratch/ten_domains_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print("SUCCESS: Generated scratch/ten_domains_report.md")
