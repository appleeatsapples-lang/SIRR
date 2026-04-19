"""Name Weight — Syllabic Light/Heavy Analysis — APPROX
Classifies Arabic syllables as light (CV) or heavy (CVC/CVV) and computes
the weight ratio per word and full chain. Approximation because full
harakat (voweling) is not available from unvoweled text.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

# Long vowels / mater lectionis in Arabic script
LONG_VOWELS = set("اوي")
# Letters that typically close a syllable when word-final or before consonant
# In unvoweled text, we approximate by counting consonant clusters

def _estimate_weight(word: str) -> dict:
    """Estimate syllable weight from unvoweled Arabic text.

    Heuristic: long vowels (ا و ي) create heavy syllables.
    Consonant clusters (two non-vowel letters adjacent) suggest closed syllables.
    This is an approximation — true analysis requires tashkeel.
    """
    letters = [ch for ch in word if '\u0621' <= ch <= '\u064A' or ch in 'إأؤئ']
    n = len(letters)
    if n == 0:
        return {"light": 0, "heavy": 0, "total": 0}

    heavy = 0
    light = 0

    for i, ch in enumerate(letters):
        if ch in LONG_VOWELS:
            heavy += 1
        else:
            # Check if next letter is also a consonant (cluster = heavy)
            if i + 1 < n and letters[i + 1] not in LONG_VOWELS:
                heavy += 1
            else:
                light += 1

    return {"light": light, "heavy": heavy, "total": light + heavy}


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    words = profile.arabic.split()
    word_weights = []
    total_light = 0
    total_heavy = 0

    for w in words:
        wt = _estimate_weight(w)
        word_weights.append({
            "word": w,
            "light": wt["light"],
            "heavy": wt["heavy"],
            "total": wt["total"],
            "heavy_ratio": round(wt["heavy"] / wt["total"] * 100, 1) if wt["total"] > 0 else 0,
        })
        total_light += wt["light"]
        total_heavy += wt["heavy"]

    total = total_light + total_heavy
    overall_heavy_ratio = round(total_heavy / total * 100, 1) if total > 0 else 0

    # Cadence: classify the weight pattern
    if overall_heavy_ratio >= 70:
        cadence = "heavy"
    elif overall_heavy_ratio <= 30:
        cadence = "light"
    else:
        cadence = "mixed"

    return SystemResult(
        id="name_weight",
        name="Name Weight (ثقل الاسم)",
        certainty="APPROX",
        data={
            "module_class": "primary",
            "total_syllables": total,
            "total_light": total_light,
            "total_heavy": total_heavy,
            "heavy_ratio": overall_heavy_ratio,
            "cadence": cadence,
            "word_weights": word_weights,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Arabic prosody — light (CV) vs heavy (CVC/CVV) syllable classification", "Approximation: tashkeel-free heuristic"],
        question="Q3_NATURE"
    )
