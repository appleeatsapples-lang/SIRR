"""Arabic→Ethiopian Cognate Sum — COMPUTED_STRICT

Scholarship fidelity (§4.5 rule 2 — cognate-mapping surfaced):
  This module routes Arabic letters through an Arabic-to-Ge'ez cognate
  table and sums the resulting values. Identity with Abjad Kabir totals
  is BY CONSTRUCTION (same Arabic input, equivalent-position letters),
  NOT cross-tradition convergence.

  Ethiopian asmat (ጸሎተ አስማት) as practiced in ketab/talisman manuscripts
  uses native Ge'ez text, not Arabic-sourced computation. Claiming a
  triple match across Arabic / Mandaean-cognate / Ethiopian-cognate
  reflects historical agreement would be false. It reflects the mapping.

  The module kept its internal id `ethiopian_asmat` for engine-key
  stability; the public `name` field names it honestly.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number

# Ge'ez fidel numeric values (first-order) via Arabic cognate mapping
GEEZ_FROM_ABJAD = {
    'ا':1,'ب':2,'ج':3,'د':4,'ه':5,'و':6,'ز':7,'ح':8,'ط':9,'ي':10,
    'ك':20,'ل':30,'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,
    'ق':100,'ر':200,'ش':300,'ت':400,'أ':1,'إ':1,'آ':1,
}

ANGELS = {1:"Mikael",2:"Gabreel",3:"Rufael",4:"Urael",5:"Raguel",6:"Suryal",7:"Fanuel",0:"Mikael"}

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    name = profile.arabic.replace(" ","")
    total = sum(GEEZ_FROM_ABJAD.get(ch, 0) for ch in name)
    root = reduce_number(total, keep_masters=())
    angel_idx = total % 7
    angel = ANGELS.get(angel_idx, "Unknown")

    return SystemResult(
        id="ethiopian_asmat", name="Arabic-to-Ethiopian Cognate Sum",
        certainty="COMPUTED_STRICT",
        data={
            "arabic_name": profile.arabic, "total": total, "root": root,
            "angel_mod7": angel_idx, "guardian_angel": angel,
            "note": ("Arabic→Ge'ez cognate letter mapping. Identity with Abjad Kabir "
                     "totals is by construction, not cross-tradition convergence. "
                     "Native Ethiopian asmat uses Ge'ez text directly."),
                     # Scholarship Fidelity — §4.1 label + note (surfaces to output JSON)
                     "scholarship_fidelity": "MODERN_SYNTHESIS",
                     "scholarship_note": "Cognate-mapping identity-by-construction with Abjad Kabir; native ketab tradition uses Ge'ez text directly.",
         },
        interpretation=None, constants_version=constants["version"],
        references=["Ethiopian ketab manuscripts (for native Ge'ez talismanic context — NOT this module's algorithm)",
                    "Arabic-to-Ge'ez cognate letter mapping (the actual algorithm used here)",
                    "SOURCE_TIER:B/INVESTIGATE — native Ethiopian asmat uses Ge'ez text, not Arabic-sourced computation."],
        question="Q4_PROTECTION"
    )
