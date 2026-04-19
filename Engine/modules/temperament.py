"""Four Temperaments — LOOKUP_FIXED"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

def compute(profile: InputProfile, constants: dict, primary_element: str, secondary_element: str = None) -> SystemResult:
    mapping = constants["temperament"]["element_mapping"]
    primary = mapping.get(primary_element, {})
    secondary = mapping.get(secondary_element, {}) if secondary_element else {}

    data = {
        "primary_element": primary_element,
        "primary_temperament": primary.get("temperament", "Unknown"),
        "primary_quality": primary.get("quality", ""),
        "primary_unani": primary.get("unani", ""),
    }

    if secondary_element:
        data["secondary_element"] = secondary_element
        data["secondary_temperament"] = secondary.get("temperament", "Unknown")
        data["secondary_quality"] = secondary.get("quality", "")
        data["secondary_unani"] = secondary.get("unani", "")
        data["blend"] = f"{primary.get('temperament','')}-{secondary.get('temperament','')}"

    return SystemResult(
        id="temperament",
        name="Four Temperaments (Classical + Unani)",
        certainty="LOOKUP_FIXED",
        data=data,
        interpretation="Element-to-temperament mapping. Depends on converged element from other systems.",
        constants_version=constants["version"],
        references=["Hippocratic/Galenic tradition + Unani Tibb"],
        question="Q3_NATURE"
    )
