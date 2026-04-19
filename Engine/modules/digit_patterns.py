"""Digit Patterns — Numeric Structural Analysis — COMPUTED_STRICT
Analyzes the abjad total's digit-level properties: digit sum, digit product,
reverse, prime factorization, palindromic properties.
"""
from __future__ import annotations
import math
from sirr_core.types import InputProfile, SystemResult
from sirr_core.utils import reduce_number


def _prime_factors(n: int) -> list[int]:
    """Return sorted list of prime factors with multiplicity."""
    if n < 2:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def _is_palindromic(n: int) -> bool:
    s = str(n)
    return s == s[::-1]


def compute(profile: InputProfile, constants: dict, **kwargs) -> SystemResult:
    abjad = constants["arabic_letters"]["abjad_kabir"]
    name = profile.arabic.replace(" ", "")
    total = sum(abjad.get(ch, 0) for ch in name)

    digits = [int(d) for d in str(total)]
    digit_sum = sum(digits)
    digit_product = math.prod(digits) if all(d != 0 for d in digits) else 0
    digit_sum_root = reduce_number(digit_sum, keep_masters=())
    reverse_num = int(str(total)[::-1])
    reverse_sum_root = reduce_number(reverse_num, keep_masters=())
    is_palindrome = _is_palindromic(total)
    prime_factors = _prime_factors(total)
    unique_primes = sorted(set(prime_factors))
    is_prime = len(prime_factors) == 1 and prime_factors[0] == total

    # DOB digit analysis
    dob_digits = [int(d) for d in f"{profile.dob.year}{profile.dob.month:02d}{profile.dob.day:02d}"]
    dob_digit_sum = sum(dob_digits)
    dob_digit_root = reduce_number(dob_digit_sum, keep_masters=())

    # Cross-check: do abjad digits and DOB digits share a root?
    roots_match = digit_sum_root == dob_digit_root

    return SystemResult(
        id="digit_patterns",
        name="Digit Patterns (أنماط الأرقام)",
        certainty="COMPUTED_STRICT",
        data={
            "module_class": "primary",
            "abjad_total": total,
            "digits": digits,
            "digit_sum": digit_sum,
            "digit_sum_root": digit_sum_root,
            "digit_product": digit_product,
            "reverse": reverse_num,
            "reverse_root": reverse_sum_root,
            "is_palindrome": is_palindrome,
            "prime_factors": prime_factors,
            "unique_primes": unique_primes,
            "is_prime": is_prime,
            "dob_digit_sum": dob_digit_sum,
            "dob_digit_root": dob_digit_root,
            "roots_match": roots_match,
        },
        interpretation=None,
        constants_version=constants["version"],
        references=["Abjad Kabir total digit analysis — structural number theory"],
        question="Q1_IDENTITY"
    )
