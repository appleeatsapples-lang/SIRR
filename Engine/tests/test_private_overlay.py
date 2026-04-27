"""Graceful-degradation tests for the V-3c calibration boundary.

The public engine must remain functional when no private overlay is mounted:
modules that depend on name-root / name-morphology lookups should report
APPROX certainty rather than crashing. When an overlay is supplied, the same
modules return COMPUTED_STRICT or LOOKUP_FIXED.
"""
from __future__ import annotations
import importlib
import json
import os
import sys
from datetime import date
from pathlib import Path

import pytest

ENGINE = Path(__file__).resolve().parent.parent
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from sirr_core.types import InputProfile  # noqa: E402


@pytest.fixture
def fatima_profile():
    """A minimal FATIMA-style profile with no compound positions."""
    return InputProfile(
        subject="TEST SUBJECT",
        arabic="فاطمة أحمد",
        dob=date(1990, 3, 15),
        today=date(2026, 4, 27),
    )


@pytest.fixture
def constants():
    from runner import load_constants
    return load_constants()


def _reset_module_caches():
    """Reset the per-module ``_TABLES`` cache so env-var changes take effect.

    The five lookup-aware modules cache their merged tables at module load.
    Tests that toggle ``SIRR_PRIVATE_OVERLAY`` between runs must clear the
    cache or they will see stale state from an earlier test.
    """
    for name in (
        "modules.arabic_morphology",
        "modules.arabic_roots",
        "modules.name_semantics",
        "modules.arabic_letter_nature",
    ):
        mod = sys.modules.get(name)
        if mod is None:
            mod = importlib.import_module(name)
        if hasattr(mod, "_TABLES"):
            mod._TABLES = None


@pytest.fixture(autouse=True)
def isolate_overlay_env(monkeypatch):
    """Each test starts with no overlay env var and a fresh module cache."""
    monkeypatch.delenv("SIRR_PRIVATE_OVERLAY", raising=False)
    _reset_module_caches()
    yield
    _reset_module_caches()


def test_engine_runs_without_overlay(fatima_profile, constants):
    """No overlay → lookup-dependent modules report APPROX without crashing."""
    from modules import arabic_morphology, arabic_roots, name_semantics
    from modules import arabic_letter_nature, lineage_computation

    morph = arabic_morphology.compute(fatima_profile, constants)
    roots = arabic_roots.compute(fatima_profile, constants)
    sem = name_semantics.compute(fatima_profile, constants)
    letter = arabic_letter_nature.compute(fatima_profile, constants)
    lineage = lineage_computation.compute(fatima_profile, constants)

    assert morph.certainty == "APPROX"
    assert roots.certainty == "APPROX"
    assert sem.certainty == "APPROX"
    # Letter-nature and lineage do not depend on overlay tables.
    assert letter.certainty == "COMPUTED_STRICT"
    assert lineage.certainty == "COMPUTED_STRICT"

    # Output schema preserved even without enrichment.
    assert "word_morphology" in morph.data
    assert "word_roots" in roots.data
    assert "unit_semantics" in sem.data
    assert all(w["wazn"] is None for w in morph.data["word_morphology"])
    assert all(w["root"] is None for w in roots.data["word_roots"])


def test_engine_runs_with_invalid_overlay_path(fatima_profile, constants, monkeypatch):
    """Pointing the env var at a non-existent file is treated as no overlay."""
    monkeypatch.setenv("SIRR_PRIVATE_OVERLAY", "/tmp/_v3c_does_not_exist_42.json")
    _reset_module_caches()

    from modules import arabic_morphology, arabic_roots, name_semantics

    assert arabic_morphology.compute(fatima_profile, constants).certainty == "APPROX"
    assert arabic_roots.compute(fatima_profile, constants).certainty == "APPROX"
    assert name_semantics.compute(fatima_profile, constants).certainty == "APPROX"


def test_engine_runs_with_valid_overlay(fatima_profile, constants, monkeypatch, tmp_path):
    """A synthetic test overlay restores COMPUTED_STRICT / LOOKUP_FIXED."""
    overlay = {
        "schema_version": "1.0",
        "name_roots": {
            "فاطمة": {
                "root": "ف-ط-م",
                "root_letters": ["ف", "ط", "م"],
                "primary_meaning": "to wean",
                "semantic_field": "weaning_separation",
                "form": "I",
                "lane_ref": "test",
            }
        },
        "name_morphology": {
            "فاطمة": {
                "wazn": "فاعلة",
                "wazn_latin": "fā'ila",
                "class": "active_participle",
                "class_ar": "اسم فاعل",
                "form": "I",
                "voice": "active",
            }
        },
    }
    p = tmp_path / "overlay.json"
    p.write_text(json.dumps(overlay, ensure_ascii=False))
    monkeypatch.setenv("SIRR_PRIVATE_OVERLAY", str(p))
    _reset_module_caches()

    from modules import arabic_morphology, arabic_roots, name_semantics

    assert arabic_morphology.compute(fatima_profile, constants).certainty == "COMPUTED_STRICT"
    assert arabic_roots.compute(fatima_profile, constants).certainty == "COMPUTED_STRICT"
    assert name_semantics.compute(fatima_profile, constants).certainty == "LOOKUP_FIXED"


def test_compound_metadata_passed_via_profile(constants, monkeypatch, tmp_path):
    """``profile.compound_metadata`` drives compound detection — no module hardcoding."""
    overlay = {
        "schema_version": "1.0",
        "name_roots": {
            "ألف": {"root": "ا-ل-ف", "root_letters": ["ا", "ل", "ف"], "primary_meaning": "first", "semantic_field": "ordinal", "form": "I", "lane_ref": ""},
            "باء": {"root": "ب-ا-ء", "root_letters": ["ب", "ا", "ء"], "primary_meaning": "second", "semantic_field": "ordinal", "form": "I", "lane_ref": ""},
        },
        "name_morphology": {
            "ألف": {"wazn": "فعل", "wazn_latin": "fa'l", "class": "noun", "class_ar": "اسم", "form": "I", "voice": "n/a"},
            "باء": {"wazn": "فعل", "wazn_latin": "fa'l", "class": "adjective", "class_ar": "صفة", "form": "I", "voice": "n/a"},
        },
    }
    p = tmp_path / "overlay.json"
    p.write_text(json.dumps(overlay, ensure_ascii=False))
    monkeypatch.setenv("SIRR_PRIVATE_OVERLAY", str(p))
    _reset_module_caches()

    profile = InputProfile(
        subject="TEST",
        arabic="أحمد عمر ألف باء حسن",
        dob=date(1990, 1, 1),
        today=date(2026, 1, 1),
        compound_metadata={2: ("ألف", "باء")},
    )

    from modules import arabic_morphology, arabic_roots, name_semantics

    morph_result = arabic_morphology.compute(profile, constants)
    compounds = morph_result.data["compound_names"]
    assert len(compounds) == 1
    assert compounds[0]["position"] == 2
    assert compounds[0]["compound"] == "ألف باء"
    assert compounds[0]["structure"] == "noun + adjective"

    sem_result = name_semantics.compute(profile, constants)
    compound_units = [u for u in sem_result.data["unit_semantics"] if u["is_compound"]]
    assert len(compound_units) == 1
    assert compound_units[0]["unit"] == "ألف باء"

    # Module-level constants must be empty: no profile data leaks into the module.
    assert arabic_morphology.COMPOUND_STRUCTURES == {}
    assert arabic_roots.COMPOUND_POSITIONS == {}
