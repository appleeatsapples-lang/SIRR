"""Arabic Letter Nature — Al-Buni Full Classification (طبائع الحروف) — COMPUTED_STRICT
Each letter has element + planet + sign + temperament per Al-Buni's
Shams al-Ma'arif. This expands beyond elemental_letters to the full
planetary and zodiacal letter classification.
"""
from __future__ import annotations
import json
from pathlib import Path
from sirr_core.types import InputProfile, SystemResult
from sirr_core.private_overlay import load_and_merge

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "arabic_linguistics_tables.json"
_TABLES = None


def _load_tables() -> dict:
    global _TABLES
    if _TABLES is None:
        public = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
        _TABLES = load_and_merge(public)
    return _TABLES


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    tables = _load_tables()
    buni_table = tables["al_buni_letter_table"]

    name = profile.arabic.replace(" ", "")
    letters = [ch for ch in name if ch in buni_table]
    total = len(letters)

    # Distributions
    element_counts = {}
    planet_counts = {}
    sign_counts = {}
    temperament_counts = {}
    quality_counts = {}

    for ch in letters:
        entry = buni_table[ch]
        elem = entry["element"]
        planet = entry["planet"]
        sign = entry["sign"]
        temp = entry["temperament"]
        qual = entry["quality"]

        element_counts[elem] = element_counts.get(elem, 0) + 1
        planet_counts[planet] = planet_counts.get(planet, 0) + 1
        sign_counts[sign] = sign_counts.get(sign, 0) + 1
        temperament_counts[temp] = temperament_counts.get(temp, 0) + 1
        quality_counts[qual] = quality_counts.get(qual, 0) + 1

    # Percentages
    element_pct = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in element_counts.items()}
    planet_pct = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in planet_counts.items()}

    # Dominants
    dominant_element = max(element_counts, key=element_counts.get) if element_counts else "unknown"
    dominant_planet = max(planet_counts, key=planet_counts.get) if planet_counts else "unknown"
    dominant_sign = max(sign_counts, key=sign_counts.get) if sign_counts else "unknown"
    dominant_temperament = max(temperament_counts, key=temperament_counts.get) if temperament_counts else "unknown"

    # Luminous vs dark
    luminous = quality_counts.get("luminous", 0)
    dark = quality_counts.get("dark", 0)
    luminous_ratio = round(luminous / total * 100, 1) if total > 0 else 0

    # Color mapping from element
    color_map = tables.get("letter_color_map", {})
    dominant_color = color_map.get(dominant_element, {}).get("color", "unknown")
    dominant_color_ar = color_map.get(dominant_element, {}).get("color_ar", "unknown")

    return SystemResult(
        id="arabic_letter_nature",
        name="Arabic Letter Nature — Al-Buni (طبائع الحروف)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "arabic_name": profile.arabic,
            "total_letters": total,
            "element_distribution": element_counts,
            "element_percentages": element_pct,
            "dominant_element": dominant_element,
            "planet_distribution": planet_counts,
            "planet_percentages": planet_pct,
            "dominant_planet": dominant_planet,
            "sign_distribution": sign_counts,
            "dominant_sign": dominant_sign,
            "temperament_distribution": temperament_counts,
            "dominant_temperament": dominant_temperament,
            "quality_distribution": quality_counts,
            "luminous_ratio": luminous_ratio,
            "dominant_color": dominant_color,
            "dominant_color_ar": dominant_color_ar,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=[
            "Al-Buni, Shams al-Ma'arif al-Kubra (28-letter classification)",
            "Ibn Arabi — Huruf correspondence tables",
        ],
        question="Q3_NATURE"
    )
