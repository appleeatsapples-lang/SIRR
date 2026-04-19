"""
SIRR Engine — Interpretation Loader
====================================
Loads interpretation JSON files and attaches them to SystemResult objects.

Usage:
    from interpretation_loader import InterpretationLoader, attach_interpretations

    loader = InterpretationLoader().load_all()
    print(loader.coverage_report(ALL_MODULE_IDS))

    # Attach to engine output
    results = attach_interpretations(engine_results, loader, lang="en")

Directory: expansion/chatgpt_interpretations/
"""

import json
from pathlib import Path
from typing import Optional, Dict, List


class Interpretation:
    """Single module interpretation with bilingual text."""

    def __init__(self, system_id: str, en: str, ar: str, version: str = "v1.0",
                 en_fallback: str = "", ar_fallback: str = ""):
        self.system_id = system_id
        self.en = en
        self.ar = ar
        self.version = version
        # Optional fallback text for conditional templates
        self.en_fallback = en_fallback
        self.ar_fallback = ar_fallback

    def to_dict(self) -> dict:
        return {
            "system_id": self.system_id,
            "version": self.version,
            "interpretation_en": self.en,
            "interpretation_ar": self.ar,
        }

    def __repr__(self):
        return f"Interpretation({self.system_id}, v{self.version})"


