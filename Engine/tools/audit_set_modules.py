#!/usr/bin/env python3
"""Audit modules with set() in CONVERGENCE_FIELDS.

Reads modules/synthesis.py to find which modules have empty convergence fields,
then reads output.json to inspect their actual data fields and report which
fields could be candidates for promotion.

Writes set_modules_audit.json to Engine/.
"""

import ast
import json
import os
import re
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNTHESIS_PATH = os.path.join(ENGINE, "modules", "synthesis.py")
OUTPUT_PATH = os.path.join(ENGINE, "output.json")
OUT_PATH = os.path.join(ENGINE, "set_modules_audit.json")


def parse_set_modules():
    """Find modules with set() in CONVERGENCE_FIELDS by reading synthesis.py."""
    with open(SYNTHESIS_PATH) as f:
        source = f.read()

    # Find CONVERGENCE_FIELDS dict region
    set_modules = []
    # Match lines like:  "module_name": set(),
    pattern = re.compile(r'"(\w+)"\s*:\s*set\(\)', re.MULTILINE)
    for match in pattern.finditer(source):
        set_modules.append(match.group(1))

    # Also check for None (legacy all-fields)
    none_pattern = re.compile(r'"(\w+)"\s*:\s*None', re.MULTILINE)
    none_modules = [m.group(1) for m in none_pattern.finditer(source)]

    return set_modules, none_modules


def get_module_output(results: list, module_id: str) -> dict:
    """Find a module's output in the results array."""
    for r in results:
        if r.get("id") == module_id:
            return r
    return {}


def analyze_fields(data: dict) -> list:
    """Analyze data fields for convergence potential."""
    candidates = []
    for key, val in data.items():
        field_info = {
            "field": key,
            "type": type(val).__name__,
            "value": val if not isinstance(val, (list, dict)) else f"[{type(val).__name__} len={len(val)}]",
        }
        # Check if integer in convergence-friendly range
        if isinstance(val, int) and 1 <= val <= 33:
            field_info["promotable"] = True
            field_info["reason"] = f"Integer {val} in range 1-33"
        elif isinstance(val, int):
            field_info["promotable"] = False
            field_info["reason"] = f"Integer {val} outside 1-33"
        elif isinstance(val, float):
            field_info["promotable"] = False
            field_info["reason"] = "Float — not integer scale"
        elif isinstance(val, str):
            field_info["promotable"] = False
            field_info["reason"] = "Categorical string"
        elif isinstance(val, (list, dict)):
            field_info["promotable"] = False
            field_info["reason"] = "Complex structure"
        elif isinstance(val, bool):
            field_info["promotable"] = False
            field_info["reason"] = "Boolean"
        else:
            field_info["promotable"] = False
            field_info["reason"] = f"Unknown type: {type(val).__name__}"

        candidates.append(field_info)
    return candidates


def main():
    set_modules, none_modules = parse_set_modules()
    print(f"Found {len(set_modules)} set() modules, {len(none_modules)} None modules")

    output = None
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            output = json.load(f)

    results = output.get("results", []) if output else []

    audits = []
    promotable_count = 0

    for mod_id in sorted(set_modules):
        mod_output = get_module_output(results, mod_id)
        data = mod_output.get("data", {})
        certainty = mod_output.get("certainty", "UNKNOWN")

        fields = analyze_fields(data)
        has_promotable = any(f.get("promotable") for f in fields)
        if has_promotable:
            promotable_count += 1

        audits.append({
            "module": mod_id,
            "certainty": certainty,
            "field_count": len(data),
            "has_promotable_fields": has_promotable,
            "fields": fields,
        })

    result = {
        "total_set_modules": len(set_modules),
        "total_none_modules": len(none_modules),
        "none_modules": none_modules,
        "modules_with_promotable_fields": promotable_count,
        "audits": audits,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nPromotion candidates: {promotable_count}/{len(set_modules)} set() modules have promotable fields")
    for a in audits:
        if a["has_promotable_fields"]:
            promo_fields = [f for f in a["fields"] if f.get("promotable")]
            print(f"  {a['module']}: {[f['field'] + '=' + str(f['value']) for f in promo_fields]}")

    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
