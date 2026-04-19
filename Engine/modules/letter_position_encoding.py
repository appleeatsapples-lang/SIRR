"""Letter Position Encoding — Positional Weight Analysis — COMPUTED_STRICT
Each letter's position in the full name matters: position × abjad value
gives a positional weight. The center of gravity reveals where the name's
numerical mass concentrates.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")

    positions = []
    total_weight = 0
    total_value = 0
    peak_pos = 0
    peak_weight = 0

    for i, ch in enumerate(name):
        if ch in abjad:
            val = abjad[ch]
            pos = i + 1  # 1-indexed
            weight = pos * val
            positions.append({"position": pos, "letter": ch, "value": val, "weight": weight})
            total_weight += weight
            total_value += val
            if weight > peak_weight:
                peak_weight = weight
                peak_pos = pos

    n = len(positions)

    # Center of gravity (weighted average position)
    if total_value > 0:
        center_of_gravity = round(sum(p["weight"] for p in positions) / total_value, 2)
    else:
        center_of_gravity = 0.0

    # Midpoint of name
    midpoint = n / 2

    # Skew: center_of_gravity relative to midpoint
    # >0 means mass is toward the end, <0 toward the beginning
    skew = round(center_of_gravity - midpoint, 2)

    # Total positional weight root
    weight_root = reduce_number(total_weight, keep_masters=())

    return SystemResult(
        id="letter_position_encoding",
        name="Letter Position Encoding (ترميز المواقع)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "total_letters": n,
            "total_weight": total_weight,
            "weight_root": weight_root,
            "center_of_gravity": center_of_gravity,
            "midpoint": midpoint,
            "skew": skew,
            "peak_position": peak_pos,
            "peak_weight": peak_weight,
            "peak_letter": positions[peak_pos - 1]["letter"] if peak_pos > 0 and peak_pos <= len(positions) else "",
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Positional abjad weighting — position × value per letter"],
        question="Q1_IDENTITY"
    )
