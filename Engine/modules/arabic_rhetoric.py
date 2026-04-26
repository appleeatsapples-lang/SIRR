"""Arabic Rhetoric — Badi' Pattern Detection — COMPUTED_STRICT
Detects rhetorical figures in the full Arabic name:
- صدى نسبي (genealogical echo): same word at different generational positions
  in the nasab chain (e.g., a single given-name appearing both as the father
  and as the first element of a later compound name). NOT جناس تام —
  genealogical repetition, not wordplay.
- تكرار (repetition): repeated letters, bigrams, roots
- طباق (antithesis): active/passive voice contrast within the name
"""
from __future__ import annotations
from collections import Counter
from sirr_core.types import InputProfile, SystemResult

# Generational labels for nasab positions (8-word chain)
_GENERATION_LABELS = [
    "subject",           # 0: first name
    "father",            # 1
    "grandfather",       # 2
    "great_grandfather", # 3 (first element of compound name when present)
    "great_grandfather", # 4 (second element of compound name when present)
    "great_great_gf",    # 5 (first element of compound name when present)
    "great_great_gf",    # 6 (second element of compound name when present)
    "nisba",             # 7 (family attribution)
]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    words = profile.arabic.split()
    name = profile.arabic.replace(" ", "")

    # 1. Genealogical echo detection (صدى نسبي)
    # Same word at different positions = cross-generational echo, NOT جناس تام
    word_positions = {}
    for i, w in enumerate(words):
        word_positions.setdefault(w, []).append(i)
    repeated_words = {w: pos for w, pos in word_positions.items() if len(pos) > 1}

    genealogical_echoes = []
    for word, positions in repeated_words.items():
        labels = []
        for p in positions:
            if p < len(_GENERATION_LABELS):
                labels.append(_GENERATION_LABELS[p])
            else:
                labels.append(f"position_{p}")
        genealogical_echoes.append({
            "word": word,
            "positions": positions,
            "generations": labels,
            "type": "genealogical_echo",
            "note": "Same name across generations — nasab repetition, not rhetorical jinas tam",
        })
    has_genealogical_echo = len(genealogical_echoes) > 0

    # 2. Letter repetition analysis
    letter_counts = Counter(ch for ch in name if '\u0621' <= ch <= '\u064A' or ch in 'إأؤئ')
    most_common_letter = letter_counts.most_common(1)[0] if letter_counts else ("", 0)
    repeated_letters = {ch: count for ch, count in letter_counts.items() if count > 2}

    # 3. Bigram repetition (consecutive letter pairs)
    bigrams = [name[i:i+2] for i in range(len(name) - 1)]
    bigram_counts = Counter(bigrams)
    repeated_bigrams = {bg: count for bg, count in bigram_counts.items() if count > 1}

    # 4. Consonant alliteration: words starting with the same letter
    initials = [w[0] for w in words if w]
    initial_counts = Counter(initials)
    alliterating_groups = {ch: count for ch, count in initial_counts.items() if count > 1}

    # 5. طباق — antithesis detection (active vs passive voice in name)
    import json
    from pathlib import Path
    morph_path = Path(__file__).resolve().parent.parent / "data" / "arabic_linguistics_tables.json"
    try:
        tables = json.loads(morph_path.read_text(encoding="utf-8"))
        morph = tables.get("name_morphology", {})
        voices = []
        for w in words:
            entry = morph.get(w, {})
            v = entry.get("voice", "n/a")
            if v in ("active", "passive"):
                voices.append(v)
        has_tibaq = "active" in voices and "passive" in voices
    except Exception:
        has_tibaq = False
        voices = []

    # 6. Internal echo: shared ending patterns (sajʿ-like)
    endings = [w[-2:] if len(w) >= 2 else w for w in words]
    ending_counts = Counter(endings)
    rhyming_endings = {end: count for end, count in ending_counts.items() if count > 1}

    return SystemResult(
        id="arabic_rhetoric",
        name="Arabic Rhetoric (علم البديع)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "word_count": len(words),
            "genealogical_echoes": genealogical_echoes,
            "has_genealogical_echo": has_genealogical_echo,
            "has_jinas_tam": False,
            "most_common_letter": most_common_letter[0],
            "most_common_letter_count": most_common_letter[1],
            "repeated_letters": repeated_letters,
            "repeated_bigrams": repeated_bigrams,
            "alliterating_groups": alliterating_groups,
            "has_tibaq": has_tibaq,
            "voice_sequence": voices,
            "rhyming_endings": rhyming_endings,
            "total_repetition_score": len(genealogical_echoes) + len(repeated_bigrams) + len(alliterating_groups),
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Ilm al-Badi' — Arabic rhetorical figures",
            "صدى نسبي: genealogical echo (same name across generations)",
            "طباق: antithetical voice contrast (active vs passive)",
        ],
        question="Q1_IDENTITY"
    )
