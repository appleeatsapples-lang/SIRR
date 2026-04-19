"""Abjad Visual Architecture — COMPUTED_STRICT
Extends calligraphy_structure with derived metrics: total dot count,
void-space frequency (dotless letters), baseline interruptions (ascender/descender ratio).
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from modules.calligraphy_structure import LETTER_VISUAL


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in LETTER_VISUAL]
    total = len(letters)

    # Dot analysis
    dotted_letters = sum(1 for ch in letters if LETTER_VISUAL[ch]["dots_above"] + LETTER_VISUAL[ch]["dots_below"] > 0)
    undotted_letters = total - dotted_letters
    total_dots = sum(LETTER_VISUAL[ch]["dots_above"] + LETTER_VISUAL[ch]["dots_below"] for ch in letters)

    # Void space: undotted ratio (letters that have no dots = "void" in the dot plane)
    void_ratio = round(undotted_letters / total * 100, 1) if total > 0 else 0

    # Baseline interruptions: how many letters break the baseline (ascend or descend)
    ascenders = sum(1 for ch in letters if LETTER_VISUAL[ch]["ascender"])
    descenders = sum(1 for ch in letters if LETTER_VISUAL[ch]["descender"])
    interruptions = ascenders + descenders
    interruption_ratio = round(interruptions / total * 100, 1) if total > 0 else 0

    # Visual density: dots per interruption (how much decoration per vertical movement)
    dots_per_interruption = round(total_dots / interruptions, 2) if interruptions > 0 else 0

    # Vertical symmetry: ascender-descender balance
    if ascenders + descenders > 0:
        vertical_balance = round((ascenders - descenders) / (ascenders + descenders), 3)
    else:
        vertical_balance = 0.0
    # -1 = all descenders, +1 = all ascenders, 0 = balanced

    # Per-word dot counts
    words = profile.arabic.split()
    word_dots = []
    for w in words:
        d = sum(LETTER_VISUAL.get(ch, {}).get("dots_above", 0) + LETTER_VISUAL.get(ch, {}).get("dots_below", 0)
                for ch in w)
        word_dots.append({"word": w, "dots": d})

    return SystemResult(
        id="abjad_visual_architecture",
        name="Abjad Visual Architecture (العمارة البصرية)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "total_letters": total,
            "dotted_letters": dotted_letters,
            "undotted_letters": undotted_letters,
            "total_dots": total_dots,
            "void_ratio": void_ratio,
            "interruptions": interruptions,
            "interruption_ratio": interruption_ratio,
            "dots_per_interruption": dots_per_interruption,
            "vertical_balance": vertical_balance,
            "word_dots": word_dots,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Calligraphic architecture — dot/void/interruption analysis"],
        question="Q1_IDENTITY"
    )
