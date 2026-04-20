"""Regression guard: empty module cards should be suppressed.

Before this test's fix, ~29% of cards in production readings were
em-dash stubs ('—') with no value / no secondary / no interpretation.
Looked broken. Fix in html_reading.py filters them out at card-build
time so only modules with real content survive into the rendered page.

These tests exercise the is_empty decision inline rather than spinning
up the full html_reading.generate_html pipeline (which needs a lot of
input scaffolding).
"""
from __future__ import annotations


def _is_empty_card(primary_val: str, secondary: str, short_interp: str) -> bool:
    """Mirrors the is_empty check in html_reading.py card loop."""
    return (
        (not primary_val or primary_val.strip() in ("—", "-", "")) and
        not secondary and
        not short_interp
    )


def test_pure_em_dash_stub_is_empty():
    assert _is_empty_card("—", "", "") is True


def test_whitespace_em_dash_stub_is_empty():
    assert _is_empty_card("  —  ", "", "") is True


def test_empty_string_is_empty():
    assert _is_empty_card("", "", "") is True


def test_plain_hyphen_is_empty():
    assert _is_empty_card("-", "", "") is True


def test_value_present_not_empty():
    assert _is_empty_card("7", "", "") is False


def test_secondary_saves_the_card():
    # No primary but has secondary → render (some modules are secondary-heavy)
    assert _is_empty_card("—", "Taurus rising", "") is False


def test_interp_saves_the_card():
    # No primary but has interpretation → render
    assert _is_empty_card("—", "", "You are moved by...") is False


def test_all_three_present_not_empty():
    assert _is_empty_card("5", "sub", "text") is False


def test_none_values_handled():
    # Defensive: some fields may come back as None, not empty string
    assert _is_empty_card(None, None, None) is True
