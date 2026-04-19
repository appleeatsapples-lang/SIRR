"""Tests for the transliteration utility."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.transliterate import transliterate_to_arabic, transliterate_to_hebrew


# ── Arabic known-correct pairs ──

def test_fatima():
    assert transliterate_to_arabic("FATIMA") == "فاطمة"

def test_omar():
    assert transliterate_to_arabic("OMAR") == "عمر"

def test_ahmed():
    assert transliterate_to_arabic("AHMED") == "أحمد"

def test_muhammad():
    assert transliterate_to_arabic("MUHAMMAD") == "محمد"

def test_sarah():
    assert transliterate_to_arabic("SARAH") == "سارة"

def test_full_name_synthetic():
    result = transliterate_to_arabic("FATIMA AHMED OMAR ALKATIB")
    assert result == "فاطمة أحمد عمر الكاتيب"

def test_john():
    result = transliterate_to_arabic("JOHN")
    assert result == "جون"

def test_david():
    result = transliterate_to_arabic("DAVID")
    assert result == "دافيد"

def test_michael():
    result = transliterate_to_arabic("MICHAEL")
    assert result == "مايكل"

def test_william():
    result = transliterate_to_arabic("WILLIAM")
    assert result == "وليام"


# ── Determinism ──

def test_deterministic():
    """Same input must always produce identical output."""
    for _ in range(10):
        assert transliterate_to_arabic("FATIMA AHMED") == "فاطمة أحمد"

def test_case_insensitive():
    """Should handle mixed case."""
    assert transliterate_to_arabic("Fatima") == transliterate_to_arabic("FATIMA")
    assert transliterate_to_arabic("omar") == transliterate_to_arabic("OMAR")


# ── Edge cases ──

def test_empty():
    assert transliterate_to_arabic("") == ""
    assert transliterate_to_arabic("   ") == ""

def test_single_letter():
    result = transliterate_to_arabic("A")
    assert result == "ا"

def test_digraph_sh():
    result = transliterate_to_arabic("SHAH")
    assert "ش" in result  # SH → ش


# ── Hebrew basic ──

def test_hebrew_david():
    result = transliterate_to_hebrew("DAVID")
    assert "ד" in result  # D present
    assert len(result) >= 3

def test_hebrew_sarah():
    result = transliterate_to_hebrew("SARAH")
    assert "ש" in result or "ס" in result  # S or SH present

def test_hebrew_deterministic():
    for _ in range(10):
        assert transliterate_to_hebrew("DAVID") == transliterate_to_hebrew("DAVID")

def test_hebrew_empty():
    assert transliterate_to_hebrew("") == ""


# ── Canonical override expansion regression ──

class TestFullNasabCanonical:
    """Regression test: full 8-word Arab nasab produces canonical Arabic spellings."""

    def test_full_nasab_canonical(self):
        """Full 8-word nasab must produce canonical Arabic spellings end-to-end."""
        result = transliterate_to_arabic(
            "FATIMA AHMED OMAR ALKATIB HASSAN MAHMOUD SAMIR WAEL"
        )
        expected = "\u0641\u0627\u0637\u0645\u0629 \u0623\u062d\u0645\u062f \u0639\u0645\u0631 \u0627\u0644\u0643\u0627\u062a\u064a\u0628 \u062d\u0633\u0646 \u0645\u062d\u0645\u0648\u062f \u0633\u0645\u064a\u0631 \u0648\u0627\u0626\u0644"
        # فاطمة أحمد عمر الكاتيب حسن محمود سمير وائل
        assert result == expected, f"Got: {result!r}\nExpected: {expected!r}"

    def test_mohammad_variant(self):
        """MOHAMMAD (O-variant, double-M ending) must produce محمد."""
        assert transliterate_to_arabic("MOHAMMAD") == "\u0645\u062d\u0645\u062f"

    def test_wasfi(self):
        """WASFI must produce وصفي (emphatic ص, not س)."""
        assert transliterate_to_arabic("WASFI") == "\u0648\u0635\u0641\u064a"


class TestCommonArabNames:
    """Smoke-test a sampling of newly added Arab names for canonical correctness."""

    def test_mustafa_emphatic(self):
        """MUSTAFA must use ص and ط and end with ى."""
        assert transliterate_to_arabic("MUSTAFA") == "\u0645\u0635\u0637\u0641\u0649"

    def test_tariq_emphatic(self):
        """TARIQ must use emphatic ط and ق."""
        assert transliterate_to_arabic("TARIQ") == "\u0637\u0627\u0631\u0642"

    def test_hossam(self):
        assert transliterate_to_arabic("HOSSAM") == "\u062d\u0633\u0627\u0645"

    def test_miral(self):
        """MIRAL must produce ميرال."""
        assert transliterate_to_arabic("MIRAL") == "\u0645\u064a\u0631\u0627\u0644"

    def test_noor_variants_identical(self):
        """NOOR / NUR / NOUR must all produce the same Arabic نور."""
        noor_ar = "\u0646\u0648\u0631"
        assert transliterate_to_arabic("NOOR") == noor_ar
        assert transliterate_to_arabic("NUR") == noor_ar
        assert transliterate_to_arabic("NOUR") == noor_ar


class TestFallbackPreserved:
    """Names NOT in override dict should still transliterate phonetically."""

    def test_unknown_name_phonetic(self):
        """ALKATIB is not an override — phonetic fallback should produce الكاتيب."""
        result = transliterate_to_arabic("ALKATIB")
        assert result == "\u0627\u0644\u0643\u0627\u062a\u064a\u0628", \
            f"Got: {result!r}"

    def test_existing_overrides_unchanged(self):
        """Existing overrides must still work."""
        assert transliterate_to_arabic("MUHAMMAD") == "\u0645\u062d\u0645\u062f"
        assert transliterate_to_arabic("OMAR") == "\u0639\u0645\u0631"
        assert transliterate_to_arabic("FATIMA") == "\u0641\u0627\u0637\u0645\u0629"
