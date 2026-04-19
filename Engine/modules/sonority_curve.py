"""Sonority Curve — Phonetic Prominence Profile — COMPUTED_STRICT
Assigns a sonority value to each letter (vowel > approximant > nasal >
fricative > stop) and plots the curve shape across the name.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Sonority scale (higher = more sonorous)
# Based on universal sonority hierarchy adapted for Arabic
SONORITY = {
    # Vowels / long vowels (sonority 5)
    "ا": 5, "و": 5, "ي": 5,
    # Approximants / glides (sonority 4)
    "ل": 4, "ر": 4,
    # Nasals (sonority 3)
    "م": 3, "ن": 3,
    # Fricatives (sonority 2)
    "ه": 2, "ع": 2, "ح": 2, "غ": 2, "خ": 2,
    "ف": 2, "ث": 2, "ذ": 2, "ظ": 2, "ز": 2,
    "س": 2, "ش": 2, "ص": 2, "ض": 2,
    # Stops / plosives (sonority 1)
    "ب": 1, "ت": 1, "د": 1, "ط": 1, "ك": 1,
    "ق": 1, "ج": 1,
    # Hamza variants
    "إ": 5, "أ": 5, "ؤ": 5, "ئ": 5,
}

SONORITY_LABELS = {1: "stop", 2: "fricative", 3: "nasal", 4: "approximant", 5: "vowel"}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    name = profile.arabic.replace(" ", "")
    curve = []
    for ch in name:
        if ch in SONORITY:
            curve.append({"letter": ch, "sonority": SONORITY[ch], "class": SONORITY_LABELS[SONORITY[ch]]})

    values = [c["sonority"] for c in curve]
    n = len(values)

    if n > 0:
        mean_sonority = round(sum(values) / n, 2)
        peak_sonority = max(values)
        trough_sonority = min(values)
    else:
        mean_sonority = 0
        peak_sonority = 0
        trough_sonority = 0

    # Count rises and falls (contour analysis)
    rises = sum(1 for i in range(n - 1) if values[i + 1] > values[i])
    falls = sum(1 for i in range(n - 1) if values[i + 1] < values[i])
    plateaus = sum(1 for i in range(n - 1) if values[i + 1] == values[i])

    # Contour shape
    if rises > falls:
        contour = "ascending"
    elif falls > rises:
        contour = "descending"
    else:
        contour = "balanced"

    # Sonority class distribution
    class_counts = {}
    for c in curve:
        cls = c["class"]
        class_counts[cls] = class_counts.get(cls, 0) + 1

    dominant_class = max(class_counts, key=class_counts.get) if class_counts else "unknown"

    return SystemResult(
        id="sonority_curve",
        name="Sonority Curve (منحنى الرنين)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "total_letters": n,
            "mean_sonority": mean_sonority,
            "peak_sonority": peak_sonority,
            "trough_sonority": trough_sonority,
            "rises": rises,
            "falls": falls,
            "plateaus": plateaus,
            "contour": contour,
            "class_distribution": class_counts,
            "dominant_class": dominant_class,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Universal Sonority Hierarchy adapted for Arabic phonology"],
        question="Q3_NATURE"
    )
