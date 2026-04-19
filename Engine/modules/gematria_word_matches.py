"""
Gematria Word Matches (גימטריא שוה)
──────────────────────────────────────
Finds Hebrew words/phrases with identical gematria value to the subject's
Arabic-to-Hebrew transliterated name, using the Semitic bridge.

Algorithm:
  1. Transliterate Arabic name → Hebrew cognate letters
  2. Compute Mispar Gadol (standard gematria) total
  3. Search known biblical/liturgical word list for value matches
  4. Report exact matches and ±1 near-matches

Source: Sefer ha-Bahir; Baal HaTurim commentary method
SOURCE_TIER: B (respected secondary — classical gematria practice)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Arabic → Hebrew letter mapping (from kabbalah_solomonic_lookups.json bridge)
ARABIC_TO_HEBREW = {
    'ا': ('aleph', 1), 'أ': ('aleph', 1), 'إ': ('aleph', 1), 'آ': ('aleph', 1),
    'ب': ('bet', 2),
    'ج': ('gimel', 3),
    'د': ('dalet', 4),
    'ه': ('he', 5), 'ة': ('he', 5),
    'و': ('vav', 6),
    'ز': ('zayin', 7),
    'ح': ('chet', 8),
    'ط': ('tet', 9),
    'ي': ('yod', 10), 'ى': ('yod', 10),
    'ك': ('kaf', 20),
    'ل': ('lamed', 30),
    'م': ('mem', 40),
    'ن': ('nun', 50),
    'س': ('samekh', 60),
    'ع': ('ayin', 70),
    'ف': ('pe', 80),
    'ص': ('tzadi', 90),
    'ق': ('qof', 100),
    'ر': ('resh', 200),
    'ش': ('shin', 300),
    'ت': ('tav', 400),
    # Extended Arabic letters (no Hebrew cognate — map to closest)
    'ث': ('tav', 400),   # Tha → Tav
    'خ': ('chet', 8),    # Kha → Chet
    'ذ': ('zayin', 7),   # Dhal → Zayin
    'ض': ('tzadi', 90),  # Dad → Tzadi
    'ظ': ('tzadi', 90),  # Dha → Tzadi
    'غ': ('ayin', 70),   # Ghain → Ayin
}

# Notable Hebrew words/phrases with known gematria values
# Source: Baal HaTurim, Sefer ha-Bahir, classical references
KNOWN_WORDS = {
    1: ["אלף (Aleph — Unity)"],
    3: ["אב (Father)"],
    5: ["הא (The Divine Name letter)"],
    7: ["גד (Fortune)"],
    8: ["חי (Chai — Life)", "אהוה"],
    9: ["אט (Slowly — patience)"],
    10: ["יד (Hand)"],
    12: ["הוא (He/It)"],
    13: ["אחד (Echad — One)", "אהבה (Ahavah — Love)"],
    17: ["טוב (Tov — Good)"],
    18: ["חי (Chai — Life)"],
    22: ["יחד (Yachad — Together)"],
    26: ["יהוה (YHVH — Tetragrammaton)"],
    32: ["לב (Lev — Heart)"],
    36: ["אלהי (Elohai — My God)"],
    42: ["בלהה (Bilhah)"],
    44: ["דם (Dam — Blood)"],
    45: ["אדם (Adam — Human)", "מה (Mah — What)"],
    50: ["כל (Kol — All)"],
    52: ["בן (Ben — Son)", "אליהו (Eliyahu)"],
    58: ["חן (Chen — Grace)"],
    65: ["אדני (Adonai)"],
    68: ["חיים (Chayyim — Life/Lives)"],
    72: ["חסד (Chesed — Mercy)"],
    78: ["מזל (Mazal — Fortune)"],
    80: ["יסוד (Yesod — Foundation)"],
    86: ["אלהים (Elohim — God)", "הטבע (HaTeva — Nature)"],
    91: ["אמן (Amen)", "מלאך (Malakh — Angel)"],
    100: ["כף (Palm)", "קד (Bow)"],
    111: ["אלף (Aleph — spelled out)"],
    119: ["טבע (Teva — Nature)"],
    120: ["סמך (Samekh — Support)"],
    137: ["קבלה (Kabbalah — Reception)"],
    148: ["נצח (Netzach — Victory)"],
    176: ["עולם (Olam — World/Eternity)"],
    200: ["רוח (Ruach — Spirit)"],
    207: ["אור (Or — Light)", "אין סוף (Ein Sof — Infinite)"],
    216: ["גבורה (Gevurah — Strength)"],
    232: ["יראה (Yirah — Awe/Fear)"],
    248: ["רחם (Rechem — Womb)", "אברהם (Abraham)"],
    314: ["שדי (Shaddai — Almighty)"],
    345: ["משה (Moshe — Moses)", "השמ (HaShem)"],
    358: ["משיח (Mashiach — Messiah)", "נחש (Nachash — Serpent)"],
    370: ["שלם (Shalem — Whole/Complete)"],
    400: ["תו (Tav — Mark/Sign)"],
    410: ["שמע (Shema — Hear)"],
    434: ["דלת (Dalet — Door)"],
    441: ["אמת (Emet — Truth)"],
    474: ["דעת (Da'at — Knowledge)"],
    480: ["תלמוד (Talmud)"],
    500: ["שר (Sar — Prince)"],
    541: ["ישראל (Yisrael — Israel)"],
    546: ["אור הגנוז (Hidden Light)"],
    611: ["תורה (Torah)"],
    620: ["כתר (Keter — Crown)"],
    666: ["סתר (Soter — Secret/Hidden)"],
    708: ["חן חן (Grace upon Grace)"],
    770: ["בית משיח (House of Messiah)"],
    888: ["ישוע (Yeshua — in Greek isopsephy Ιησους)"],
}


def _arabic_to_gematria(arabic_name: str) -> tuple[int, list]:
    """Compute Hebrew gematria from Arabic name via Semitic bridge."""
    letters = []
    total = 0
    for ch in arabic_name:
        if ch in ARABIC_TO_HEBREW:
            heb_name, val = ARABIC_TO_HEBREW[ch]
            letters.append({"arabic": ch, "hebrew": heb_name, "value": val})
            total += val
    return total, letters


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    arabic = profile.arabic
    if not arabic or not arabic.strip():
        return SystemResult(
            id="gematria_word_matches",
            name="Gematria Word Matches",
            certainty="NEEDS_INPUT",
            data={"matches": None, "reason": "No Arabic name provided"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["Sefer ha-Bahir"],
            question="Q2_MEANING",
        )

    total, letters = _arabic_to_gematria(arabic)

    # Reduce to root
    def _reduce(n):
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(d) for d in str(n))
        return n

    root = _reduce(total)

    # Find exact matches
    exact = KNOWN_WORDS.get(total, [])

    # Find near matches (±1)
    near_minus = KNOWN_WORDS.get(total - 1, [])
    near_plus = KNOWN_WORDS.get(total + 1, [])

    # Find root matches (words sharing same digital root)
    root_matches = []
    for val, words in KNOWN_WORDS.items():
        if _reduce(val) == root and val != total:
            for w in words:
                root_matches.append({"value": val, "word": w})
    root_matches.sort(key=lambda x: abs(x["value"] - total))
    root_matches = root_matches[:10]  # Cap at 10

    # Per-word gematria
    word_values = []
    for word in arabic.split():
        w_total, _ = _arabic_to_gematria(word)
        w_matches = KNOWN_WORDS.get(w_total, [])
        word_values.append({
            "word": word,
            "gematria": w_total,
            "root": _reduce(w_total),
            "matches": w_matches[:3],
        })

    return SystemResult(
        id="gematria_word_matches",
        name="Gematria Word Matches",
        certainty="APPROX",
        data={
            "full_name_gematria": total,
            "root": root,
            "exact_matches": exact,
            "near_matches_minus_1": near_minus,
            "near_matches_plus_1": near_plus,
            "root_matches": root_matches,
            "per_word": word_values,
            "letter_count": len(letters),
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Sefer ha-Bahir", "Baal HaTurim", "kabbalah_solomonic_lookups.json"],
        question="Q2_MEANING",
    )
