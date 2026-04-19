"""Sarvatobhadra Chakra — 9×9 Vedic Predictive Matrix — COMPUTED_STRICT

The "All-Auspicious Wheel" maps nakshatras, vowels, consonants, tithis, and
rasis onto a 9×9 grid to detect vedha (obstruction) patterns from natal and
transit planetary placements.

Algorithm:
  1. Convert natal planets to sidereal (Lahiri)
  2. Map each planet to its nakshatra (28 nakshatras including Abhijit)
  3. Place nakshatras on the outer ring of the 9×9 matrix
  4. Detect vedha: benefics on a nakshatra → positive, malefics → negative
  5. Score vedha interactions for each cell

Sources: Mansagari, Phaladeepika (Mantreswara)
"""
from __future__ import annotations
import swisseph as swe
from sirr_core.types import InputProfile, SystemResult

# 28 Nakshatras (including Abhijit between Uttara Ashadha and Shravana)
NAKSHATRAS_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Abhijit", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Standard 27 nakshatras (without Abhijit) for longitude mapping
NAKSHATRAS_27 = [n for n in NAKSHATRAS_28 if n != "Abhijit"]

# SBC outer ring: 28 nakshatras mapped to border cells of 9×9 grid
# The grid border has 32 cells (9*4 - 4 corners counted once)
# 28 nakshatras + 4 corner cells = 32 border positions
# Classic mapping: nakshatras placed clockwise starting from top-left
SBC_BORDER_POSITIONS = [
    # Top row (left to right): cells (0,0) through (0,8)
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
    # Right column (top to bottom): cells (1,8) through (7,8)
    (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8),
    # Bottom row (right to left): cells (8,7) through (8,1)
    (8, 7), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1),
    # Left column (bottom to top): cells (7,0) through (1,0)
    (7, 0), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0),
]

# Corner cells (not nakshatras — traditionally hold rasis or tithis)
SBC_CORNERS = [(0, 0), (0, 8), (8, 8), (8, 0)]

# Benefic/malefic classification (natural)
BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
MALEFICS = {"Saturn", "Mars", "Sun", "Rahu", "Ketu"}

# 12 Rashis (sidereal signs)
RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

# 30 Tithis
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

# Abhijit nakshatra spans 6°40' to 10°53'20" Capricorn (sidereal)
ABHIJIT_START = 276.6667  # 276°40'
ABHIJIT_END = 280.8889    # 280°53'20"


def _sid_to_nakshatra_28(sid_lon: float) -> tuple:
    """Map sidereal longitude to one of 28 nakshatras (with Abhijit).
    Returns (index_in_28, nakshatra_name)."""
    lon = sid_lon % 360
    # Check Abhijit range first (special insertion)
    if ABHIJIT_START <= lon < ABHIJIT_END:
        return (21, "Abhijit")

    # Standard 27-nakshatra mapping
    nak_span = 360 / 27  # 13°20'
    idx_27 = int(lon / nak_span)
    if idx_27 >= 27:
        idx_27 = 26
    nak_name = NAKSHATRAS_27[idx_27]

    # Map 27-index to 28-index (Abhijit inserted at position 21)
    idx_28 = NAKSHATRAS_28.index(nak_name)
    return (idx_28, nak_name)


def _compute_tithi(sun_sid: float, moon_sid: float) -> tuple:
    """Compute tithi from sidereal Sun and Moon longitudes.
    Returns (tithi_number 1-30, tithi_name)."""
    diff = (moon_sid - sun_sid) % 360
    tithi_num = int(diff / 12) + 1
    if tithi_num > 30:
        tithi_num = 30
    return (tithi_num, TITHIS[tithi_num - 1])


