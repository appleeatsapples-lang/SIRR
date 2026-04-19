"""Data classes for the Quranic Figures Full module."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BilingualText:
    en: str
    ar: str


@dataclass
class HebrewCrossmatch:
    name_he: str
    gematria: int
    match_type: str          # "exact"
    tag: str                 # "EXPECTED_COGNATE_MATCH" | "CROSS_TRADITION_CONVERGENCE"
    note: Optional[str] = None


@dataclass
class ConfidenceRecord:
    level: str               # "HIGH" | "MEDIUM" | "LOW" | "RETIRED"
    adversarial_batches: int  # always 3
    computation_verified: bool


@dataclass
class FigureMetadata:
    is_prophet: bool
    is_antagonist: bool
    opposed_prophet: Optional[str]
    is_pair_member: bool
    pair_key: Optional[str]
    master_chain: Optional[str]   # e.g. "11→2" if passes through 11
    scope: str                    # "prophet_chain" | "full_corpus"


@dataclass
class QuranicFigureFullRecord:
    index: int
    name_ar: str
    name_en: str
    category: str
    abjad_value: int
    letter_breakdown: List[Dict]
    reduction_chain: str
    final_value: int
    master_number_retained: bool
    quran_frequency: Optional[int]
    special_tag: Optional[str]
    letter_meanings: BilingualText
    structural_reading: BilingualText
    quranic_role_note: BilingualText
    contrast_with_prophets: BilingualText
    hebrew_crossmatch: Optional[HebrewCrossmatch]
    convergence_tags: List[str]
    confidence: ConfidenceRecord
    metadata: FigureMetadata
