"""Planetary Joy (Hellenistic House Rejoicing) — COMPUTED_STRICT
Each classical planet has a house where it rejoices — expresses most purely.
Measures angular resonance between natal chart and the classical cosmological
template. Independent of sign dignity, decan, or any other house system module.
Source tier A: Antiochus of Athens (c.200 CE), Porphyry, Abu Ma'shar.
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult

JOY_HOUSES = {'Mercury':1,'Moon':3,'Venus':5,'Mars':6,'Sun':9,'Jupiter':11,'Saturn':12}
JOY_RATIONALE = {
    'Mercury': 'H1 — Ascendant, body and self-presentation',
    'Moon':    'H3 — House of the Goddess, siblings and local movement',
    'Venus':   'H5 — Good Fortune, pleasure and children',
    'Mars':    'H6 — Bad Fortune, conflict and illness',
    'Sun':     'H9 — House of God, philosophy and long journeys',
    'Jupiter': 'H11 — Good Spirit, friendship and hope',
    'Saturn':  'H12 — Bad Spirit, isolation and hidden enemies',
}
PLANET_NATURE = {'Mercury':'neutral','Moon':'benefic','Venus':'benefic','Mars':'malefic','Sun':'light','Jupiter':'benefic','Saturn':'malefic'}

def _get_data(dob, birth_time_local, timezone):
    try:
        import swisseph as swe
        swe.set_ephe_path(None)
        tz_off = {"Asia/Riyadh":3,"Asia/Dubai":4,"UTC":0}.get(timezone,3)
        h, m = map(int, birth_time_local.split(":"))
        jd_ut = swe.julday(dob.year, dob.month, dob.day, (h + m/60) - tz_off)
        cusps, ascmc = swe.houses(jd_ut, 26.23, 50.03, b'P')
        bodies = {'Sun':swe.SUN,'Moon':swe.MOON,'Mercury':swe.MERCURY,'Venus':swe.VENUS,'Mars':swe.MARS,'Jupiter':swe.JUPITER,'Saturn':swe.SATURN}
        positions = {name: swe.calc_ut(jd_ut, bid)[0][0] for name, bid in bodies.items()}
        return positions, list(cusps), ascmc[0], True
    except Exception:
        return None, None, None, False

def _planet_house(lon, cusps):
    for i in range(12):
        s, e = cusps[i], cusps[(i+1)%12]
        if s <= e:
            if s <= lon < e: return i+1
        else:
            if lon >= s or lon < e: return i+1
    return 1

def _score(ph, jh):
    diff = abs(ph - jh)
    if diff > 6: diff = 12 - diff
    return round((1 - diff/6) * 100)

def compute(profile: InputProfile, constants: dict) -> SystemResult:
    positions, cusps, asc_lon, has_ephem = _get_data(
        profile.dob, profile.birth_time_local or "10:14", profile.timezone or "Asia/Riyadh"
    )

    if has_ephem and positions and cusps:
        ph = {p: _planet_house(lon, cusps) for p, lon in positions.items()}
        analysis = {}
        in_joy, near_joy = [], []
        for planet, joy_h in JOY_HOUSES.items():
            natal_h = ph.get(planet, 0)
            score = _score(natal_h, joy_h)
            status = 'IN JOY' if natal_h == joy_h else ('NEAR JOY' if score >= 67 else 'DISTANT')
            analysis[planet] = {'natal_house':natal_h,'joy_house':joy_h,'rejoicing_score':score,'status':status,'rationale':JOY_RATIONALE[planet],'nature':PLANET_NATURE[planet]}
            if status == 'IN JOY': in_joy.append(planet)
            elif status == 'NEAR JOY': near_joy.append(planet)
        certainty = "COMPUTED_STRICT"
        note = f"ASC={asc_lon:.2f}°. Placidus. Tropical."
        headline = f"{', '.join(in_joy)} in joy." if in_joy else (f"{', '.join(near_joy)} near joy." if near_joy else "No planets in direct joy.")
    else:
        analysis = {p:{'natal_house':0,'joy_house':h,'rejoicing_score':0,'status':'APPROX','rationale':JOY_RATIONALE[p],'nature':PLANET_NATURE[p]} for p,h in JOY_HOUSES.items()}
        in_joy, near_joy = [], []
        certainty, note, headline = "APPROX", "Ephemeris unavailable.", "Ephemeris required."

    in_joy_str = ', '.join(in_joy) if in_joy else 'none'
    near_joy_str = ', '.join(near_joy) if near_joy else 'none'

    interp_en = (
        f"Planetary Joy: {headline} In joy: {in_joy_str}. Near joy: {near_joy_str}. "
        f"A planet in its joy house expresses without constraint — the house amplifies rather than "
        f"qualifies its significations. Independent of sign dignity; measures spatial resonance "
        f"between your natal chart and the classical cosmological template."
    )
    interp_ar = (
        f"فرح الكواكب: {headline} في الفرح: {in_joy_str}. قريب من الفرح: {near_joy_str}. "
        f"الكوكب في بيت فرحه يُعبّر دون قيود — البيت يُضخّم دلالاته لا يُقيّدها. "
        f"مستقل عن كرامة البرج؛ يقيس الرنين المكاني بين خريطتك الميلادية والنموذج الكوزمولوجي الكلاسيكي."
    )

    return SystemResult(
        id="planetary_joy",
        name="Planetary Joy (Hellenistic House Rejoicing)",
        certainty=certainty,
        data={"planets":analysis,"in_joy":in_joy,"near_joy":near_joy,"joy_count":len(in_joy),"headline":headline,"note":note},
        interpretation=interp_en,
        ar_interpretation=interp_ar,
        constants_version=constants["version"],
        references=["Antiochus of Athens — Thesaurus (c.200 CE)","Porphyry — Introduction to the Tetrabiblos","Abu Ma'shar — Introductorium in Astronomiam","Brennan, C. — Hellenistic Astrology (2017)"],
        question="Q1_IDENTITY",
    )
