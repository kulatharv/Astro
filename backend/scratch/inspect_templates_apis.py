import os
import re
import json
from pathlib import Path

tmpl_dir = Path(r"c:\Desktop\astro_may_res (2)\astro-platform\app\templates")
summary = {}

for f in sorted(tmpl_dir.glob("*.html")):
    text = f.read_text(encoding="utf-8", errors="ignore")
    fetches = re.findall(r"fetch\(['\"`]([^'\"`]+)['\"`]", text)
    # also check for endpoints in axios or XMLHttpRequest or $.ajax or string literals like '/api/'
    api_refs = re.findall(r"['\"`](/api/[^'\"`\s\?]+)['\"`]", text)
    all_apis = sorted(list(set(fetches + api_refs)))
    forms = re.findall(r"<form[^>]*>", text, re.I)
    inputs = re.findall(r"<input[^>]*name=['\"]([^'\"]+)['\"]", text, re.I)
    buttons = re.findall(r"<button[^>]*>([^<]+)</button>", text, re.I)
    scripts = len(re.findall(r"<script", text, re.I))
    styles = len(re.findall(r"<style", text, re.I))
    title = re.search(r"<title>([^<]+)</title>", text, re.I)
    
    # Extract navigation links
    nav_links = re.findall(r"href=['\"](/[^'\"]*)['\"]", text)
    
    summary[f.name] = {
        "size_bytes": len(text),
        "title": title.group(1).strip() if title else "No Title",
        "api_endpoints": all_apis,
        "form_count": len(forms),
        "input_names": sorted(list(set(inputs))),
        "script_blocks": scripts,
        "style_blocks": styles,
        "internal_nav_links": sorted(list(set(nav_links)))
    }

out_path = Path(r"c:\Desktop\astro_may_res (2)\astro-platform\backend\scratch\template_analysis.json")
out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"Template analysis written to {out_path} for {len(summary)} files.")
