"""Human Design — Type, Authority, Profile, Channels, Centers, Incarnation Cross.
Computes Personality (birth) and Design (88° solar arc backward) planetary positions,
maps to I Ching gates via the Rave Mandala, determines defined centers, channels,
Type, Authority, Profile, and Incarnation Cross.

COMPUTED_STRICT when birth time present, NEEDS_INPUT when missing.
"""
from __future__ import annotations
from collections import deque
from sirr_core.types import InputProfile, SystemResult
from modules.natal_chart import LOCATIONS, TZ_OFFSETS

# ── Rave Mandala mapping ──
MANDALA_OFFSET = 358.25
GATE_WIDTH = 5.625       # 360 / 64
LINE_WIDTH = 0.9375      # 5.625 / 6

GATE_SEQUENCE = [
    25, 17, 21, 51, 42,  3, 27, 24,  2, 23,
     8, 20, 16, 35, 45, 12, 15, 52, 39, 53,
    62, 56, 31, 33,  7,  4, 29, 59, 40, 64,
    47,  6, 46, 18, 48, 57, 32, 50, 28, 44,
     1, 43, 14, 34,  9,  5, 26, 11, 10, 58,
    38, 54, 61, 60, 41, 19, 13, 49, 30, 55,
    37, 63, 22, 36,
]

GATE_CENTER = {
    1:"G", 2:"G", 3:"Sacral", 4:"Ajna", 5:"Sacral", 6:"Solar Plexus",
    7:"G", 8:"Throat", 9:"Sacral", 10:"G", 11:"Ajna", 12:"Throat",
    13:"G", 14:"Sacral", 15:"G", 16:"Throat", 17:"Ajna", 18:"Spleen",
    19:"Root", 20:"Throat", 21:"Heart", 22:"Solar Plexus", 23:"Throat",
    24:"Ajna", 25:"G", 26:"Heart", 27:"Sacral", 28:"Spleen", 29:"Sacral",
    30:"Solar Plexus", 31:"Throat", 32:"Spleen", 33:"Throat", 34:"Sacral",
    35:"Throat", 36:"Solar Plexus", 37:"Solar Plexus", 38:"Root", 39:"Root",
    40:"Heart", 41:"Root", 42:"Sacral", 43:"Ajna", 44:"Spleen", 45:"Throat",
    46:"G", 47:"Ajna", 48:"Spleen", 49:"Solar Plexus", 50:"Spleen",
    51:"Heart", 52:"Root", 53:"Root", 54:"Root", 55:"Solar Plexus",
    56:"Throat", 57:"Spleen", 58:"Root", 59:"Sacral", 60:"Root", 61:"Head",
    62:"Throat", 63:"Head", 64:"Head",
}

CHANNELS = [
    (1,8), (2,14), (3,60), (4,63), (5,15), (6,59), (7,31), (9,52),
    (10,20), (10,34), (10,57), (11,56), (12,22), (13,33), (16,48),
    (17,62), (18,58), (19,49), (20,34), (20,57), (21,45), (23,43),
    (24,61), (25,51), (26,44), (27,50), (28,38), (29,46), (30,41),
    (32,54), (34,57), (35,36), (37,40), (39,55), (42,53), (47,64),
]

