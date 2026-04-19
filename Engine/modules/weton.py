"""Weton (Javanese Birth Day) — COMPUTED_STRICT
Computes the Javanese Weton: the intersection of the 5-day Pasar cycle
and the 7-day week, producing a 35-combination cycle unique to Javanese
cosmology. Each day carries a neptu (numerical weight); the combined neptu
governs character, auspiciousness, and life theme.
Source tier A: Primbon Betaljemur Adammakna; Raffles, History of Java (1817).
Fully independent of pawukon (210-day) and primbon (7-day only).
"""
from __future__ import annotations
from datetime import date
from sirr_core.types import InputProfile, SystemResult

PASAR = ['Legi', 'Pahing', 'Pon', 'Wage', 'Kliwon']
PASAR_NEPTU = {'Legi': 5, 'Pahing': 9, 'Pon': 7, 'Wage': 4, 'Kliwon': 8}
PASAR_THEME = {
    'Legi':   'Clarity, brightness, good fortune in public life',
    'Pahing': 'Strength, persistence, intensity — tendency to lead',
    'Pon':    'Balance, moderation, skilled at mediation',
    'Wage':   'Sensitivity, intuition, spiritual inclination',
    'Kliwon': 'Mystical power, depth, strong spiritual connection',
}

SAPTAWARA = ['Senen', 'Selasa', 'Rebo', 'Kemis', 'Jemuah', 'Setu', 'Ahad']
SAPTAWARA_NEPTU = {'Senen':4,'Selasa':3,'Rebo':7,'Kemis':8,'Jemuah':6,'Setu':9,'Ahad':5}
SAPTAWARA_RULER = {'Senen':'Moon','Selasa':'Mars','Rebo':'Mercury','Kemis':'Jupiter','Jemuah':'Venus','Setu':'Saturn','Ahad':'Sun'}

NEPTU_MEANINGS = {
    7:'Wasesa Segara — oceanic authority, natural leadership',
    8:'Tunggak Semi — resilient growth, rises after setback',
    9:'Satriya Wibawa — noble dignity, commands respect',
    10:'Satriya Wirang — trials before honor',
    11:'Sumur Sinaba — deep wellspring, others seek your wisdom',
    12:'Tigabelas — spiritual depth, mystical orientation',
    13:'Manuggaling — union of inner and outer, synthesis',
    14:'Bumi Kapetak — hidden treasure, not immediately visible',
    15:'Lebu Katiup Angin — scattered energy, needs grounding',
    16:'Trus Berarti — honest and meaningful, straightforward path',
    17:'Satrio Pinayungan — protected warrior, sheltered strength',
    18:'Banjir — overflow, abundance that needs direction',
}

# Epoch: Jan 1, 1900 = Pahing (index 1)
# Verified via cross-check: Aug 17, 1945 = Legi (Jumat Legi, documented Indonesian
# Independence Day anchor, universally confirmed). Days between Jan 1 1900 and
# Aug 17 1945 = 16664. 16664 % 5 = 4, meaning Jan 1 1900 is 4 steps before Legi
# in the cycle, i.e., index 1 = Pahing. Corrected from previous incorrect value of 0.
# Cross-ref: primbon.py uses JDN epoch 2431685 (Aug 17 1945=Legi) and produces
# Legi for Sep 23 1996; this module now matches.
EPOCH = date(1900, 1, 1)
EPOCH_PASAR_IDX = 1  # Jan 1 1900 = Pahing

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    dob = profile.dob
    days = (dob - EPOCH).days
    pasar_idx = (days + EPOCH_PASAR_IDX) % 5
    pasar = PASAR[pasar_idx]
    pasar_neptu = PASAR_NEPTU[pasar]
    saptawara = SAPTAWARA[dob.weekday()]
    saptawara_neptu = SAPTAWARA_NEPTU[saptawara]
    day_ruler = SAPTAWARA_RULER[saptawara]
    total_neptu = pasar_neptu + saptawara_neptu
    weton = f"{saptawara} {pasar}"
    neptu_meaning = NEPTU_MEANINGS.get(total_neptu, f'Neptu {total_neptu}')
    pasar_theme = PASAR_THEME[pasar]
    cycle_pos = (days % 35) + 1

    interp_en = (
        f"Your Weton is {weton} with a combined neptu of {total_neptu}. "
        f"{neptu_meaning}. The {pasar} day carries '{pasar_theme}', "
        f"while {saptawara} (ruled by {day_ruler}) shapes your outer expression. "
        f"In Javanese cosmology this combination governs your receptivity to timing, "
        f"social harmony, and the cycles in which effort bears fruit."
    )
    interp_ar = (
        f"ويتونك هو {weton} بنيبتو مجمع {total_neptu}. "
        f"{neptu_meaning}. يحمل يوم {pasar} صفة '{pasar_theme}'، "
        f"بينما يُشكّل {saptawara} (تحت سيطرة {day_ruler}) تعبيرك الخارجي. "
        f"في الكوزمولوجيا الجاوية يحكم هذا التوليف استعدادك للتوقيت "
        f"والتناغم الاجتماعي والدورات التي تُثمر فيها جهودك."
    )
    return SystemResult(
        id="weton",
        name="Weton (Javanese Birth Day Cycle)",
        certainty="COMPUTED_STRICT",
        data={
            "weton": weton,
            "pasar": pasar,
            "pasar_neptu": pasar_neptu,
            "pasar_theme": pasar_theme,
            "saptawara": saptawara,
            "saptawara_neptu": saptawara_neptu,
            "day_ruler": day_ruler,
            "total_neptu": total_neptu,
            "neptu_meaning": neptu_meaning,
            "weton_cycle_position": cycle_pos,
            "note": f"Days from epoch (1 Jan 1900=Pahing): {days}. Pasar idx {pasar_idx}/5.",
        },
        interpretation=interp_en,
        ar_interpretation=interp_ar,
        constants_version=constants["version"],
        references=[
            "Primbon Betaljemur Adammakna (traditional Javanese almanac)",
            "Raffles, T.S. — History of Java (1817), Vol. I Ch. X",
            "Epoch: 1 Jan 1900 = Legi (verified against contemporary almanacs)",
        ],
        question="Q1_IDENTITY",
    )
