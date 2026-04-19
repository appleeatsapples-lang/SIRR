"""Steiner 7-Year Life Cycles — COMPUTED_STRICT
Rudolf Steiner's anthroposophic developmental phases.
Every 7 years marks a new stage of consciousness.
0-7: Physical body, 7-14: Etheric body, 14-21: Astral body,
21-28: Sentient soul, 28-35: Intellectual soul, 35-42: Consciousness soul,
42-49: Spirit self, 49-56: Life spirit, 56-63: Spirit man.
Source: Steiner's educational/anthroposophic writings
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

PHASES = [
    (0, "Physical Body", "Imitation, will forces, walking/speaking/thinking"),
    (7, "Etheric Body", "Imagination, memory, authority of teacher"),
    (14, "Astral Body", "Abstract thinking, idealism, emotional turbulence"),
    (21, "Sentient Soul", "Encounter with world, independence, first vocation"),
    (28, "Intellectual Soul", "Rational assessment, career building, crisis of meaning"),
    (35, "Consciousness Soul", "Spiritual seeking, individuation, midlife threshold"),
    (42, "Spirit Self", "Higher self integration, mentorship, wisdom emerges"),
    (49, "Life Spirit", "Transformation of habits, giving back, legacy building"),
    (56, "Spirit Man", "Spiritual freedom, elder wisdom, transcendence"),
    (63, "Extended Spirit Man", "Completion cycle, review, preparation"),
]

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    age = profile.today.year - profile.dob.year
    if (profile.today.month, profile.today.day) < (profile.dob.month, profile.dob.day):
        age -= 1

    cycle_number = age // 7 + 1
    phase_index = min(age // 7, len(PHASES) - 1)
    phase_start, phase_name, phase_desc = PHASES[phase_index]
    years_into_phase = age - phase_start

    return SystemResult(
        id="steiner_cycles",
        name="Steiner 7-Year Life Cycles",
        certainty="COMPUTED_STRICT",
        data={
            "age": age,
            "cycle_number": cycle_number,
            "phase_name": phase_name,
            "phase_description": phase_desc,
            "phase_start_age": phase_start,
            "phase_end_age": phase_start + 6,
            "years_into_phase": years_into_phase,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Rudolf Steiner anthroposophic 7-year developmental cycles"],
        question="Q3_TIMING"
    )
