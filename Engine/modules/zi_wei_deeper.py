"""
Zi Wei Dou Shu Deeper — Four Transformations (四化)
─────────────────────────────────────────────────────
Extends zi_wei_dou_shu with the Si Hua (Four Transformations) system
based on the year stem.

Algorithm (from chinese_african_lookups.json):
  1. Get birth year Heavenly Stem
  2. Look up the 4 transformations: Hua Lu (化禄), Hua Quan (化权),
     Hua Ke (化科), Hua Ji (化忌)
  3. Each transformation maps a specific ZWDS star to a quality

Source: Zi Wei Dou Shu classical texts; Ming dynasty variants
SOURCE_TIER: A (primary ZWDS text)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Year stem → Four Transformations (from chinese_african_lookups.json)
FOUR_TRANSFORMATIONS = {
    "jia": {"hua_lu": "Lian Zhen", "hua_quan": "Po Jun", "hua_ke": "Wu Qu", "hua_ji": "Tai Yang"},
    "yi": {"hua_lu": "Tian Ji", "hua_quan": "Tian Liang", "hua_ke": "Zi Wei", "hua_ji": "Tai Yin"},
    "bing": {"hua_lu": "Tian Tong", "hua_quan": "Tian Ji", "hua_ke": "Wen Chang", "hua_ji": "Lian Zhen"},
    "ding": {"hua_lu": "Tai Yin", "hua_quan": "Tian Tong", "hua_ke": "Tian Ji", "hua_ji": "Ju Men"},
    "wu": {"hua_lu": "Tan Lang", "hua_quan": "Tai Yin", "hua_ke": "You Bi", "hua_ji": "Tian Ji"},
    "ji": {"hua_lu": "Wu Qu", "hua_quan": "Tan Lang", "hua_ke": "Tian Liang", "hua_ji": "Wen Qu"},
    "geng": {"hua_lu": "Tai Yang", "hua_quan": "Wu Qu", "hua_ke": "Tai Yin", "hua_ji": "Tian Tong"},
    "xin": {"hua_lu": "Ju Men", "hua_quan": "Tai Yang", "hua_ke": "Wen Qu", "hua_ji": "Wen Chang"},
    "ren": {"hua_lu": "Tian Liang", "hua_quan": "Zi Wei", "hua_ke": "Zuo Fu", "hua_ji": "Wu Fu"},
    "gui": {"hua_lu": "Po Jun", "hua_quan": "Ju Men", "hua_ke": "Tai Yin", "hua_ji": "Tan Lang"},
}

TRANSFORMATION_MEANING = {
    "hua_lu": {"name": "化禄 (Hua Lu)", "english": "Transformation of Prosperity", "quality": "abundance, flow, ease"},
    "hua_quan": {"name": "化权 (Hua Quan)", "english": "Transformation of Authority", "quality": "power, control, leadership"},
    "hua_ke": {"name": "化科 (Hua Ke)", "english": "Transformation of Fame", "quality": "recognition, scholarship, reputation"},
    "hua_ji": {"name": "化忌 (Hua Ji)", "english": "Transformation of Obstruction", "quality": "attachment, obsession, karmic debt"},
}

STEMS = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]


def _year_stem(year: int) -> str:
    """Get Heavenly Stem from year."""
    return STEMS[(year - 4) % 10]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    year = profile.dob.year
    stem = _year_stem(year)

    transformations = FOUR_TRANSFORMATIONS.get(stem, {})
    if not transformations:
        return SystemResult(
            id="zi_wei_deeper",
            name="Zi Wei Dou Shu — Four Transformations",
            certainty="NEEDS_INPUT",
            data={"transformations": None, "reason": f"Unknown stem: {stem}"},
            interpretation=None,
            constants_version=constants.get("version", ""),
            references=["ZWDS classical texts"],
            question="Q1_IDENTITY",
        )

    # Build detailed transformation report
    details = {}
    for key in ["hua_lu", "hua_quan", "hua_ke", "hua_ji"]:
        star = transformations.get(key, "Unknown")
        meaning = TRANSFORMATION_MEANING[key]
        details[key] = {
            "star": star,
            "transformation_name": meaning["name"],
            "english": meaning["english"],
            "quality": meaning["quality"],
        }

    # Detect if any star appears in multiple transformations (self-transformation)
    all_stars = [transformations[k] for k in ["hua_lu", "hua_quan", "hua_ke", "hua_ji"]]
    duplicates = [s for s in set(all_stars) if all_stars.count(s) > 1]

    return SystemResult(
        id="zi_wei_deeper",
        name="Zi Wei Dou Shu — Four Transformations",
        certainty="COMPUTED_STRICT",
        data={
            "year_stem": stem,
            "year": year,
            "hua_lu_star": transformations["hua_lu"],
            "hua_quan_star": transformations["hua_quan"],
            "hua_ke_star": transformations["hua_ke"],
            "hua_ji_star": transformations["hua_ji"],
            "details": details,
            "self_transformation": duplicates if duplicates else None,
            "module_class": "primary",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["ZWDS classical texts", "chinese_african_lookups.json"],
        question="Q1_IDENTITY",
    )
