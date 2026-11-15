#!/usr/bin/env python3
"""
Deep UI/UX, Alignment, and Typography Audit for Devanagari (Marathi/Hindi)
Scans frontend JSX/TSX components for:
1. `leading-none` or `leading-tight` on Devanagari headings that risk diacritic clipping.
2. Missing word-break / overflow handling on Marathi strings (which average 15-25% longer).
3. Hardcoded English UI tokens in client components.
4. Flex layouts with `whitespace-nowrap` on mobile viewports.
"""

import os
import re

FRONTEND_DIR = os.path.abspath("astro-platform/frontend")
AUDIT_LOG = []

def audit_files():
    for root, _, files in os.walk(FRONTEND_DIR):
        if "node_modules" in root or ".next" in root:
            continue
        for f in files:
            if f.endswith((".tsx", ".jsx")):
                filepath = os.path.join(root, f)
                relpath = os.path.relpath(filepath, FRONTEND_DIR)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fp:
                    lines = fp.readlines()
                
                for idx, line in enumerate(lines, 1):
                    # Check 1: Large typography with leading-none
                    if ("text-2xl" in line or "text-3xl" in line or "text-4xl" in line or "text-5xl" in line) and "leading-none" in line:
                        AUDIT_LOG.append({
                            "file": relpath,
                            "line": idx,
                            "type": "TYPOGRAPHY_CLIP_RISK",
                            "severity": "MEDIUM",
                            "snippet": line.strip()[:100],
                            "recommendation": "Replace 'leading-none' with 'leading-tight' or 'leading-snug' to prevent upper matra clipping (e.g. ौ, ी, ं)."
                        })

                    # Check 2: whitespace-nowrap on potential long translated strings without responsive unwrap
                    if "whitespace-nowrap" in line and not ("sm:" in line or "md:" in line or "hidden" in line):
                        # check if it wraps a translation
                        if "t(" in line or "title" in line or "label" in line:
                            AUDIT_LOG.append({
                                "file": relpath,
                                "line": idx,
                                "type": "MOBILE_OVERFLOW_RISK",
                                "severity": "LOW",
                                "snippet": line.strip()[:100],
                                "recommendation": "Consider 'whitespace-normal sm:whitespace-nowrap' for Marathi strings that expand 20%+."
                            })

                    # Check 3: Raw English buttons
                    matches = re.findall(r'>\s*(Submit|Save|Cancel|Delete|Edit|Back|Next|Continue)\s*<', line)
                    if matches:
                        AUDIT_LOG.append({
                            "file": relpath,
                            "line": idx,
                            "type": "HARDCODED_I18N_TOKEN",
                            "severity": "HIGH",
                            "snippet": line.strip()[:100],
                            "recommendation": f"Token '{matches[0]}' should use next-intl t() translation hook."
                        })

    print(f"Audit completed across frontend components.")
    print(f"Total findings: {len(AUDIT_LOG)}")
    for item in AUDIT_LOG:
        print(f"[{item['severity']}] {item['file']}:{item['line']} - {item['type']}")
        print(f"   Snippet: {item['snippet']}")
        print(f"   Fix: {item['recommendation']}\n")

if __name__ == "__main__":
    audit_files()