CHANNEL_NAMES = {
    frozenset((1,8)):   "Inspiration",
    frozenset((2,14)):  "The Beat",
    frozenset((3,60)):  "Mutation",
    frozenset((4,63)):  "Logic",
    frozenset((5,15)):  "Rhythm",
    frozenset((6,59)):  "Mating",
    frozenset((7,31)):  "The Alpha",
    frozenset((9,52)):  "Concentration",
    frozenset((10,20)): "Awakening",
    frozenset((10,34)): "Exploration",
    frozenset((10,57)): "Perfected Form",
    frozenset((11,56)): "Curiosity",
    frozenset((12,22)): "Openness",
    frozenset((13,33)): "The Prodigal",
    frozenset((16,48)): "The Wave",
    frozenset((17,62)): "Acceptance",
    frozenset((18,58)): "Judgment",
    frozenset((19,49)): "Synthesis",
    frozenset((20,34)): "Charisma",
    frozenset((20,57)): "The Brainwave",
    frozenset((21,45)): "Money",
    frozenset((23,43)): "Structuring",
    frozenset((24,61)): "Awareness",
    frozenset((25,51)): "Initiation",
    frozenset((26,44)): "Surrender",
    frozenset((27,50)): "Preservation",
    frozenset((28,38)): "Struggle",
    frozenset((29,46)): "Discovery",
    frozenset((30,41)): "Feelings",
    frozenset((32,54)): "Transformation",
    frozenset((34,57)): "Power",
    frozenset((35,36)): "Transitoriness",
    frozenset((37,40)): "Community",
    frozenset((39,55)): "Spirit",
    frozenset((42,53)): "Maturation",
    frozenset((47,64)): "Abstraction",
}

STRATEGY = {
    "Generator": "Wait to respond",
    "Manifesting Generator": "Wait to respond, then inform",
    "Manifestor": "Inform before acting",
    "Projector": "Wait for the invitation",
    "Reflector": "Wait a lunar cycle",
}

NOT_SELF = {
    "Generator": "Frustration",
    "Manifesting Generator": "Frustration & Anger",
    "Manifestor": "Anger",
    "Projector": "Bitterness",
    "Reflector": "Disappointment",
}

ALL_CENTERS = ["Head", "Ajna", "Throat", "G", "Heart", "Solar Plexus", "Sacral", "Spleen", "Root"]
MOTOR_CENTERS = {"Sacral", "Root", "Solar Plexus", "Heart"}

# HD uses 13 bodies: Sun, Earth, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, North Node, South Node
HD_BODIES = [
    ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3), ("Mars", 4),
    ("Jupiter", 5), ("Saturn", 6), ("Uranus", 7), ("Neptune", 8), ("Pluto", 9),
    ("North Node", 10),  # swe.MEAN_NODE
]


def longitude_to_gate_line(longitude: float) -> tuple[int, int]:
    adjusted = (longitude - MANDALA_OFFSET) % 360
    gate_idx = min(int(adjusted / GATE_WIDTH), 63)
    gate = GATE_SEQUENCE[gate_idx]
    line = min(int((adjusted % GATE_WIDTH) / LINE_WIDTH) + 1, 6)
    return gate, line


def _compute_positions(swe, jd: float) -> dict:
    """Compute all 13 HD body positions at a given Julian Day."""
    positions = {}
    for name, pid in HD_BODIES:
        result = swe.calc_ut(jd, pid)
        lon = result[0][0]
        gate, line = longitude_to_gate_line(lon)
        positions[name] = {
            "longitude": round(lon, 4),
            "gate": gate,
            "line": line,
            "center": GATE_CENTER[gate],
            "gate_line": f"{gate}.{line}",
        }
    # Earth = Sun + 180°
    sun_lon = positions["Sun"]["longitude"]
    earth_lon = (sun_lon + 180.0) % 360
    eg, el = longitude_to_gate_line(earth_lon)
    positions["Earth"] = {
        "longitude": round(earth_lon, 4),
        "gate": eg,
        "line": el,
        "center": GATE_CENTER[eg],
        "gate_line": f"{eg}.{el}",
    }
    # South Node = North Node + 180°
    nn_lon = positions["North Node"]["longitude"]
    sn_lon = (nn_lon + 180.0) % 360
    sg, sl = longitude_to_gate_line(sn_lon)
    positions["South Node"] = {
        "longitude": round(sn_lon, 4),
        "gate": sg,
        "line": sl,
        "center": GATE_CENTER[sg],
        "gate_line": f"{sg}.{sl}",
    }
    return positions


