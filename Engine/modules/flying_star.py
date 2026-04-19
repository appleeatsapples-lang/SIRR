"""Flying Star Feng Shui (玄空飛星) — COMPUTED_STRICT
Computes annual flying star chart for birth year AND current year.
Stars fly through the 9 Lo Shu palaces.
Period-aware star timeliness per Xuan Kong tradition.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Lo Shu flight path order: Center(5)→NW(6)→W(7)→NE(8)→S(9)→N(1)→SW(2)→E(3)→SE(4)
PALACE_FLIGHT_ORDER = [4, 3, 8, 9, 5, 1, 2, 7, 6]  # indices into 3x3 grid (row-major)
PALACE_NAMES = {
    (0, 0): "SE", (0, 1): "S", (0, 2): "SW",
    (1, 0): "E",  (1, 1): "Center", (1, 2): "W",
    (2, 0): "NE", (2, 1): "N", (2, 2): "NW",
}

# Standard Lo Shu base grid
LO_SHU_BASE = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

# Flight sequence: palace positions in flight order
FLIGHT_SEQUENCE = [
    (1, 1),  # Center
    (2, 2),  # NW
    (1, 2),  # W
    (2, 0),  # NE
    (0, 1),  # S
    (2, 1),  # N
    (0, 2),  # SW
    (1, 0),  # E
    (0, 0),  # SE
]

# Star timeliness by period number (1-9)
# Each period: timely star = period number, future prosperous = next star,
# retreating = previous two, untimely = rest
def _star_timeliness(period: int) -> dict:
    """Return star → timeliness status mapping for a given period.
    Timely = current period star. Future Prosperous = next star.
    Retreating = previous period star and the one before it.
    Untimely = all remaining stars.
    Period 9 example: 9=timely, 1=future, 8=retreating, 6=retreating, rest=untimely.
    """
    status = {}
    # Retreating: previous period star and 3-periods-back star
    # Period 9 example: 8 (prev period) and 6 (3 back) are retreating
    retreating = {((period - 2) % 9) + 1, ((period - 4) % 9) + 1}
    for s in range(1, 10):
        if s == period:
            status[s] = "TIMELY"
        elif s == (period % 9) + 1:
            status[s] = "FUTURE_PROSPEROUS"
        elif s in retreating:
            status[s] = "RETREATING"
        else:
            status[s] = "UNTIMELY"
    return status


def _get_period(year: int) -> int:
    """Determine the Feng Shui period for a given year."""
    # Upper Era: P1(1864-1883), P2(1884-1903), P3(1904-1923)
    # Middle Era: P4(1924-1943), P5(1944-1963), P6(1964-1983)
    # Lower Era: P7(1984-2003), P8(2004-2023), P9(2024-2043)
    # Then cycles: P1(2044-2063)...
    base = 1864
    offset = (year - base) % 180
    period = (offset // 20) + 1
    return min(period, 9)  # clamp to 1-9


def _annual_star(year: int) -> int:
    """Same formula as Nine Star Ki year star."""
    s = (11 - (year % 9)) % 9
    return s if s != 0 else 9


def _build_chart(center_star: int) -> dict:
    """Build flying star chart with given center star."""
    chart = {}
    offset = center_star - 5
    for i, (r, c) in enumerate(FLIGHT_SEQUENCE):
        star = ((5 + i + offset - 1) % 9) + 1
        palace = PALACE_NAMES[(r, c)]
        chart[palace] = star
    return chart


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    # Birth year chart
    y = profile.dob.year
    m, d = profile.dob.month, profile.dob.day
    eff_birth_year = y if (m > 2 or (m == 2 and d >= 4)) else y - 1

    birth_center = _annual_star(eff_birth_year)
    birth_chart = _build_chart(birth_center)

    # Current year chart
    cy = profile.today.year
    cm, cd = profile.today.month, profile.today.day
    eff_current_year = cy if (cm > 2 or (cm == 2 and cd >= 4)) else cy - 1

    current_center = _annual_star(eff_current_year)
    current_chart = _build_chart(current_center)

    # Period detection and star timeliness
    current_period = _get_period(eff_current_year)
    timeliness = _star_timeliness(current_period)

    # Period-aware sector analysis
    auspicious = {k: v for k, v in current_chart.items()
                  if timeliness.get(v) in ("TIMELY", "FUTURE_PROSPEROUS")}
    inauspicious = {k: v for k, v in current_chart.items()
                    if timeliness.get(v) == "UNTIMELY"}

    # Star timeliness for current chart
    star_status = {}
    for palace, star in current_chart.items():
        star_status[palace] = {"star": star, "status": timeliness.get(star, "UNKNOWN")}

    return SystemResult(
        id="flying_star",
        name="Flying Star Feng Shui (玄空飛星)",
        certainty="COMPUTED_STRICT",
        data={
            "birth_year_star": birth_center,
            "birth_chart": birth_chart,
            "current_year_star": current_center,
            "current_year": eff_current_year,
            "current_period": current_period,
            "current_chart": current_chart,
            "star_timeliness": timeliness,
            "star_status_by_sector": star_status,
            "auspicious_sectors": auspicious,
            "inauspicious_sectors": inauspicious,
            "note": f"Period {current_period} (star {current_period} is TIMELY). Annual flying stars."
        },
        interpretation=f"Birth center star: {birth_center}. Current ({eff_current_year}) center: {current_center}. Period {current_period}.",
        constants_version=constants["version"],
        references=["Xuan Kong Flying Star 玄空飛星", "Lo Shu magic square flight path"],
        question="Q4_TIMING"
    )
