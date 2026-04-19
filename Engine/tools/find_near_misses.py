#!/usr/bin/env python3
"""Find near-miss convergences — values one system or one group short.

Reads output.json and re-analyzes the raw system results to find numbers
that almost converge but fall short of the 3-system/2-group threshold.

Writes near_misses.json to Engine/.
"""

import json
import os
import re
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ENGINE, "output.json")
SYNTHESIS_PATH = os.path.join(ENGINE, "modules", "synthesis.py")
OUT_PATH = os.path.join(ENGINE, "near_misses.json")

# We need to know the CONVERGENCE_FIELDS and SYSTEM_TO_GROUP to replicate
# the convergence detection. We'll parse them from synthesis.py.


def load_json(path):
    with open(path) as f:
        return json.load(f)


def parse_system_groups():
    """Parse SYSTEM_TO_GROUP from synthesis.py."""
    with open(SYNTHESIS_PATH) as f:
        source = f.read()

    groups = {}
    # Match lines like:  "module_id": "group_name",
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


def parse_convergence_fields():
    """Parse CONVERGENCE_FIELDS to know which fields to extract per module."""
    with open(SYNTHESIS_PATH) as f:
        source = f.read()

    fields = {}
    in_block = False
    brace_depth = 0

    for line in source.split("\n"):
        if "CONVERGENCE_FIELDS" in line and "=" in line and "{" in line:
            in_block = True
            brace_depth = 1
            continue
        if in_block:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                break
            # Match: "module": {"field1", "field2"},
            match = re.match(r'\s*"(\w+)"\s*:\s*\{([^}]*)\}', line)
            if match:
                mod = match.group(1)
                field_str = match.group(2).strip()
                if field_str:
                    fset = set(re.findall(r'"(\w+)"', field_str))
                    fields[mod] = fset
                else:
                    fields[mod] = set()
            # Match: "module": set(),
            match2 = re.match(r'\s*"(\w+)"\s*:\s*set\(\)', line)
            if match2:
                fields[match2.group(1)] = set()
            # Match: "module": None,
            match3 = re.match(r'\s*"(\w+)"\s*:\s*None', line)
            if match3:
                fields[match3.group(1)] = None  # all fields

    return fields


def extract_numbers(data: dict, allowed_fields) -> set:
    """Extract integers 1-33 from whitelisted fields."""
    numbers = set()
    if allowed_fields is None:
        # All fields
        items = data.items()
    elif len(allowed_fields) == 0:
        return numbers
    else:
        items = [(k, v) for k, v in data.items() if k in allowed_fields]

    for key, val in items:
        if isinstance(val, int) and 1 <= val <= 33:
            numbers.add(val)
    return numbers


def main():
    output = load_json(OUTPUT_PATH)
    system_groups = parse_system_groups()
    conv_fields = parse_convergence_fields()

    results = output.get("results", [])

    # Only use COMPUTED_STRICT and LOOKUP_FIXED
    lockable = [r for r in results if r.get("certainty") in ("COMPUTED_STRICT", "LOOKUP_FIXED")]

    # Collect votes: number -> [(module_id, group)]
    votes = {}
    for r in lockable:
        mod_id = r.get("id", "")
        group = system_groups.get(mod_id, "unknown")
        allowed = conv_fields.get(mod_id)
        if allowed is not None and len(allowed) == 0:
            continue  # set() modules excluded
        nums = extract_numbers(r.get("data", {}), allowed)
        for n in nums:
            if n not in votes:
                votes[n] = []
            votes[n].append((mod_id, group))

    # Find existing convergences (3+ systems, 2+ groups)
    synthesis = output.get("synthesis", {})
    existing_numbers = set()
    for conv in synthesis.get("number_convergences", []):
        existing_numbers.add(conv.get("number"))

    # Find near-misses
    one_system_short = []  # 2 systems, 2+ groups
    one_group_short = []   # 3+ systems, 1 group

    for number, voter_list in sorted(votes.items()):
        if number in existing_numbers:
            continue

        systems = list(set(v[0] for v in voter_list))
        groups = list(set(v[1] for v in voter_list))
        sys_count = len(systems)
        grp_count = len(groups)

        entry = {
            "number": number,
            "system_count": sys_count,
            "group_count": grp_count,
            "systems": systems,
            "groups": groups,
            "missing": [],
        }

        if sys_count == 2 and grp_count >= 2:
            entry["missing"].append("1 more system needed (have 2 systems, 2+ groups)")
            one_system_short.append(entry)
        elif sys_count >= 3 and grp_count == 1:
            entry["missing"].append("1 more independence group needed (have 3+ systems, 1 group)")
            one_group_short.append(entry)
        elif sys_count == 2 and grp_count == 1:
            entry["missing"].append("1 system + 1 group needed")
            one_system_short.append(entry)

    result = {
        "total_existing_convergences": len(existing_numbers),
        "one_system_short": len(one_system_short),
        "one_group_short": len(one_group_short),
        "near_misses_system": one_system_short,
        "near_misses_group": one_group_short,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Existing convergences: {len(existing_numbers)}")
    print(f"Near misses (1 system short): {len(one_system_short)}")
    print(f"Near misses (1 group short): {len(one_group_short)}")
    for nm in one_system_short:
        print(f"  Number {nm['number']}: {nm['system_count']} systems, {nm['group_count']} groups — {nm['systems']}")
    for nm in one_group_short:
        print(f"  Number {nm['number']}: {nm['system_count']} systems, {nm['group_count']} groups — {nm['systems']}")
    print(f"\nWritten to {OUT_PATH}")


if __name__ == "__main__":
    main()
