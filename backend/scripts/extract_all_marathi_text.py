"""
Comprehensive Marathi Text Extractor & Audit Tool for AstroLogic.
Extracts every Marathi string from messages/mr.json and TypeScript localization files,
classifying by page/feature, UI context, character length, and linguistic fidelity.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT / "frontend"

def extract_all_marathi():
    audit_data = {
        "summary": {},
        "modules": {}
    }

    # 1. messages/mr.json
    mr_json_path = FRONTEND_DIR / "messages" / "mr.json"
    with open(mr_json_path, "r", encoding="utf-8") as f:
        mr_json = json.load(f)

    json_extracted = []
    def parse_dict(d, prefix=""):
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                parse_dict(v, full_key)
            elif isinstance(v, str):
                json_extracted.append({
                    "key": full_key,
                    "text": v,
                    "char_count": len(v),
                    "is_devanagari": bool(re.search(r"[\u0900-\u097F]", v))
                })

    parse_dict(mr_json)
    audit_data["modules"]["core_messages_mr_json"] = json_extracted

    # 2. Extract from TypeScript localizations
    ts_files = {
        "kundali": FRONTEND_DIR / "components" / "kundali" / "kundaliLocalization.ts",
        "prediction": FRONTEND_DIR / "components" / "prediction" / "predictionLocalization.ts",
        "panchang": FRONTEND_DIR / "components" / "panchang" / "panchangLocalization.ts",
        "horoscope": FRONTEND_DIR / "components" / "horoscope" / "horoscopeLocalization.ts",
        "blog": FRONTEND_DIR / "components" / "blog" / "blogLocalization.ts"
    }

    for mod_name, file_path in ts_files.items():
        if not file_path.exists():
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract string literals containing Devanagari characters
        # Pattern matches: "..." or '...' or `...` containing Devanagari
        matches = re.findall(r"(['\"`])([^'\"`]*[\u0900-\u097F][^'\"`]*)\1", content)
        unique_texts = []
        seen = set()
        for _, text in matches:
            t = text.strip()
            if t and t not in seen and len(t) > 1:
                seen.add(t)
                unique_texts.append({
                    "text": t,
                    "char_count": len(t)
                })

        audit_data["modules"][f"component_{mod_name}"] = unique_texts

    total_strings = sum(len(v) for v in audit_data["modules"].values())
    audit_data["summary"]["total_extracted_marathi_strings"] = total_strings
    audit_data["summary"]["modules_audited"] = list(audit_data["modules"].keys())

    # Write full JSON audit dump
    output_path = ROOT / "docs" / "marathi_text_extraction_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {total_strings} Marathi strings across all modules!")
    print(f"📁 Full audit dump written to: {output_path}")

    # Print summary breakdown
    for mod, items in audit_data["modules"].items():
        print(f"   • {mod}: {len(items)} strings")

if __name__ == "__main__":
    extract_all_marathi()