def compute(profile: InputProfile, constants: dict, natal_chart_data: dict = None,
            **kwargs) -> SystemResult:
    if natal_chart_data is None:
        return SystemResult(
            id="sarvatobhadra",
            name="Sarvatobhadra Chakra (9×9 Vedic Matrix)",
            certainty="NEEDS_INPUT",
            data={"error": "natal_chart_data required"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q5_SYSTEM",
        )

    jd = natal_chart_data.get("julian_day", 2450349.8)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    planets_raw = natal_chart_data.get("planets", {})

    # Convert to sidereal
    sid_planets = {}
    for name, pdata in planets_raw.items():
        trop = pdata.get("longitude", 0)
        sid = (trop - ayanamsa) % 360
        sid_planets[name] = sid

    # Add Ketu (180° from North Node)
    if "North Node" in sid_planets:
        sid_planets["Rahu"] = sid_planets["North Node"]
        sid_planets["Ketu"] = (sid_planets["North Node"] + 180) % 360

    # Map planets to nakshatras
    planet_nakshatras = {}
    for name, sid_lon in sid_planets.items():
        if name == "North Node":
            continue  # Use Rahu instead
        idx_28, nak_name = _sid_to_nakshatra_28(sid_lon)
        planet_nakshatras[name] = {
            "nakshatra": nak_name,
            "nakshatra_index": idx_28,
            "sidereal_longitude": round(sid_lon, 4),
        }

    # Compute natal tithi
    sun_sid = sid_planets.get("Sun", 0)
    moon_sid = sid_planets.get("Moon", 0)
    tithi_num, tithi_name = _compute_tithi(sun_sid, moon_sid)

    # Natal rashi (Moon's sidereal sign)
    moon_rashi_idx = int(moon_sid / 30) % 12
    moon_rashi = RASHIS[moon_rashi_idx]

    # Build 9×9 matrix
    matrix = [[{"row": r, "col": c, "content": None, "planets": [], "vedha_score": 0}
                for c in range(9)] for r in range(9)]

    # Place nakshatras on border
    for i, nak_name in enumerate(NAKSHATRAS_28):
        if i < len(SBC_BORDER_POSITIONS):
            r, c = SBC_BORDER_POSITIONS[i]
            matrix[r][c]["content"] = nak_name
            matrix[r][c]["type"] = "nakshatra"

    # Place corners (traditionally: 4 rashis or directional markers)
    corner_labels = ["NE", "NW", "SW", "SE"]
    for i, (r, c) in enumerate(SBC_CORNERS):
        matrix[r][c]["content"] = corner_labels[i]
        matrix[r][c]["type"] = "corner"

    # Center cell
    matrix[4][4]["content"] = "Center"
    matrix[4][4]["type"] = "center"

    # Place planets on their nakshatra positions
    for name, pnak in planet_nakshatras.items():
        idx = pnak["nakshatra_index"]
        if idx < len(SBC_BORDER_POSITIONS):
            r, c = SBC_BORDER_POSITIONS[idx]
            matrix[r][c]["planets"].append(name)

    # Compute vedha scores
    # Vedha occurs when a planet occupies a nakshatra that has a diagonal
    # relationship to another nakshatra on the grid
    vedha_list = []
    occupied_cells = []
    for name, pnak in planet_nakshatras.items():
        idx = pnak["nakshatra_index"]
        if idx < len(SBC_BORDER_POSITIONS):
            r, c = SBC_BORDER_POSITIONS[idx]
            is_benefic = name in BENEFICS
            score = 1 if is_benefic else -1
            occupied_cells.append((r, c, name, score))

    # Check vedha between occupied cells
    for i, (r1, c1, name1, score1) in enumerate(occupied_cells):
        for j, (r2, c2, name2, score2) in enumerate(occupied_cells):
            if i >= j:
                continue
            # Vedha: diagonal alignment (same row, same column, or diagonal)
            if r1 == r2 or c1 == c2:
                vedha_type = "direct"
            elif abs(r1 - r2) == abs(c1 - c2):
                vedha_type = "diagonal"
            else:
                continue

            combined_score = score1 + score2
            vedha_list.append({
                "planet_1": name1,
                "planet_2": name2,
                "vedha_type": vedha_type,
                "combined_effect": "positive" if combined_score > 0 else "negative" if combined_score < 0 else "neutral",
            })
            matrix[r1][c1]["vedha_score"] += score2
            matrix[r2][c2]["vedha_score"] += score1

    # Count benefic vs malefic vedhas
    positive_vedhas = sum(1 for v in vedha_list if v["combined_effect"] == "positive")
    negative_vedhas = sum(1 for v in vedha_list if v["combined_effect"] == "negative")

    # Flatten matrix for output (only non-empty cells)
    matrix_summary = []
    for r in range(9):
        for c in range(9):
            cell = matrix[r][c]
            if cell["content"] or cell["planets"]:
                matrix_summary.append({
                    "row": r, "col": c,
                    "content": cell["content"],
                    "planets": cell["planets"],
                    "vedha_score": cell["vedha_score"],
                })

    data = {
        "method": "sbc_28nak_v1",
        "ayanamsa": round(ayanamsa, 6),
        "natal_tithi": tithi_num,
        "natal_tithi_name": tithi_name,
        "moon_rashi": moon_rashi,
        "planet_nakshatras": planet_nakshatras,
        "vedha_interactions": vedha_list,
        "vedha_count": len(vedha_list),
        "positive_vedhas": positive_vedhas,
        "negative_vedhas": negative_vedhas,
        "matrix_occupied_cells": len(matrix_summary),
        "matrix_summary": matrix_summary,
    }

    return SystemResult(
        id="sarvatobhadra",
        name="Sarvatobhadra Chakra (9×9 Vedic Matrix)",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Mansagari — Sarvatobhadra Chakra classical reference",
            "Mantreswara, Phaladeepika — SBC application",
        ],
        question="Q5_SYSTEM",
    )
