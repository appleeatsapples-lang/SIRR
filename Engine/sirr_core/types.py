from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Literal, Optional

Certainty = Literal[
    "COMPUTED_STRICT",
    "LOOKUP_FIXED",
    "APPROX",
    "NEEDS_EPHEMERIS",
    "NEEDS_CORRELATION",
    "NEEDS_INPUT",
    "META"
]

@dataclass(frozen=True)
class InputProfile:
    subject: str
    arabic: str
    dob: date
    today: date
    birth_time_local: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    # Pre-computed core numbers (from SIRR v1 engines) for bridge/synthesis use
    life_path: Optional[int] = None
    expression: Optional[int] = None
    soul_urge: Optional[int] = None
    personality: Optional[int] = None
    birthday_number: Optional[int] = None
    abjad_first: Optional[int] = None
    gender: Optional[str] = None  # "male" or "female" — needed for BaZi Luck Pillars direction
    mother_name: Optional[str] = None
    mother_name_ar: Optional[str] = None
    mother_dob: Optional[str] = None  # ISO format string
    variant: Optional[str] = None      # name variant key (passport_legal, spoken_legal, etc.)
    latitude: Optional[float] = None   # decimal degrees (from geocoder)
    longitude: Optional[float] = None  # decimal degrees (from geocoder)
    utc_offset: Optional[float] = None # hours from UTC (from geocoder)

@dataclass
class SystemResult:
    id: str
    name: str
    certainty: Certainty
    data: Dict[str, Any]
    interpretation: Optional[str]
    constants_version: str
    references: List[str]
    question: Optional[str] = None  # Which of the 6 Questions this answers
    ar_interpretation: Optional[str] = None

@dataclass
class RunOutput:
    profile: Dict[str, Any]
    constants: Dict[str, Any]
    results: List[SystemResult]
    ledger: List[Dict[str, Any]]
    synthesis: Optional[Dict[str, Any]] = None
