"""Lineage Computation — Word-Level Abjad Sequence Analysis — COMPUTED_STRICT
Analyzes the sequence of per-word abjad sums across the nasab chain:
palindromic patterns, deltas, positional symmetry.

Also provides compound_groups: the 6-unit generational view where
configured compound names (see COMPOUND_POSITIONS below) are summed
as single units.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Positional compound detection (same as name_semantics)
COMPOUND_POSITIONS = {
    3: ("عمر", "عاكف"),    # great-grandfather
    5: ("محمد", "وصفي"),   # great-great-grandfather
}


def _group_compound_sums(words: list[str], abjad: dict) -> list[dict]:
    """Group words into generational units and sum compounds together."""
    groups = []
    i = 0
    while i < len(words):
        compound = COMPOUND_POSITIONS.get(i)
        if compound and i + 1 < len(words) and words[i] == compound[0] and words[i + 1] == compound[1]:
            s = sum(abjad.get(ch, 0) for ch in words[i]) + sum(abjad.get(ch, 0) for ch in words[i + 1])
            groups.append({
                "unit": f"{words[i]} {words[i + 1]}",
                "sum": s,
                "root": reduce_number(s, keep_masters=()),
                "is_compound": True,
            })
            i += 2
        else:
            s = sum(abjad.get(ch, 0) for ch in words[i])
            groups.append({
                "unit": words[i],
                "sum": s,
                "root": reduce_number(s, keep_masters=()),
                "is_compound": False,
            })
            i += 1
    return groups


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    words = profile.arabic.split()

    # Word-level (8-element) sequence — preserved for backward compatibility
    word_sums = []
    for w in words:
        s = sum(abjad.get(ch, 0) for ch in w)
        word_sums.append({"word": w, "sum": s, "root": reduce_number(s, keep_masters=())})

    sequence = [ws["sum"] for ws in word_sums]
    total = sum(sequence)
    n = len(sequence)

    # Compound groups (6-unit generational view)
    compound_units = _group_compound_sums(words, abjad)
    compound_groups = [u["sum"] for u in compound_units]

    # Palindromic detection: find repeated values at mirrored positions
    repeats = {}
    for i, v in enumerate(sequence):
        repeats.setdefault(v, []).append(i)
    palindromic_values = {str(v): positions for v, positions in repeats.items() if len(positions) > 1}

    # Delta sequence (consecutive differences)
    deltas = [sequence[i+1] - sequence[i] for i in range(n - 1)]

    # Center of weight (weighted average position)
    if total > 0:
        center_of_weight = round(sum(i * s for i, s in enumerate(sequence)) / total, 2)
    else:
        center_of_weight = 0.0

    # Max, min, range
    seq_max = max(sequence) if sequence else 0
    seq_min = min(sequence) if sequence else 0
    seq_range = seq_max - seq_min

    # Root sequence
    root_sequence = [ws["root"] for ws in word_sums]
    unique_roots = sorted(set(root_sequence))

    # Is the full sequence palindromic?
    is_sequence_palindrome = sequence == sequence[::-1]

    return SystemResult(
        id="lineage_computation",
        name="Lineage Computation (حساب النسب)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "word_count": n,
            "word_sums": word_sums,
            "sequence": sequence,
            "compound_groups": compound_groups,
            "compound_units": compound_units,
            "total": total,
            "deltas": deltas,
            "palindromic_values": palindromic_values,
            "is_sequence_palindrome": is_sequence_palindrome,
            "center_of_weight": center_of_weight,
            "max": seq_max,
            "min": seq_min,
            "range": seq_range,
            "root_sequence": root_sequence,
            "unique_roots": unique_roots,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Nasab word-level abjad sequence — structural lineage analysis"],
        question="Q1_IDENTITY"
    )