def _find_design_jd(swe, birth_jd: float, birth_sun_lon: float) -> float:
    """Find the JD when the Sun was at (birth_sun_lon - 88°) mod 360."""
    target = (birth_sun_lon - 88.0) % 360

    # Coarse search: 1-day steps backward from ~91 days before birth
    best_jd = birth_jd - 88
    best_diff = 999.0
    for day_offset in range(91, 80, -1):
        test_jd = birth_jd - day_offset
        result = swe.calc_ut(test_jd, 0)  # Sun
        sun_lon = result[0][0]
        diff = abs((sun_lon - target + 180) % 360 - 180)
        if diff < best_diff:
            best_diff = diff
            best_jd = test_jd

    # Fine search: 1-minute steps around best_jd, tolerance 0.01°
    minute_step = 1.0 / 1440.0  # 1 minute in days
    search_start = best_jd - 2  # 2 days around best
    best_diff = 999.0
    for i in range(int(4 * 1440)):  # 4 days of minutes
        test_jd = search_start + i * minute_step
        result = swe.calc_ut(test_jd, 0)
        sun_lon = result[0][0]
        diff = abs((sun_lon - target + 180) % 360 - 180)
        if diff < best_diff:
            best_diff = diff
            best_jd = test_jd
        if best_diff < 0.01:
            break

    return best_jd


