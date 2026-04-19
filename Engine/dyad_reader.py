"""
SIRR Dyad Reader — Cross-Tradition Dyad Analysis
Compares two already-computed SIRR output JSON files and produces a structured
dyad analysis. No new compute modules. Reads existing output only.

Usage:
    python dyad_reader.py \
      --profile-a output.json \
      --profile-b output_gen2_mazen_maternal.json \
      --label-a "ProfileA" \
      --label-b "Mazen" \
      --relationship "uncle_maternal" \
      --output output_dyad_AB.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Import convergence field map and independence groups from synthesis ──
from modules.synthesis import CONVERGENCE_FIELDS, SYSTEM_TO_GROUP

LOCKABLE = {"COMPUTED_STRICT", "LOOKUP_FIXED"}

# ── Five Element cycle for BaZi Ten God computation ──
ELEMENT_CYCLE = ["Wood", "Fire", "Earth", "Metal", "Water"]
PRODUCING = {
    "Metal": "Water", "Water": "Wood", "Wood": "Fire",
    "Fire": "Earth", "Earth": "Metal",
}
CONTROLLING = {
    "Metal": "Wood", "Wood": "Earth", "Earth": "Water",
    "Water": "Fire", "Fire": "Metal",
}

# Calendar modules to compare for shared markers
CALENDAR_MODULES = [
    ("ogham", "primary_tree"),
    ("tibetan_mewa", "mewa_number"),
    ("nine_star_ki", "year_star"),
    ("egyptian_decan", "decan_number"),
    ("zoroastrian_day_yazata", "roj_number"),
]


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _load_output(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _result_map(output: dict) -> Dict[str, dict]:
    """Map module_id → result dict."""
    return {r["id"]: r for r in output.get("results", [])}


def _get_data(result_map: dict, module_id: str) -> Optional[dict]:
    r = result_map.get(module_id)
    return r["data"] if r else None


def _get_certainty(result_map: dict, module_id: str) -> Optional[str]:
    r = result_map.get(module_id)
    return r["certainty"] if r else None


def _extract_convergence_values(data: dict, fields: set) -> List[int]:
    """Extract integer values from whitelisted fields."""
    if fields is None:
        # Use all fields (legacy behavior)
        fields = set(data.keys())
    vals = []
    for key in fields:
        v = data.get(key)
        if isinstance(v, int) and 1 <= v <= 33:
            vals.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, int) and 1 <= item <= 33:
                    vals.append(item)
    return vals


# ═══════════════════════════════════════════════════════════════════════════
# Section A: Cross-Tradition Matches
# ═══════════════════════════════════════════════════════════════════════════

def compute_cross_tradition_matches(
    map_a: dict, map_b: dict
) -> Tuple[List[dict], List[dict], int, float]:
    """Compare convergence-eligible values per module between two profiles."""
    matches = []
    non_matches = []

    common_ids = set(map_a.keys()) & set(map_b.keys())

    for mid in sorted(common_ids):
        cert_a = _get_certainty(map_a, mid)
        cert_b = _get_certainty(map_b, mid)
        if cert_a not in LOCKABLE or cert_b not in LOCKABLE:
            continue

        fields = CONVERGENCE_FIELDS.get(mid)
        if fields is not None and len(fields) == 0:
            continue  # explicitly excluded

        data_a = _get_data(map_a, mid)
        data_b = _get_data(map_b, mid)
        if not data_a or not data_b:
            continue

        vals_a = set(_extract_convergence_values(data_a, fields))
        vals_b = set(_extract_convergence_values(data_b, fields))

        if not vals_a or not vals_b:
            continue

        shared = vals_a & vals_b
        group = SYSTEM_TO_GROUP.get(mid, "unknown")

        entry = {
            "module_id": mid,
            "values_a": sorted(vals_a),
            "values_b": sorted(vals_b),
            "shared_values": sorted(shared),
            "match": len(shared) > 0,
            "independence_group": group,
        }

        if shared:
            matches.append(entry)
        else:
            non_matches.append(entry)

    total = len(matches) + len(non_matches)
    rate = round(len(matches) / total, 4) if total > 0 else 0.0

    return matches, non_matches, len(matches), rate


# ═══════════════════════════════════════════════════════════════════════════
# Section B: Independence-Grouped Matches
# ═══════════════════════════════════════════════════════════════════════════

def compute_independence_grouped(matches: List[dict]) -> dict:
    """Group matches by independence group. Report shared values across groups."""
    groups: Dict[str, List[dict]] = {}
    for m in matches:
        g = m["independence_group"]
        groups.setdefault(g, []).append(m)

    # Find values that appear in ≥2 groups
    value_to_groups: Dict[int, set] = {}
    for m in matches:
        for v in m["shared_values"]:
            value_to_groups.setdefault(v, set()).add(m["independence_group"])

    cross_group_values = {
        v: sorted(gs) for v, gs in value_to_groups.items() if len(gs) >= 2
    }

    return {
        "groups": {g: [m["module_id"] for m in ms] for g, ms in sorted(groups.items())},
        "group_count": len(groups),
        "cross_group_values": cross_group_values,
        "cross_group_count": len(cross_group_values),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Section C: BaZi Ten God Relationship
# ═══════════════════════════════════════════════════════════════════════════

def _ten_god_relationship(
    el_a: str, pol_a: str, el_b: str, pol_b: str
) -> Tuple[str, str, str]:
    """Compute Ten God from A's perspective toward B.
    Returns (ten_god_chinese, ten_god_english, dynamic_description)."""
    same_polarity = pol_a == pol_b

    if el_a == el_b:
        if same_polarity:
            return "比肩", "Companion (Bi Jian)", f"Same element {el_a}, same polarity"
        else:
            return "劫财", "Rob Wealth (Jie Cai)", f"Same element {el_a}, different polarity"

    # A produces B?
    if PRODUCING.get(el_a) == el_b:
        if same_polarity:
            return "食神", "Eating God (Shi Shen)", f"{el_a} produces {el_b}, same polarity"
        else:
            return "伤官", "Hurting Officer (Shang Guan)", f"{el_a} produces {el_b}, different polarity"

    # B produces A?
    if PRODUCING.get(el_b) == el_a:
        if same_polarity:
            return "偏印", "Indirect Resource (Pian Yin)", f"{el_b} produces {el_a}, same polarity"
        else:
            return "正印", "Direct Resource (Zheng Yin)", f"{el_b} produces {el_a}, different polarity"

    # A controls B?
    if CONTROLLING.get(el_a) == el_b:
        if same_polarity:
            return "偏财", "Indirect Wealth (Pian Cai)", f"{el_a} controls {el_b}, same polarity"
        else:
            return "正财", "Direct Wealth (Zheng Cai)", f"{el_a} controls {el_b}, different polarity"

    # B controls A?
    if CONTROLLING.get(el_b) == el_a:
        if same_polarity:
            return "七杀", "Seven Killings (Qi Sha)", f"{el_b} controls {el_a}, same polarity"
        else:
            return "正官", "Direct Officer (Zheng Guan)", f"{el_b} controls {el_a}, different polarity"

    return "?", "Unknown", f"{el_a} ↔ {el_b}"


def compute_bazi_ten_gods(map_a: dict, map_b: dict) -> dict:
    """Compute Ten God relationship between two Day Masters."""
    pil_a = _get_data(map_a, "bazi_pillars") or {}
    pil_b = _get_data(map_b, "bazi_pillars") or {}

    dp_a = pil_a.get("day_pillar", {})
    dp_b = pil_b.get("day_pillar", {})

    el_a = dp_a.get("stem_element", "")
    pol_a = dp_a.get("stem_polarity", "")
    stem_a = dp_a.get("stem_pinyin", "")

    el_b = dp_b.get("stem_element", "")
    pol_b = dp_b.get("stem_polarity", "")
    stem_b = dp_b.get("stem_pinyin", "")

    if not el_a or not el_b:
        return {"error": "Missing BaZi Day Master data"}

    tg_ab_cn, tg_ab_en, dyn_ab = _ten_god_relationship(el_a, pol_a, el_b, pol_b)
    tg_ba_cn, tg_ba_en, dyn_ba = _ten_god_relationship(el_b, pol_b, el_a, pol_a)

    return {
        "a_day_master": f"{stem_a} ({dp_a.get('stem', '')}) {pol_a} {el_a}",
        "b_day_master": f"{stem_b} ({dp_b.get('stem', '')}) {pol_b} {el_b}",
        "a_to_b": {
            "ten_god": tg_ab_cn,
            "ten_god_english": tg_ab_en,
            "dynamic": dyn_ab,
        },
        "b_to_a": {
            "ten_god": tg_ba_cn,
            "ten_god_english": tg_ba_en,
            "dynamic": dyn_ba,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# Section D: Convergence Overlap
# ═══════════════════════════════════════════════════════════════════════════

def compute_convergence_overlap(synth_a: dict, synth_b: dict) -> List[dict]:
    """Find numbers that appear as TIER_1 in both profiles' synthesis."""
    nc_a = {
        c["number"]: c for c in synth_a.get("number_convergences", [])
        if c.get("tier", "").startswith("TIER_1")
    }
    nc_b = {
        c["number"]: c for c in synth_b.get("number_convergences", [])
        if c.get("tier", "").startswith("TIER_1")
    }

    shared = sorted(set(nc_a.keys()) & set(nc_b.keys()))
    result = []
    for num in shared:
        result.append({
            "number": num,
            "a_system_count": nc_a[num].get("system_count", 0),
            "a_tier": nc_a[num].get("tier", ""),
            "b_system_count": nc_b[num].get("system_count", 0),
            "b_tier": nc_b[num].get("tier", ""),
            "combined_systems": nc_a[num].get("system_count", 0) + nc_b[num].get("system_count", 0),
        })
    return result


