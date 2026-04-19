"""Zakat al-Huruf (Letter Zakat / Invocation Tax) — COMPUTED_STRICT
Calculates the repetition count needed to 'activate' a name or phrase.
The Zakat Akbar (Greater) = Abjad total of the name.
The Zakat Asghar (Lesser) = digital root × letter count.
The Da'wat (invocation protocol) specifies recitation over days.
Source: Manba' Usul al-Hikmah (Al-Buni, 13th century)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in abjad]
    letter_count = len(letters)

    total = sum(abjad.get(ch, 0) for ch in letters)
    root = reduce_number(total, keep_masters=())

    # Zakat Akbar: full abjad total = number of recitations
    zakat_akbar = total

    # Zakat Asghar: root × letter count
    zakat_asghar = root * letter_count

    # Da'wat protocol: spread over 7 days
    daily_akbar = zakat_akbar // 7
    remainder_akbar = zakat_akbar % 7

    # Per-letter zakat (each letter's own activation count)
    letter_zakats = []
    for ch in letters:
        v = abjad.get(ch, 0)
        letter_zakats.append((ch, v))

    return SystemResult(
        id="zakat_huruf",
        name="Zakat al-Huruf (زكاة الحروف — Letter Zakat)",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic,
            "letter_count": letter_count,
            "abjad_total": total,
            "abjad_root": root,
            "zakat_akbar": zakat_akbar,
            "zakat_asghar": zakat_asghar,
            "dawat_7day": {
                "daily_count": daily_akbar,
                "final_day_extra": remainder_akbar,
                "total_check": daily_akbar * 7 + remainder_akbar,
            },
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Zakat Akbar = full Abjad total of name.",
            "Zakat Asghar = digital root × letter count.",
            "Da'wat protocol: 7-day distribution.",
            "Source: Manba' Usul al-Hikmah, Al-Buni.",
        ],
        question="Q3_PRACTICE"
    )
