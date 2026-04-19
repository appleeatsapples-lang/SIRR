#!/usr/bin/env python3
"""
Stress-test diff: compares two SIRR engine outputs module-by-module.
Usage: python tools/stress_test_diff.py output_original.json output_mutated.json
"""
import json
import sys
from datetime import datetime


def deep_diff(a, b, path=""):
    """Recursively find all differing leaf values between two structures."""
    diffs = []
    if type(a) != type(b):
        diffs.append((path or "root", a, b))
        return diffs
    if isinstance(a, dict):
        all_keys = set(list(a.keys()) + list(b.keys()))
        for k in sorted(all_keys):
            p = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append((p, "<missing>", b[k]))
            elif k not in b:
                diffs.append((p, a[k], "<missing>"))
            else:
                diffs.extend(deep_diff(a[k], b[k], p))
    elif isinstance(a, list):
        for i in range(max(len(a), len(b))):
            p = f"{path}[{i}]"
            if i >= len(a):
                diffs.append((p, "<missing>", b[i]))
            elif i >= len(b):
                diffs.append((p, a[i], "<missing>"))
            else:
                diffs.extend(deep_diff(a[i], b[i], p))
    else:
        if a != b:
            diffs.append((path, a, b))
    return diffs


def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/stress_test_diff.py <original.json> <mutated.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        orig = json.load(f)
    with open(sys.argv[2]) as f:
        mut = json.load(f)

    orig_results = {r["id"]: r for r in orig.get("results", [])}
    mut_results = {r["id"]: r for r in mut.get("results", [])}

    all_ids = sorted(set(list(orig_results.keys()) + list(mut_results.keys())))

    unchanged = []
    changed = []
    errors = []

    for mid in all_ids:
        if mid not in orig_results:
            errors.append((mid, "missing in original"))
            continue
        if mid not in mut_results:
            errors.append((mid, "missing in mutated"))
            continue

        o = orig_results[mid]
        m = mut_results[mid]

        # Compare data dict only (skip meta fields like constants_version)
        o_data = o.get("data", {})
        m_data = m.get("data", {})

        diffs = deep_diff(o_data, m_data)
        if diffs:
            changed.append((mid, diffs))
        else:
            unchanged.append(mid)

    total = len(all_ids)
    n_unchanged = len(unchanged)
    n_changed = len(changed)
    n_errors = len(errors)

    # --- Print report ---
    print("=" * 70)
    print(f"STRESS-TEST DIFF: Birth Time +20 min (10:14 → 10:34)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print(f"\n## SUMMARY")
    print(f"Total modules: {total}")
    print(f"Unchanged: {n_unchanged} ({100*n_unchanged/total:.1f}%)")
    print(f"Changed: {n_changed} ({100*n_changed/total:.1f}%)")
    print(f"Errors: {n_errors}")

    if errors:
        print(f"\n## ERRORS")
        for mid, reason in errors:
            print(f"  - {mid}: {reason}")

    if changed:
        print(f"\n## CHANGED MODULES ({n_changed})")
        for mid, diffs in changed:
            print(f"\n### {mid}")
            for field, old_val, new_val in diffs:
                old_s = _truncate(old_val)
                new_s = _truncate(new_val)
                print(f"  {field}: {old_s} → {new_s}")

    print(f"\n## UNCHANGED MODULES ({n_unchanged})")
    for mid in unchanged:
        print(f"  - {mid}")

    # --- Convergence check ---
    print(f"\n## CONVERGENCE CHECK (10 signatures)")
    _check_convergences(orig, mut, orig_results, mut_results)

    # --- Ascendant status ---
    print(f"\n## ASCENDANT STATUS")
    _check_ascendant(orig_results, mut_results)


def _truncate(val, maxlen=80):
    s = str(val)
    if len(s) > maxlen:
        return s[:maxlen] + "..."
    return s


def _safe_get(data, *keys):
    """Navigate nested dict safely."""
    curr = data
    for k in keys:
        if isinstance(curr, dict):
            curr = curr.get(k)
        else:
            return None
    return curr


def _check_convergences(orig, mut, orig_r, mut_r):
    checks = []

    # 1. Root 8 dominant in Semitic scripts → abjad root
    o_abjad = _safe_get(orig_r.get("abjad_kabir", {}), "data", "root")
    m_abjad = _safe_get(mut_r.get("abjad_kabir", {}), "data", "root")
    checks.append(("Root 8 Semitic (abjad_kabir root)", o_abjad, m_abjad))

    # 2. Mercury governance → dominant planet
    o_merc = _safe_get(orig_r.get("planetary_ruler_consensus", {}), "data", "dominant_planet")
    m_merc = _safe_get(mut_r.get("planetary_ruler_consensus", {}), "data", "dominant_planet")
    checks.append(("Mercury governance (planetary_ruler_consensus)", o_merc, m_merc))

    # 3. Air element dominant → element consensus
    o_elem = _safe_get(orig_r.get("element_consensus", {}), "data", "dominant_element")
    m_elem = _safe_get(mut_r.get("element_consensus", {}), "data", "dominant_element")
    checks.append(("Element dominant (element_consensus)", o_elem, m_elem))

    # 4. Teacher archetype → archetype consensus
    o_arch = _safe_get(orig_r.get("archetype_consensus", {}), "data", "dominant_archetype")
    m_arch = _safe_get(mut_r.get("archetype_consensus", {}), "data", "dominant_archetype")
    checks.append(("Archetype (archetype_consensus)", o_arch, m_arch))

    # 5. Missing digit 7 → subconscious_self
    o_miss = _safe_get(orig_r.get("subconscious_self", {}), "data", "missing_numbers")
    m_miss = _safe_get(mut_r.get("subconscious_self", {}), "data", "missing_numbers")
    if o_miss is None:
        o_miss = _safe_get(orig_r.get("inclusion_table", {}), "data", "missing_digits")
    if m_miss is None:
        m_miss = _safe_get(mut_r.get("inclusion_table", {}), "data", "missing_digits")
    checks.append(("Missing digit 7 (inclusion_table)", o_miss, m_miss))

    # 6. Barzakh score
    o_barz = _safe_get(orig_r.get("barzakh_coefficient", {}), "data", "barzakh_index")
    m_barz = _safe_get(mut_r.get("barzakh_coefficient", {}), "data", "barzakh_index")
    if o_barz is None:
        o_barz = _safe_get(orig_r.get("barzakh_coefficient", {}), "data", "barzakh_coefficient")
    if m_barz is None:
        m_barz = _safe_get(mut_r.get("barzakh_coefficient", {}), "data", "barzakh_coefficient")
    checks.append(("Barzakh score", o_barz, m_barz))

    # 7. Enneagram Type 3
    o_enn = _safe_get(orig_r.get("enneagram_dob", {}), "data", "type")
    m_enn = _safe_get(mut_r.get("enneagram_dob", {}), "data", "type")
    checks.append(("Enneagram type (enneagram_dob)", o_enn, m_enn))

    # 8. Part of Fortune
    o_pof = _safe_get(orig_r.get("arabic_parts", {}), "data", "part_of_fortune")
    m_pof = _safe_get(mut_r.get("arabic_parts", {}), "data", "part_of_fortune")
    checks.append(("Part of Fortune (arabic_parts)", o_pof, m_pof))

    # 9. Ascendant sign
    o_asc = _safe_get(orig_r.get("natal_chart", {}), "data", "ascendant")
    m_asc = _safe_get(mut_r.get("natal_chart", {}), "data", "ascendant")
    checks.append(("Ascendant (natal_chart)", o_asc, m_asc))

    # 10. Zi Wei Life Palace
    o_zw = _safe_get(orig_r.get("zi_wei_dou_shu", {}), "data", "life_palace")
    m_zw = _safe_get(mut_r.get("zi_wei_dou_shu", {}), "data", "life_palace")
    if o_zw is None:
        o_zw = _safe_get(orig_r.get("zi_wei_dou_shu", {}), "data", "命宮")
    if m_zw is None:
        m_zw = _safe_get(mut_r.get("zi_wei_dou_shu", {}), "data", "命宮")
    checks.append(("Zi Wei Life Palace", o_zw, m_zw))

    for i, (label, o_val, m_val) in enumerate(checks, 1):
        if o_val == m_val:
            print(f"  {i}. {label}: SAME ({_truncate(o_val, 60)})")
        else:
            print(f"  {i}. {label}: CHANGED ({_truncate(o_val, 40)} → {_truncate(m_val, 40)})")


def _check_ascendant(orig_r, mut_r):
    o_asc = _safe_get(orig_r.get("natal_chart", {}), "data", "ascendant")
    m_asc = _safe_get(mut_r.get("natal_chart", {}), "data", "ascendant")
    o_asc_deg = _safe_get(orig_r.get("natal_chart", {}), "data", "ascendant_degree")
    m_asc_deg = _safe_get(mut_r.get("natal_chart", {}), "data", "ascendant_degree")

    print(f"  Original: {o_asc} {o_asc_deg}")
    print(f"  Mutated:  {m_asc} {m_asc_deg}")

    o_sign = o_asc if isinstance(o_asc, str) else str(o_asc)
    m_sign = m_asc if isinstance(m_asc, str) else str(m_asc)
    print(f"  Sign change: {'YES' if o_sign != m_sign else 'NO'}")


if __name__ == "__main__":
    main()
