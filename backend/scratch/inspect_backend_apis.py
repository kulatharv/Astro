import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, r"c:\Desktop\astro_may_res (2)\astro-platform\backend")

import json
from gateway.main import app

routes_info = []

for route in app.routes:
    methods = list(getattr(route, "methods", []))
    path = getattr(route, "path", None)
    name = getattr(route, "name", None)
    endpoint = getattr(route, "endpoint", None)
    doc = endpoint.__doc__ if endpoint else ""
    
    # check dependencies / signature
    routes_info.append({
        "path": path,
        "name": name,
        "methods": sorted(methods) if methods else [],
        "doc": doc.strip() if doc else "",
        "tags": getattr(route, "tags", [])
    })

# sort by path
routes_info.sort(key=lambda x: (x["path"] or "", x["name"] or ""))

out_path = Path(r"c:\Desktop\astro_may_res (2)\astro-platform\backend\scratch\backend_api_inventory.json")
out_path.write_text(json.dumps(routes_info, indent=2), encoding="utf-8")
print(f"Backend API inventory written to {out_path} ({len(routes_info)} routes).")