class InterpretationLoader:
    """
    Loads all interpretation JSON batches and provides lookup by system_id.
    """

    # ID normalization map — fixes ChatGPT drift from earlier sessions
    ID_FIXES = {
        "avgad_temurah": "avgad",
        "sabian_symbol": "sabian",
        "annual_profection": "profection",
        "i_ching": "iching",
        "zodiac_and_nine_star": None,  # was split
        "bazi": "bazi_pillars",
    }

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = str(Path(__file__).parent / "expansion" / "chatgpt_interpretations")
        self.base_dir = Path(base_dir)
        self._store: Dict[str, Interpretation] = {}
        self._load_errors: list = []

    def load_all(self) -> "InterpretationLoader":
        """Load all JSON files from the interpretations directory."""
        if not self.base_dir.exists():
            self._load_errors.append(f"Directory not found: {self.base_dir}")
            return self

        for f in sorted(self.base_dir.glob("*.json")):
            self._load_file(f)

        return self

    def _load_file(self, filepath: Path):
        """Load a single JSON batch file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle nested "interpretations" dict format (batch 18+)
            if isinstance(data, dict) and "interpretations" in data:
                items = []
                for sid, body in data["interpretations"].items():
                    items.append({
                        "system_id": sid,
                        "interpretation_en": body.get("interpretation", body.get("interpretation_en", "")),
                        "interpretation_ar": body.get("ar_interpretation", body.get("interpretation_ar", "")),
                        "version": body.get("version", "v1.0"),
                    })
                data = items

            if not isinstance(data, list):
                data = [data]

            for item in data:
                sid = item.get("system_id", "")

                # Apply ID fixes
                if sid in self.ID_FIXES:
                    fixed = self.ID_FIXES[sid]
                    if fixed is None:
                        continue
                    sid = fixed

                if not sid:
                    self._load_errors.append(f"Missing system_id in {filepath.name}")
                    continue

                # Support conditional templates (primary + fallback)
                en_primary = item.get("interpretation_en_primary", "")
                ar_primary = item.get("interpretation_ar_primary", "")
                en_fallback = item.get("interpretation_en_fallback", "")
                ar_fallback = item.get("interpretation_ar_fallback", "")

                interp = Interpretation(
                    system_id=sid,
                    en=en_primary or item.get("interpretation_en", ""),
                    ar=ar_primary or item.get("interpretation_ar", ""),
                    version=item.get("version", "v1.0"),
                    en_fallback=en_fallback,
                    ar_fallback=ar_fallback,
                )
                self._store[sid] = interp

        except json.JSONDecodeError as e:
            self._load_errors.append(f"JSON error in {filepath.name}: {e}")
        except Exception as e:
            self._load_errors.append(f"Error loading {filepath.name}: {e}")

    def get(self, system_id: str) -> Optional[Interpretation]:
        """Look up interpretation by system_id."""
        return self._store.get(system_id)

    def get_text(self, system_id: str, lang: str = "en") -> Optional[str]:
        """Get just the interpretation text for a module."""
        interp = self._store.get(system_id)
        if not interp:
            return None
        return interp.en if lang == "en" else interp.ar

    def has(self, system_id: str) -> bool:
        return system_id in self._store

    @property
    def loaded_ids(self) -> list:
        return sorted(self._store.keys())

    @property
    def count(self) -> int:
        return len(self._store)

    @property
    def errors(self) -> list:
        return self._load_errors

    def coverage_report(self, all_module_ids: list) -> dict:
        """Report coverage against full module list."""
        missing = [mid for mid in all_module_ids if mid not in self._store]
        interpreted = len(all_module_ids) - len(missing)
        return {
            "total_modules": len(all_module_ids),
            "interpreted": interpreted,
            "missing": missing,
            "coverage_pct": round(interpreted / len(all_module_ids) * 100, 1) if all_module_ids else 0,
        }


def _flatten_data(data: dict) -> dict:
    """
    Pre-process module data to surface nested values as top-level keys
    for placeholder resolution. Returns a new dict with flattened keys
    added (does not modify original).
    """
    flat = dict(data)

    # minimum_viable_signature: extract from facts list
    if "facts" in data and isinstance(data["facts"], list):
        for fact in data["facts"]:
            fname = fact.get("fact", "")
            if fname == "dominant_root":
                flat["dominant_root"] = fact.get("value")
                flat["dominant_axis_count"] = fact.get("support")
            elif fname == "structural_voice":
                flat["activity_mode"] = fact.get("value")
            elif fname == "semantic_center":
                flat["semantic_center_pct"] = fact.get("ratio")
            elif fname == "structural_balance":
                flat["coefficient"] = fact.get("coefficient")
            elif fname == "void_geometry":
                vc = fact.get("void_center")
                flat["matrix_void_status"] = "center absent" if vc else "center present"
                flat["void_count"] = fact.get("total_voids")

    # midpoints: extract lead planet from activations list
    if "activations" in data and isinstance(data["activations"], list):
        from collections import Counter
        planets = Counter(a.get("planet", "") for a in data["activations"] if a.get("planet"))
        if planets:
            lead, count = planets.most_common(1)[0]
            flat["lead_planet"] = lead
            flat["lead_count"] = count
        flat.setdefault("activated_count", data.get("activation_count"))

    # house_system: surface ascending sign as first_house_sign
    if "ascending_sign" in data:
        flat["first_house_sign"] = data["ascending_sign"]

    # sect: surface chart_sect as sect_type
    if "chart_sect" in data:
        flat["sect_type"] = data["chart_sect"]

    # hijri: surface birth_* fields as hijri_* aliases
    if "birth_month_name" in data:
        flat["hijri_month_name"] = data["birth_month_name"]
    if "birth_day" in data and "hijri_day" not in data:
        flat["hijri_day"] = data["birth_day"]
    if "birth_year" in data and "hijri_year" not in data:
        flat["hijri_year"] = data["birth_year"]

    # hebrew_calendar: surface holiday as holiday_if_any
    if "holiday" in data:
        flat["holiday_if_any"] = data["holiday"] or "none"

    # nayin: surface nayin_english as nayin_name
    if "nayin_english" in data:
        flat["nayin_name"] = data["nayin_english"]
    if "element" in data and "nayin_element" not in data:
        flat["nayin_element"] = data["element"]

    # taksir: surface depth as taksir_depth, first_column as first_column_letter
    if "depth" in data and "taksir_depth" not in data:
        flat["taksir_depth"] = data["depth"]
    if "first_column" in data and "first_column_letter" not in data:
        fc = data["first_column"]
        if isinstance(fc, str) and fc:
            flat["first_column_letter"] = fc[0]  # first unique letter
        else:
            flat["first_column_letter"] = fc

    # akan_kra_din: surface kra_name as kra_din, day_akan as soul_day
    if "kra_name" in data:
        flat["kra_din"] = data["kra_name"]
    if "day_akan" in data:
        flat["soul_day"] = data["day_akan"]
    if "element" in data and "soul_element" not in data:
        flat["soul_element"] = data["element"]

    # zwds_si_hua_palace: surface year_stem, lu_star, ji_star
    if "year_stem" in data:
        flat["heavenly_stem"] = data["year_stem"]
    if "lu_star" in data:
        flat["hua_lu_star"] = data["lu_star"]
    if "ji_star" in data:
        flat["hua_ji_star"] = data["ji_star"]

    # hijri_calendar_encoding: surface year_digit_root as year_root, is_sacred_month as sacred_month
    if "year_digit_root" in data and "year_root" not in flat:
        flat["year_root"] = data["year_digit_root"]
    if "is_sacred_month" in data and "sacred_month" not in flat:
        flat["sacred_month"] = data["is_sacred_month"]

    # essential_dignities: surface total_dignity_score
    if "planet_conditions" in data and "total_dignity_score" not in flat:
        # Sum dignity scores from planet conditions if available
        pcs = data["planet_conditions"]
        if isinstance(pcs, dict):
            total = sum(pc.get("dignity_score", 0) for pc in pcs.values() if isinstance(pc, dict))
            flat["total_dignity_score"] = total

    return flat


def _format_interp(template: str, data: dict) -> str:
    """
    Format {placeholder} tokens in an interpretation template using
    the module's engine data dict.

    Uses an alias map to resolve generic placeholder names (e.g., {total})
    to module-specific data keys (e.g., abjad_total, total_gematria).
    Also flattens known nested structures before resolution.

    Graceful fallback: if a placeholder has no matching engine field,
    leave the literal placeholder and log a warning to stderr.
    """
    import re
    import sys

    # Flatten nested data structures into top-level keys
    flat = _flatten_data(data)

    # Generic placeholder → list of module-specific keys to try (in priority order)
    _ALIASES = {
        "total": [
            "total", "value", "result", "sum",
            "total_gematria", "chaldean_total", "abjad_total",
            "ordinal_sum", "cipher_sum", "chronogram_total",
            "arabic_sum", "gadol_total", "total_weight",
            "expanded_value", "original_value", "millman_compound",
            "compound_number", "base_number", "solar_value",
            "expression_card_number",
        ],
        "root": [
            "root", "reduced", "digital_root", "reduction",
            "gematria_root", "chaldean_root", "abjad_root",
            "ordinal_root", "cipher_root", "chronogram_root",
            "arabic_root", "gadol_root", "weight_root",
            "hidden_root", "millman_final", "compound_root",
        ],
        "archetype": [
            "archetype", "dominant_archetype", "top_archetype",
            "consensus_archetype", "primary_temperament",
            "dominant_element", "natal_bird", "birth_card",
            "expression_card_name", "compound_name", "type",
        ],
    }

    def _resolve(key):
        """Try the key directly in flat data, then try aliases."""
        if key in flat:
            return flat[key]
        aliases = _ALIASES.get(key, [])
        for alias in aliases:
            if alias in flat:
                return flat[alias]
        return None

    def _replace(match):
        key = match.group(1)
        val = _resolve(key)
        if val is not None:
            return str(val)
        print(f"[interp_loader] WARNING: placeholder {{{key}}} has no matching field in engine data", file=sys.stderr)
        return match.group(0)  # leave literal placeholder

    return re.sub(r"\{(\w+)\}", _replace, template)


def attach_interpretations(engine_results: list, loader: InterpretationLoader, lang: str = "en") -> list:
    """
    Attach interpretation text to engine result dicts.
    Modifies results in-place and returns them.

    - Skips override when the module already provides a non-None interpretation
      (module-source interpretations take priority over batch-file text).
    - When an interp string contains {placeholder} syntax, formats it at
      attach-time using the module's engine data dict.
    """
    for result in engine_results:
        # Handle both dict and SystemResult
        if hasattr(result, "id"):
            sid = result.id
        elif isinstance(result, dict):
            sid = result.get("id", result.get("system_id", ""))
        else:
            continue

        # Skip override if module-source already provides interpretation
        existing = None
        if hasattr(result, "interpretation"):
            existing = result.interpretation
        elif isinstance(result, dict):
            existing = result.get("interpretation")
        if existing is not None and existing != "":
            continue

        interp = loader.get(sid)
        if interp:
            # Get the engine data dict for placeholder formatting
            if isinstance(result, dict):
                data = result.get("data", {})
            elif hasattr(result, "data") and isinstance(result.data, dict):
                data = result.data
            else:
                data = {}

            en_text = _format_interp(interp.en, data) if interp.en else ""
            ar_text = _format_interp(interp.ar, data) if interp.ar else ""

            if hasattr(result, "__dict__"):
                result.interpretation = en_text if lang == "en" else ar_text
                result.ar_interpretation = ar_text if lang == "en" else en_text
            elif isinstance(result, dict):
                result["interpretation"] = en_text if lang == "en" else ar_text
                result["ar_interpretation"] = ar_text if lang == "en" else en_text
                result["interpretation_version"] = interp.version

    return engine_results


# All 145 module IDs for coverage checking
ALL_MODULE_IDS = [
    # Core
    "julian", "biorhythm", "mayan", "geomancy", "iching", "wafq", "essence",
    "cardology", "nayin", "compound", "sabian", "challenges", "bridges",
    "attitude", "profection", "firdaria", "notarikon", "atbash", "albam",
    "temperament", "bazi_growth", "vedic_tithi", "vedic_yoga",
    # Batch 1-3
    "pinnacles", "personal_year", "karmic_debt", "lo_shu_grid",
    "hidden_passion", "subconscious_self", "maturity",
    "abjad_kabir", "abjad_saghir", "abjad_wusta", "abjad_maghribi", "hijri",
    "solar_lunar", "elemental_letters", "luminous_dark",
    "decan", "day_ruler", "tarot_birth", "dwad",
    # Batch 5-7
    "hebrew_gematria", "avgad", "tree_of_life", "hebrew_calendar",
    "chinese_zodiac", "nine_star_ki", "flying_star", "bazi_pillars",
    "nakshatra", "manazil", "vimshottari",
    # Phase 2 + Batch 8
    "chaldean", "ifa", "egyptian_decan",
    "taksir", "bast_kasr", "istikhara_adad", "zakat_huruf", "jafr", "buduh",
    # Batch 9
    "cornerstone", "life_purpose", "steiner_cycles", "enneagram_dob",
    "tarot_year", "tarot_name", "latin_ordinal", "mandaean_gematria",
    # Batch 10
    "greek_isopsephy", "coptic_isopsephy", "armenian_gematria",
    "georgian_gematria", "agrippan", "thelemic_gematria", "trithemius",
    # Batch 11-12
    "planetary_hours", "god_of_day", "celtic_tree", "ogham", "birth_rune",
    "bazi_daymaster", "bazi_luck_pillars", "bazi_hidden_stems",
    "bazi_ten_gods", "bazi_combos", "bazi_shensha",
    # Batch 13
    "bazhai", "meihua", "pawukon", "primbon", "tibetan_mewa",
    "dreamspell", "tonalpohualli", "ethiopian_asmat",
    "rose_cross_sigil", "planetary_kameas", "ars_magna", "gd_correspondences",
    # Modules 110-113
    "weton", "planetary_joy", "akan_kra_din", "persian_abjad",
    # Ephemeris Phase 1-3
    "natal_chart", "house_system", "aspects",
    "essential_dignities", "sect", "arabic_parts",
    "solar_return", "progressions", "fixed_stars",
    "antiscia", "yogini_dasha", "ashtottari_dasha",
    "zi_wei_dou_shu", "shadbala",
    "almuten", "reception", "declinations", "midpoints", "harmonic_charts",
    "zodiacal_releasing", "solar_arc", "dorothean_chronocrators",
    "ashtakavarga", "shodashavarga", "tasyir", "kalachakra_dasha",
    # Batch 18a-b
    "bonification", "zairja", "qimen", "liu_ren",
    "primary_directions", "chara_dasha", "sarvatobhadra", "tajika", "kp_system",
    # Batch 19
    "taiyi", "onmyodo", "uranian",
    # Batch 20
    "nadi_amsa", "maramataka",
    # Batch 21a
    "babylonian_horoscope",
    # Batch 21b
    "sudarshana",
]


if __name__ == "__main__":
    loader = InterpretationLoader().load_all()

    print(f"Loaded: {loader.count} interpretations")
    print(f"IDs: {loader.loaded_ids}")

    if loader.errors:
        print(f"\nErrors:")
        for e in loader.errors:
            print(f"  - {e}")

    report = loader.coverage_report(ALL_MODULE_IDS)
    print(f"\nCoverage: {report['interpreted']}/{report['total_modules']} ({report['coverage_pct']}%)")
    if report["missing"]:
        print(f"Missing: {report['missing']}")
