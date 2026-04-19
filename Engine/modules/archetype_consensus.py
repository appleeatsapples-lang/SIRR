"""
Archetype Consensus (Cross-Tradition Archetype Bridge)
───────────────────────────────────────────────────────
Class C / META — collects archetypal/symbolic assignments from multiple
systems and finds convergent themes.

Systems polled:
  - Tarot birth cards → Major Arcana archetype
  - Enneagram → personality archetype
  - Gene Keys → shadow/gift/siddhi archetype
  - Human Design → type archetype
  - Nakshatra → deity/quality archetype
  - Tree of Life → sephirotic archetype

Algorithm:
  1. Extract archetype/theme keywords from each system
  2. Cluster into meta-themes (Leader, Seeker, Healer, Builder, etc.)
  3. Count theme frequency → consensus archetype

Source: Cross-tradition structural comparison
SOURCE_TIER: C (meta-interpretive bridge)
"""
from __future__ import annotations
from sirr_core.types import InputProfile, SystemResult


# Keyword → meta-theme mapping
THEME_KEYWORDS = {
    "Leader": {"emperor", "king", "leader", "authority", "power", "manifestor", "challenger", "mars", "sun", "aries", "leo", "assertive"},
    "Seeker": {"hermit", "investigator", "seeker", "wisdom", "knowledge", "projector", "mercury", "virgo", "gemini", "analytical"},
    "Healer": {"temperance", "healer", "healing", "nurture", "kapha", "moon", "cancer", "pisces", "empathy", "helper"},
    "Builder": {"empress", "builder", "earth", "taurus", "capricorn", "saturn", "foundation", "structure", "generator"},
    "Transformer": {"death", "tower", "transformation", "scorpio", "pluto", "rebirth", "phoenix", "pitta", "fire", "intensity"},
    "Communicator": {"magician", "mercury", "communicator", "air", "gemini", "aquarius", "messenger", "hermes"},
    "Mystic": {"high_priestess", "moon", "mystical", "intuitive", "reflector", "pisces", "neptune", "spiritual", "mystic"},
    "Creator": {"star", "creator", "venus", "art", "beauty", "libra", "creative", "individualist"},
}


def _classify_theme(text: str) -> str | None:
    """Match text against theme keywords."""
    if not text:
        return None
    lower = text.lower().replace("-", "_").replace(" ", "_")
    best_theme = None
    best_score = 0
    for theme, keywords in THEME_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_theme = theme
    return best_theme if best_score > 0 else None


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    all_results = kwargs.get("all_results", [])

    votes: dict[str, int] = {}
    system_themes = {}

    for r in all_results:
        if not r.data:
            continue

        texts_to_check = []

        if r.id == "tarot_birth":
            texts_to_check.append(r.data.get("card_name", ""))
            texts_to_check.append(r.data.get("archetype", ""))
        elif r.id == "enneagram_dob":
            texts_to_check.append(r.data.get("type_name", ""))
        elif r.id == "enneagram_deeper":
            texts_to_check.append(r.data.get("type_name", ""))
            texts_to_check.append(r.data.get("harmonic_group", ""))
        elif r.id == "human_design":
            texts_to_check.append(r.data.get("type", ""))
            texts_to_check.append(r.data.get("authority", ""))
        elif r.id == "gene_keys":
            for gate_info in (r.data.get("gates") or {}).values():
                if isinstance(gate_info, dict):
                    texts_to_check.append(gate_info.get("gift", ""))
                    texts_to_check.append(gate_info.get("siddhi", ""))
        elif r.id == "nakshatra":
            texts_to_check.append(r.data.get("quality", ""))
            texts_to_check.append(r.data.get("deity", ""))
        elif r.id == "tree_of_life":
            texts_to_check.append(r.data.get("sephirah", ""))
            texts_to_check.append(r.data.get("english", ""))
        elif r.id == "sephirotic_path_analysis":
            texts_to_check.append(r.data.get("dominant_pillar", ""))

        # Classify each text snippet
        for text in texts_to_check:
            theme = _classify_theme(str(text))
            if theme:
                votes[theme] = votes.get(theme, 0) + 1
                if r.id not in system_themes:
                    system_themes[r.id] = []
                system_themes[r.id].append({"text": text, "theme": theme})

    total_votes = sum(votes.values())
    if total_votes == 0:
        consensus = None
        agreement = 0.0
    else:
        consensus = max(votes, key=votes.get)
        agreement = round(votes[consensus] / total_votes, 3)

    sorted_themes = sorted(votes.items(), key=lambda x: -x[1])
    secondary = sorted_themes[1][0] if len(sorted_themes) > 1 else None

    return SystemResult(
        id="archetype_consensus",
        name="Archetype Consensus (Cross-Tradition)",
        certainty="META",
        data={
            "votes": votes,
            "consensus_archetype": consensus,
            "consensus_count": votes.get(consensus, 0) if consensus else 0,
            "secondary_archetype": secondary,
            "total_votes": total_votes,
            "total_systems": len(system_themes),
            "agreement_score": agreement,
            "system_themes": system_themes,
            "module_class": "meta",
        },
        interpretation=None,
        constants_version=constants.get("version", ""),
        references=["Cross-tradition structural comparison"],
        question="Q6_SYNTHESIS",
    )