# ═══════════════════════════════════════════════════════════════════════════
# Section E: Dominant Element Match
# ═══════════════════════════════════════════════════════════════════════════

def compute_element_match(synth_a: dict, synth_b: dict) -> dict:
    """Check if both profiles share a dominant element."""
    ec_a = synth_a.get("element_convergences", [])
    ec_b = synth_b.get("element_convergences", [])

    dom_a = ec_a[0] if ec_a else {}
    dom_b = ec_b[0] if ec_b else {}

    el_a = dom_a.get("element", "")
    el_b = dom_b.get("element", "")

    return {
        "a_dominant_element": el_a,
        "a_system_count": dom_a.get("system_count", 0),
        "b_dominant_element": el_b,
        "b_system_count": dom_b.get("system_count", 0),
        "match": el_a == el_b and el_a != "",
    }


# ═══════════════════════════════════════════════════════════════════════════
# Section F: Timing Sync (2026)
# ═══════════════════════════════════════════════════════════════════════════

def compute_timing_sync(map_a: dict, map_b: dict) -> dict:
    """Compare current timing cycles for both profiles."""
    py_a = _get_data(map_a, "personal_year") or {}
    py_b = _get_data(map_b, "personal_year") or {}

    vim_a = _get_data(map_a, "vimshottari") or {}
    vim_b = _get_data(map_b, "vimshottari") or {}

    lp_a = _get_data(map_a, "bazi_luck_pillars") or {}
    lp_b = _get_data(map_b, "bazi_luck_pillars") or {}

    py_match = py_a.get("personal_year") == py_b.get("personal_year")

    return {
        "personal_year": {
            "a": py_a.get("personal_year"),
            "b": py_b.get("personal_year"),
            "match": py_match,
        },
        "vimshottari_mahadasha": {
            "a": vim_a.get("current_maha_dasha"),
            "b": vim_b.get("current_maha_dasha"),
        },
        "bazi_luck_pillar": {
            "a": lp_a.get("current_luck_pillar"),
            "b": lp_b.get("current_luck_pillar"),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# Section G: Shared Calendar Markers
# ═══════════════════════════════════════════════════════════════════════════

def compute_shared_calendar(map_a: dict, map_b: dict) -> List[dict]:
    """Check which calendar modules return the same value for both people."""
    shared = []
    for mid, key in CALENDAR_MODULES:
        data_a = _get_data(map_a, mid) or {}
        data_b = _get_data(map_b, mid) or {}
        val_a = data_a.get(key)
        val_b = data_b.get(key)
        if val_a is not None and val_b is not None:
            entry = {
                "module": mid,
                "field": key,
                "a_value": val_a,
                "b_value": val_b,
                "match": val_a == val_b,
            }
            shared.append(entry)
    return shared


# ═══════════════════════════════════════════════════════════════════════════
# Section H: Relationship Archetype
# ═══════════════════════════════════════════════════════════════════════════

def compute_archetype(
    ten_gods: dict,
    matches: List[dict],
    match_count: int,
    match_rate: float,
    grouped: dict,
    convergence_overlap: List[dict],
    element_match: dict,
    shared_calendar: List[dict],
    relationship: str,
) -> dict:
    """Produce a structured relationship archetype summary."""
    shared_roots = [c["number"] for c in convergence_overlap]
    shared_cal_modules = [c["module"] for c in shared_calendar if c["match"]]

    return {
        "ten_god_a_to_b": f"{ten_gods.get('a_to_b', {}).get('ten_god', '')} {ten_gods.get('a_to_b', {}).get('ten_god_english', '')}",
        "ten_god_b_to_a": f"{ten_gods.get('b_to_a', {}).get('ten_god', '')} {ten_gods.get('b_to_a', {}).get('ten_god_english', '')}",
        "shared_roots": shared_roots,
        "shared_calendar_modules": shared_cal_modules,
        "dominant_element_match": element_match.get("match", False),
        "match_count": match_count,
        "match_rate": match_rate,
        "independence_groups_matched": grouped.get("group_count", 0),
        "cross_group_value_count": grouped.get("cross_group_count", 0),
        "relationship_type": relationship,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def run_dyad(
    path_a: str, path_b: str,
    label_a: str, label_b: str,
    relationship: str,
    output_path: str,
) -> dict:
    """Run the full dyad analysis and write output JSON."""
    out_a = _load_output(path_a)
    out_b = _load_output(path_b)

    map_a = _result_map(out_a)
    map_b = _result_map(out_b)

    synth_a = out_a.get("synthesis", {})
    synth_b = out_b.get("synthesis", {})

    # A. Cross-tradition matches
    matches, non_matches, match_count, match_rate = compute_cross_tradition_matches(map_a, map_b)

    # B. Independence-grouped matches
    grouped = compute_independence_grouped(matches)

    # C. BaZi Ten Gods
    ten_gods = compute_bazi_ten_gods(map_a, map_b)

    # D. Convergence overlap
    convergence_overlap = compute_convergence_overlap(synth_a, synth_b)

    # E. Dominant element
    element_match = compute_element_match(synth_a, synth_b)

    # F. Timing sync
    timing = compute_timing_sync(map_a, map_b)

    # G. Shared calendar markers
    shared_calendar = compute_shared_calendar(map_a, map_b)

    # H. Relationship archetype
    archetype = compute_archetype(
        ten_gods, matches, match_count, match_rate,
        grouped, convergence_overlap, element_match,
        shared_calendar, relationship,
    )

    result = {
        "dyad": {
            "profile_a": {
                "label": label_a,
                "file": path_a,
                "subject": out_a.get("profile", {}).get("subject", ""),
            },
            "profile_b": {
                "label": label_b,
                "file": path_b,
                "subject": out_b.get("profile", {}).get("subject", ""),
            },
            "relationship": relationship,
        },
        "cross_tradition_matches": matches,
        "cross_tradition_non_matches": non_matches,
        "match_summary": {
            "match_count": match_count,
            "total_compared": match_count + len(non_matches),
            "match_rate": match_rate,
        },
        "independence_grouped_matches": grouped,
        "bazi_ten_gods": ten_gods,
        "convergence_overlap": convergence_overlap,
        "dominant_element": element_match,
        "timing_2026": timing,
        "shared_calendar_markers": shared_calendar,
        "relationship_archetype": archetype,
    }

    Path(output_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    # Terminal summary
    print(f"\n  SIRR Dyad Analysis: {label_a} × {label_b}")
    print(f"  Relationship: {relationship}")
    print(f"  Cross-tradition matches: {match_count}/{match_count + len(non_matches)} ({match_rate:.1%})")
    print(f"  Independence groups matched: {grouped['group_count']}")
    print(f"  Cross-group values: {grouped['cross_group_count']}")
    print(f"  BaZi: {label_a}→{label_b} = {ten_gods.get('a_to_b', {}).get('ten_god', '?')} | {label_b}→{label_a} = {ten_gods.get('b_to_a', {}).get('ten_god', '?')}")
    print(f"  Shared TIER_1 roots: {[c['number'] for c in convergence_overlap]}")
    print(f"  Element match: {element_match.get('match', False)} ({element_match.get('a_dominant_element', '?')} vs {element_match.get('b_dominant_element', '?')})")
    cal_matches = [c["module"] for c in shared_calendar if c["match"]]
    print(f"  Calendar matches: {cal_matches}")
    print(f"\n  Output: {output_path}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIRR Dyad Reader")
    parser.add_argument("--profile-a", required=True, help="Path to profile A output JSON")
    parser.add_argument("--profile-b", required=True, help="Path to profile B output JSON")
    parser.add_argument("--label-a", default="A", help="Label for profile A")
    parser.add_argument("--label-b", default="B", help="Label for profile B")
    parser.add_argument("--relationship", default="unknown", help="Relationship type")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    run_dyad(
        args.profile_a, args.profile_b,
        args.label_a, args.label_b,
        args.relationship, args.output,
    )
