"""
Deep Marathi Localization & UI/UX Audit Script.
Extracts all Marathi strings from messages/mr.json and TypeScript localization files,
verifies Devanagari encoding, checks for Hindi/English leakage, and analyzes key density.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT / "frontend"

def audit_json_messages():
    mr_path = FRONTEND_DIR / "messages" / "mr.json"
    en_path = FRONTEND_DIR / "messages" / "en.json"
    hi_path = FRONTEND_DIR / "messages" / "hi.json"

    with open(mr_path, "r", encoding="utf-8") as f:
        mr_json = json.load(f)
    with open(en_path, "r", encoding="utf-8") as f:
        en_json = json.load(f)
    with open(hi_path, "r", encoding="utf-8") as f:
        hi_json = json.load(f)

    print("=================================================================")
    print("        ASTROLOGIC MARATHI LOCALIZATION & UI/UX AUDIT            ")
    print("=================================================================")

    # 1. Structural Parity
    en_keys = set(en_json.keys())
    mr_keys = set(mr_json.keys())
    hi_keys = set(hi_json.keys())

    missing_in_mr = en_keys - mr_keys
    extra_in_mr = mr_keys - en_keys
    print(f"\n1. Root Section Parity:")
    print(f"   - English sections: {len(en_keys)}")
    print(f"   - Marathi sections: {len(mr_keys)}")
    print(f"   - Missing in Marathi: {list(missing_in_mr) if missing_in_mr else 'None (100% matched)'}")
    print(f"   - Extra in Marathi: {list(extra_in_mr) if extra_in_mr else 'None'}")

    # 2. Extract and Classify all Marathi strings
    mr_strings = {}
    english_fallbacks = []
    hindi_loanword_suspects = []

    # Common Hindi words that should be authentic Marathi:
    # Hindi: 'राशिफल' -> Marathi: 'राशीभविष्य'
    # Hindi: 'कुंडली' -> Marathi: 'जन्मपत्रिका' / 'कुंडली'
    # Hindi: 'आज का' -> Marathi: 'आजचे'
    # Hindi: 'दोष' -> Marathi: 'दोष'
    # Hindi: 'उपाय' -> Marathi: 'तोडगे / उपाय'
    # Hindi: 'वर्ष' -> Marathi: 'वर्ष'
    # Hindi: 'मित्र' -> Marathi: 'मित्र'
    # Hindi: 'नहीं' -> Marathi: 'नाही'
    # Hindi: 'है' -> Marathi: 'आहे'
    # Hindi: 'था' -> Marathi: 'होता'
    # Hindi: 'होगी' -> Marathi: 'होईल'
    hindi_markers = [r"\bनहीं\b", r"\bहै\b", r"\bथा\b", r"\bहोगी\b", r"\bहोगा\b", r"\bआज का\b", r"\bराशिफल\b"]

    def recurse(data, prefix=""):
        if isinstance(data, dict):
            for k, v in data.items():
                recurse(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(data, str):
            mr_strings[prefix] = data
            # Check for English leak
            latin = re.findall(r"[a-zA-Z]", data)
            deva = re.findall(r"[\u0900-\u097F]", data)
            if len(latin) > 4 and len(deva) == 0 and not data.startswith("/") and not data.startswith("http"):
                english_fallbacks.append((prefix, data))
            
            # Check for Hindi leak
            for h_pattern in hindi_markers:
                if re.search(h_pattern, data):
                    hindi_loanword_suspects.append((prefix, h_pattern, data))

    recurse(mr_json)

    print(f"\n2. Marathi String Density & Health in messages/mr.json:")
    print(f"   - Total Localized Strings: {len(mr_strings)}")
    print(f"   - English Fallbacks (Untranslated): {len(english_fallbacks)}")
    print(f"   - Hindi Grammar Leakage Suspects: {len(hindi_loanword_suspects)}")

    if english_fallbacks:
        print("\n   [!] Untranslated English Strings in mr.json:")
        for p, s in english_fallbacks[:10]:
            print(f"       • {p}: \"{s}\"")

    if hindi_loanword_suspects:
        print("\n   [!] Potential Hindi Grammar/Loanword Leakage in mr.json:")
        for p, marker, s in hindi_loanword_suspects[:10]:
            print(f"       • {p} (Matched {marker}): \"{s[:80]}...\"")

    return mr_strings

def audit_component_localizations():
    print("\n3. Auditing TypeScript Component Localization Dictionaries:")
    comp_files = [
        ("Kundali", FRONTEND_DIR / "components" / "kundali" / "kundaliLocalization.ts"),
        ("Prediction", FRONTEND_DIR / "components" / "prediction" / "predictionLocalization.ts"),
        ("Panchang", FRONTEND_DIR / "components" / "panchang" / "panchangLocalization.ts"),
        ("Horoscope", FRONTEND_DIR / "components" / "horoscope" / "horoscopeLocalization.ts"),
        ("Blog", FRONTEND_DIR / "components" / "blog" / "blogLocalization.ts"),
    ]

    for name, path in comp_files:
        if not path.exists():
            print(f"   [x] {name}: File NOT found at {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        has_mr = "mr:" in content or "'mr'" in content or '"mr"' in content
        size_kb = len(content) / 1024
        print(f"   [✓] {name} Localization: {size_kb:.1f} KB | Has Marathi dictionary: {has_mr}")

if __name__ == "__main__":
    audit_json_messages()
    audit_component_localizations()

