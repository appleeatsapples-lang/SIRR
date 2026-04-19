#!/usr/bin/env python3
"""Element signature analysis — cross-tradition element convergence.

Reads output.json and constants.json (global_element_matrix).
Scans all module outputs for element references and tallies them
across traditions and independence groups.

Writes element_signature.json to Engine/.
"""

import json
import os
import re
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ENGINE, "output.json")
CONSTANTS_PATH = os.path.join(ENGINE, "constants.json")
SYNTHESIS_PATH = os.path.join(ENGINE, "modules", "synthesis.py")
OUT_PATH = os.path.join(ENGINE, "element_signature.json")

ELEMENTS = ["fire", "water", "earth", "air", "wood", "metal", "ether"]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def parse_system_groups():
    """Parse SYSTEM_TO_GROUP from synthesis.py."""
    with open(SYNTHESIS_PATH) as f:
        source = f.read()

    groups = {}
    in_block = False
    for line in source.split("\n"):
        if "SYSTEM_TO_GROUP" in line and "=" in line:
            in_block = True
            continue
        if in_block:
            if line.strip() == "}":
                break
            match = re.match(r'\s*"(\w+)"\s*:\s*"(\w+)"', line)
            if match:
                groups[match.group(1)] = match.group(2)
    return groups


# Per-module whitelist of fields containing genuine element values.
ELEMENT_FIELD_WHITELIST: dict[str, set[str]] = {
    "bazi_daymaster":    {"day_master_element"},
    "bazi_ten_gods":     {"day_master_element"},
    "chinese_zodiac":    {"stem_element"},
    "temperament":       {"primary_element", "secondary_element"},
    "elemental_letters": {"dominant_element", "secondary_element"},
    "nakshatra":         {"element"},
    "nine_star_ki":      {"year_element", "month_element"},
    "tibetan_mewa":      {"mewa_element", "parkha_element"},
    "onmyodo":           {"birth_element"},
    "nayin":             {"element"},
    "bazhai":            {"gua_element"},
    "taiyi":             {"taiyi_palace_element"},
}


def extract_elements(data: dict, module_id: str = "") -> list:
    """Extract element references from whitelisted fields only."""
    allowed = ELEMENT_FIELD_WHITELIST.get(module_id)
    if allowed is None:
        return []

    found = []
    for key, val in data.items():
        if key not in allowed:
            continue
        if isinstance(val, str):
            val_lower = val.lower()
            for elem in ELEMENTS:
                if elem in val_lower:
                    found.append(elem.capitalize())
    return list(set(found))


def main():
    output = load_json(OUTPUT_PATH)
    constants = load_json(CONSTANTS_PATH)
    system_groups = parse_system_groups()

    matrix = constants.get("global_element_matrix")
    if not matrix:
        print("WARNING: global_element_matrix not found in constants.json")
        print("Proceeding with element scan only.")

    results = output.get("results", [])

    # Tally elements across all modules
    element_votes = {e.capitalize(): [] for e in ELEMENTS}

    for r in results:
        mod_id = r.get("id", "")
        group = system_groups.get(mod_id, "unknown")
        data = r.get("data", {})
        elements = extract_elements(data, mod_id)

        for elem in elements:
            if elem in element_votes:
                element_votes[elem].append({
                    "module": mod_id,
                    "group": group,
                })

    # Compute summary
    summary = {}
    for elem, voters in element_votes.items():
        modules = list(set(v["module"] for v in voters))
        groups = list(set(v["group"] for v in voters))
        summary[elem] = {
            "module_count": len(modules),
            "group_count": len(groups),
            "modules": modules,
            "groups": groups,
        }

    # Determine dominant element
    ranked = sorted(summary.items(), key=lambda x: (-x[1]["module_count"], -x[1]["group_count"]))
    dominant = ranked[0][0] if ranked and ranked[0][1]["module_count"] > 0 else "NONE"

    # Cross-tradition mapping from matrix
    tradition_map = {}
    if matrix:
        for elem_key in ELEMENTS:
            elem_data = matrix.get(elem_key, {})
            if elem_data and not elem_key.startswith("_"):
                traditions = {}
                for trad_key, trad_val in elem_data.items():
                    if trad_key not in ("quality", "direction", "season", "note") and trad_val:
                        traditions[trad_key] = trad_val
                if traditions:
                    tradition_map[elem_key.capitalize()] = traditions

    result = {
        "dominant_element": dominant,
        "element_summary": {k: {
            "module_count": v["module_count"],
            "group_count": v["group_count"],
            "modules": v["modules"],
            "groups": v["groups"],
        } for k, v in ranked},
        "ranking": [{"element": k, "modules": v["module_count"], "groups": v["group_count"]} for k, v in ranked],
        "tradition_mapping": tradition_map,
        "matrix_present": matrix is not None,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Element Signature:")
    print(f"  Dominant: {dominant}")
    for elem, count in ranked:
        if count["module_count"] > 0:
            print(f"    {elem}: {count['module_count']} modules, {count['group_count']} groups")
    print(f"  Matrix present: {matrix is not None}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
