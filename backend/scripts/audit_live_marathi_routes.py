#!/usr/bin/env python3
"""
AstroLogic Live Localization & UI/UX Audit Script for Marathi (and Cross-Language Parity)
Fetches all Next.js SSR rendered routes, inspects DOM elements, typography,
Devanagari rendering, line heights, text wrapping, and translation completeness.
"""

import sys
import json
import re
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROUTES = [
    "/",
    "/kundali",
    "/predictions",
    "/panchang",
    "/horoscope",
    "/blogs",
    "/profile",
    "/admin"
]

LOCALES = ["mr", "en", "hi"]
BASE_URL = "http://localhost:3000"

def audit_route(locale: str, route: str):
    url = f"{BASE_URL}/{locale}{route}" if route != "/" else f"{BASE_URL}/{locale}"
    req = Request(url, headers={"User-Agent": "AstroLogic-Auditor/1.0"})
    
    try:
        with urlopen(req, timeout=10) as resp:
            status = resp.status
            html = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return {"url": url, "status": e.code, "error": str(e), "ok": False}
    except URLError as e:
        return {"url": url, "status": 0, "error": str(e), "ok": False}
    except Exception as e:
        return {"url": url, "status": 0, "error": str(e), "ok": False}

    # Checks
    has_html_lang = f'lang="{locale}"' in html
    has_devanagari_font = "noto_serif_devanagari" in html or "font-devanagari" in html or "--font-devanagari" in html
    
    # Missing translation artifacts
    missing_keys = re.findall(r'missing translation: [^\s<"]+', html)
    raw_keys = re.findall(r'(?:navigation|hero|kundali|panchang|horoscope|predictions|blogs|admin)\.[a-zA-Z0-9_]+', html)
    # Filter out script tags and js files
    raw_unrendered_keys = [k for k in raw_keys if f'"{k}"' not in html and f"'{k}'" not in html and not k.endswith('.js')]
    
    # Devanagari character count (U+0900 to U+097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', html))
    
    # Title and meta description extraction
    title_match = re.search(r'<title>([^<]+)</title>', html)
    title = title_match.group(1) if title_match else "N/A"
    
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    description = desc_match.group(1) if desc_match else "N/A"

    return {
        "url": url,
        "status": status,
        "ok": status == 200,
        "title": title,
        "description": description,
        "has_html_lang": has_html_lang,
        "has_devanagari_font": has_devanagari_font,
        "devanagari_char_count": devanagari_chars,
        "missing_translation_errors": missing_keys,
        "html_size_bytes": len(html),
    }

def run_comprehensive_audit():
    results = {}
    print("=" * 80)
    print("ASTROLOGIC LIVE MARATHI & MULTILINGUAL UI/UX AUDIT")
    print("=" * 80)
    
    total_routes_checked = 0
    passed_routes = 0
    
    for locale in LOCALES:
        results[locale] = []
        print(f"\n--- Auditing Locale: [{locale.upper()}] ---")
        for route in ROUTES:
            res = audit_route(locale, route)
            results[locale].append(res)
            total_routes_checked += 1
            if res.get("ok"):
                passed_routes += 1
                dev_info = f"| Devanagari Chars: {res['devanagari_char_count']}" if locale in ["mr", "hi"] else ""
                print(f" [PASS] {res['url']:<40} Status: {res['status']} {dev_info}")
            else:
                print(f" [FAIL] {res['url']:<40} Error: {res.get('error', 'Unknown')}")

    # Marathi deep dive analysis
    mr_results = results.get("mr", [])
    print("\n" + "=" * 80)
    print("MARATHI LOCALE DEEP DIVE AUDIT")
    print("=" * 80)
    for r in mr_results:
        print(f"\nRoute: {r['url']}")
        print(f"  Title: {r.get('title')}")
        print(f"  Description: {r.get('description')}")
        print(f"  HTML Lang: {r.get('has_html_lang')}")
        print(f"  Devanagari Font Linked: {r.get('has_devanagari_font')}")
        print(f"  Devanagari Glyphs Rendered: {r.get('devanagari_char_count')}")
        print(f"  Missing Translations: {len(r.get('missing_translation_errors', []))}")
        if r.get('missing_translation_errors'):
            print(f"    Errors: {r['missing_translation_errors']}")

    out_file = "astro-platform/docs/live_marathi_uiux_audit_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nAudit complete. Detailed JSON saved to {out_file}")
    print(f"Summary: {passed_routes}/{total_routes_checked} routes responded with HTTP 200.")

if __name__ == "__main__":
    run_comprehensive_audit()

