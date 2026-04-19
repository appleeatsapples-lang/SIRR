"""Calligraphy Structure — Visual Letter Architecture — COMPUTED_STRICT
Classifies each Arabic letter by visual properties: ascenders, descenders,
dots above/below, tooth letters, loops, joined density.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Visual classification of Arabic letters (standard Naskh)
# Properties: ascender, descender, dots_above, dots_below, tooth, loop, baseline
LETTER_VISUAL = {
    "ا": {"ascender": True, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": False},
    "ب": {"ascender": False, "descender": False, "dots_above": 0, "dots_below": 1, "tooth": True, "loop": False},
    "ت": {"ascender": False, "descender": False, "dots_above": 2, "dots_below": 0, "tooth": True, "loop": False},
    "ث": {"ascender": False, "descender": False, "dots_above": 3, "dots_below": 0, "tooth": True, "loop": False},
    "ج": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 1, "tooth": False, "loop": True},
    "ح": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "خ": {"ascender": False, "descender": True, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "د": {"ascender": False, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": False},
    "ذ": {"ascender": False, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": False},
    "ر": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": False},
    "ز": {"ascender": False, "descender": True, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": False},
    "س": {"ascender": False, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": True, "loop": False},
    "ش": {"ascender": False, "descender": False, "dots_above": 3, "dots_below": 0, "tooth": True, "loop": False},
    "ص": {"ascender": False, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "ض": {"ascender": False, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "ط": {"ascender": True, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "ظ": {"ascender": True, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "ع": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "غ": {"ascender": False, "descender": True, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "ف": {"ascender": False, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "ق": {"ascender": False, "descender": True, "dots_above": 2, "dots_below": 0, "tooth": False, "loop": True},
    "ك": {"ascender": True, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": False},
    "ل": {"ascender": True, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": False},
    "م": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "ن": {"ascender": False, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": True, "loop": False},
    "ه": {"ascender": False, "descender": False, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "و": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 0, "tooth": False, "loop": True},
    "ي": {"ascender": False, "descender": True, "dots_above": 0, "dots_below": 2, "tooth": True, "loop": False},
    # hamza/alef variants
    "إ": {"ascender": True, "descender": False, "dots_above": 0, "dots_below": 1, "tooth": False, "loop": False},
    "أ": {"ascender": True, "descender": False, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": False},
    "ؤ": {"ascender": False, "descender": True, "dots_above": 1, "dots_below": 0, "tooth": False, "loop": True},
    "ئ": {"ascender": False, "descender": True, "dots_above": 1, "dots_below": 2, "tooth": True, "loop": False},
}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in LETTER_VISUAL]
    total = len(letters)

    ascenders = sum(1 for ch in letters if LETTER_VISUAL[ch]["ascender"])
    descenders = sum(1 for ch in letters if LETTER_VISUAL[ch]["descender"])
    dots_above = sum(LETTER_VISUAL[ch]["dots_above"] for ch in letters)
    dots_below = sum(LETTER_VISUAL[ch]["dots_below"] for ch in letters)
    total_dots = dots_above + dots_below
    teeth = sum(1 for ch in letters if LETTER_VISUAL[ch]["tooth"])
    loops = sum(1 for ch in letters if LETTER_VISUAL[ch]["loop"])
    baseline = total - ascenders - descenders  # letters on baseline only

    # Ratios
    ascender_ratio = round(ascenders / total * 100, 1) if total > 0 else 0
    descender_ratio = round(descenders / total * 100, 1) if total > 0 else 0
    dot_density = round(total_dots / total, 2) if total > 0 else 0
    tooth_ratio = round(teeth / total * 100, 1) if total > 0 else 0
    loop_ratio = round(loops / total * 100, 1) if total > 0 else 0

    # Dominant visual feature
    features = {"ascenders": ascenders, "descenders": descenders, "teeth": teeth, "loops": loops, "baseline": baseline}
    dominant_feature = max(features, key=features.get)

    return SystemResult(
        id="calligraphy_structure",
        name="Calligraphy Structure (هندسة الخط)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "total_letters": total,
            "ascenders": ascenders,
            "descenders": descenders,
            "ascender_ratio": ascender_ratio,
            "descender_ratio": descender_ratio,
            "dots_above": dots_above,
            "dots_below": dots_below,
            "total_dots": total_dots,
            "dot_density": dot_density,
            "teeth": teeth,
            "tooth_ratio": tooth_ratio,
            "loops": loops,
            "loop_ratio": loop_ratio,
            "baseline_letters": baseline,
            "dominant_feature": dominant_feature,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Naskh script visual analysis — ascender/descender/dot/tooth/loop classification"],
        question="Q1_IDENTITY"
    )
