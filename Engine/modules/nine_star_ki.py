"""Nine Star Ki (九星気学) — COMPUTED_STRICT
Computes Year Star and Month Star from DOB.
Year Star: (11 - (year % 9)) % 9; if 0 then 9.
Month Star: lookup from year-star group table.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


def _year_star(year: int) -> int:
    """Calculate Nine Star Ki year number. Uses Feb 4 as year start."""
    s = (11 - (year % 9)) % 9
    return s if s != 0 else 9


def _month_star(year_star: int, month: int) -> int:
    """Calculate month star from year star group and month.
    Month index: Feb=0, Mar=1, ..., Jan=11.
    Year stars 1,4,7 share one table; 2,5,8 another; 3,6,9 another.
    """
    # Month tables (Feb=index 0 through Jan=index 11)
    if year_star in (1, 4, 7):
        table = [5, 4, 3, 2, 1, 9, 8, 7, 6, 5, 4, 3]
    elif year_star in (2, 5, 8):
        table = [8, 7, 6, 5, 4, 3, 2, 1, 9, 8, 7, 6]
    else:  # 3, 6, 9
        table = [2, 1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 9]

    # Convert calendar month to table index (Feb=0)
    idx = (month - 2) % 12
    return table[idx]


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    cfg = constants["nine_star_ki"]
    stars_data = cfg["stars"]

    # Effective year (Lichun ~ Feb 4)
    y, m, d = profile.dob.year, profile.dob.month, profile.dob.day
    eff_year = y if (m > 2 or (m == 2 and d >= 4)) else y - 1

    ys = _year_star(eff_year)
    ms = _month_star(ys, profile.dob.month)

    year_info = stars_data[str(ys)]
    month_info = stars_data[str(ms)]

    # Ki number string (e.g. "1-5" or "1.5")
    ki_string = f"{ys}.{ms}"

    # Element interaction
    year_elem = year_info["element"]
    month_elem = month_info["element"]

    return SystemResult(
        id="nine_star_ki",
        name="Nine Star Ki (九星気学)",
        certainty="COMPUTED_STRICT",
        data={
            "year_star": ys,
            "year_star_name": year_info["name"],
            "year_element": year_elem,
            "year_trigram": year_info["trigram"],
            "year_direction": year_info["direction"],
            "month_star": ms,
            "month_star_name": month_info["name"],
            "month_element": month_elem,
            "month_trigram": month_info["trigram"],
            "month_direction": month_info["direction"],
            "ki_string": ki_string,
            "note": "Year star = core nature. Month star = emotional/inner nature. Lichun boundary applied."
        },
        interpretation=f"Nine Star Ki: {ki_string}. Year: {year_info['name']} ({year_info['trigram']}). Month: {month_info['name']} ({month_info['trigram']}).",
        constants_version=constants["version"],
        references=["Nine Star Ki / 九星気学", "Lo Shu reverse cycle"],
        question="Q1_IDENTITY"
    )