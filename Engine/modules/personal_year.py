"""Personal Year / Month / Day — COMPUTED_STRICT
Current temporal vibration cycles.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def compute(profile: InputProfile, constants: dict) -> SystemResult:
    m = profile.dob.month
    d = profile.dob.day
    y = profile.today.year

    # Personal Year = birth month + birth day + current year
    py_raw = m + d + sum(int(x) for x in str(y))
    personal_year = reduce_number(py_raw)

    # Personal Month = personal year + current calendar month
    pm_raw = personal_year + profile.today.month
    personal_month = reduce_number(pm_raw)

    # Personal Day = personal month + current calendar day
    pd_raw = personal_month + profile.today.day
    personal_day = reduce_number(pd_raw)

    # Check if birthday has passed this year
    bday_passed = (profile.today.month, profile.today.day) >= (m, d)

    return SystemResult(
        id="personal_year",
        name="Personal Year / Month / Day",
        certainty="COMPUTED_STRICT",
        data={
            "personal_year": personal_year,
            "personal_year_raw": py_raw,
            "personal_month": personal_month,
            "personal_day": personal_day,
            "calendar_year": y,
            "birthday_passed": bday_passed,
            "note": "Year cycle shifts near birthday" if not bday_passed else "In current year cycle"
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Personal Year = birth month + birth day + current year digits, reduced",
                    "SOURCE_TIER:C — Modern system. Algorithms popularized by Juno Jordan, Florence Campbell (20th c.). No classical Pythagorean textual algorithm documented."],
        question="Q4_TIMING"
    )