def _motor_to_throat(defined_channels: list, defined_centers: set) -> bool:
    """BFS: check if any motor center connects to Throat through defined channels."""
    if "Throat" not in defined_centers:
        return False

    # Build adjacency from defined channels
    adj: dict[str, set[str]] = {}
    for ch in defined_channels:
        g1, g2 = ch["gates"]
        c1, c2 = GATE_CENTER[g1], GATE_CENTER[g2]
        if c1 != c2:  # only cross-center channels matter
            adj.setdefault(c1, set()).add(c2)
            adj.setdefault(c2, set()).add(c1)

    # BFS from each motor center
    for motor in MOTOR_CENTERS:
        if motor not in defined_centers:
            continue
        visited = {motor}
        queue = deque([motor])
        while queue:
            current = queue.popleft()
            if current == "Throat":
                return True
            for neighbor in adj.get(current, []):
                if neighbor in defined_centers and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return False


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    if not profile.birth_time_local or not profile.timezone or not profile.location:
        return SystemResult(
            id="human_design",
            name="Human Design",
            certainty="NEEDS_INPUT",
            data={"error": "Requires birth_time_local, timezone, and location"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    try:
        import swisseph as swe
    except ImportError:
        return SystemResult(
            id="human_design",
            name="Human Design",
            certainty="NEEDS_EPHEMERIS",
            data={"error": "pyswisseph not available"},
            interpretation=None,
            constants_version=constants["version"],
            references=[],
            question="Q1_IDENTITY",
        )

    swe.set_ephe_path(None)

    # Resolve coordinates and timezone
    coords = LOCATIONS.get(profile.location)
    if coords is None:
        # Fallback to Cairo
        coords = (26.2361, 50.0393)
    lat, lon = coords

    tz_offset = TZ_OFFSETS.get(profile.timezone, 3)  # default +3 Riyadh

    # Step 1 — Birth JD (UT)
    h, m = map(int, profile.birth_time_local.split(":"))
    ut = (h + m / 60.0) - tz_offset
    birth_jd = swe.julday(profile.dob.year, profile.dob.month, profile.dob.day, ut)

    # Step 2 — Personality positions (birth moment)
    personality = _compute_positions(swe, birth_jd)

    # Step 3 — Design positions (88° solar arc backward)
    birth_sun_lon = personality["Sun"]["longitude"]
    design_jd = _find_design_jd(swe, birth_jd, birth_sun_lon)
    design = _compute_positions(swe, design_jd)

    # Step 4 — Collect all activated gates
    all_gates = set()
    for pos in personality.values():
        all_gates.add(pos["gate"])
    for pos in design.values():
        all_gates.add(pos["gate"])

    # Step 6 — Find defined channels
    defined_channels = []
    for g1, g2 in CHANNELS:
        if g1 in all_gates and g2 in all_gates:
            ch_name = CHANNEL_NAMES.get(frozenset((g1, g2)), "Unknown")
            defined_channels.append({
                "gates": [g1, g2],
                "name": ch_name,
                "centers": [GATE_CENTER[g1], GATE_CENTER[g2]],
            })

    # Step 7 — Defined centers (from channels only)
    defined_centers = set()
    for ch in defined_channels:
        defined_centers.update(ch["centers"])
    defined_centers_sorted = sorted(defined_centers)
    undefined_centers = sorted(c for c in ALL_CENTERS if c not in defined_centers)

    # Step 8 — Motor-to-Throat detection
    m2t = _motor_to_throat(defined_channels, defined_centers)

    # Step 9 — Type
    sacral_defined = "Sacral" in defined_centers
    if len(defined_centers) == 0:
        hd_type = "Reflector"
    elif sacral_defined and m2t:
        hd_type = "Manifesting Generator"
    elif sacral_defined:
        hd_type = "Generator"
    elif m2t:
        hd_type = "Manifestor"
    else:
        hd_type = "Projector"

    # Step 10 — Authority
    if hd_type == "Reflector":
        authority = "Lunar (None)"
    elif "Solar Plexus" in defined_centers:
        authority = "Emotional (Solar Plexus)"
    elif sacral_defined:
        authority = "Sacral"
    elif "Spleen" in defined_centers:
        authority = "Splenic"
    elif "Heart" in defined_centers:
        authority = "Ego/Heart"
    elif "G" in defined_centers:
        authority = "Self-Projected (G)"
    else:
        authority = "None (Mental Projector)"

    # Step 11 — Profile
    hd_profile = f"{personality['Sun']['line']}/{design['Sun']['line']}"

    # Step 12 — Incarnation Cross
    incarnation_cross = (
        f"{personality['Sun']['gate']}/{personality['Earth']['gate']}/"
        f"{design['Sun']['gate']}/{design['Earth']['gate']}"
    )

    strategy = STRATEGY.get(hd_type, "")
    not_self_theme = NOT_SELF.get(hd_type, "")

    channel_names = [ch["name"] for ch in defined_channels]
    channel_summary = ", ".join(channel_names[:4])
    if len(channel_names) > 4:
        channel_summary += f" +{len(channel_names)-4} more"

    interpretation = (
        f"Your Human Design type is {hd_type} with {authority} authority. "
        f"Strategy: {strategy}. "
        f"Profile {hd_profile} defines your archetypal learning and teaching role. "
        f"Incarnation Cross {incarnation_cross} frames the overarching life theme. "
        f"{len(defined_centers)} of 9 centers are defined "
        f"({', '.join(defined_centers_sorted)}), creating consistent, reliable energy. "
        f"Undefined centers ({', '.join(undefined_centers)}) are open to amplification and conditioning from the environment. "
        f"Active channels: {channel_summary}. "
        f"Not-self signature to notice: {not_self_theme}. "
        f"Human Design is a structural map for self-recognition, not prediction. "
        f"The type and authority orient decision-making; the channels and centers describe consistent circuitry. "
        f"Alignment comes through following the strategy, not through willpower or mental override."
    )

    data = {
        "type": hd_type,
        "authority": authority,
        "strategy": strategy,
        "not_self_theme": not_self_theme,
        "profile": hd_profile,
        "incarnation_cross": incarnation_cross,
        "personality": personality,
        "design": design,
        "design_jd": round(design_jd, 6),
        "all_activated_gates": sorted(all_gates),
        "defined_channels": defined_channels,
        "defined_centers": defined_centers_sorted,
        "undefined_centers": undefined_centers,
        "n_defined_centers": len(defined_centers),
    }

    return SystemResult(
        id="human_design",
        name="Human Design",
        certainty="COMPUTED_STRICT",
        data=data,
        interpretation=interpretation,
        constants_version=constants["version"],
        references=[
            "Ra Uru Hu — Human Design: The Definitive Book of Human Design (Jovian Archive, 2011)",
            "Jovian Archive — Rave Mandala gate sequence (standard tropical zodiac mapping)",
            "Swiss Ephemeris (Moshier) — planetary positions",
            "SOURCE_TIER:C — Invented 1987 by Ra Uru Hu (Alan Krakower). No pre-1987 classical source.",
        ],
        question="Q1_IDENTITY",
    )
