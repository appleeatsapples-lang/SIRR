"""Robustness analysis for convergence claims.

Tests how stable convergence claims are when modules are removed (jackknife)
or when field whitelists are perturbed.

DeepSeek Recommendation: "Run leave-one-out on each convergence claim.
If removing a single module drops a claim below threshold, flag it as fragile."
"""
from __future__ import annotations
from typing import Any


def jackknife_convergence(convergence: dict, all_results: list[dict]) -> dict[str, Any]:
    """Leave-one-out stability test for a convergence claim.

    For each contributing system, remove it and check if the claim
    still meets thresholds (≥3 systems, ≥2 groups).

    Returns:
        fragile: bool — True if any single removal breaks the claim
        removed_systems: list of systems whose removal breaks the claim
        stability_ratio: fraction of removals that preserve the claim
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")


def whitelist_perturbation(convergence_fields: dict,
                           results: list[dict],
                           n_perturbations: int = 100) -> dict[str, Any]:
    """Test convergence stability under random field whitelist changes.

    Randomly adds/removes fields from CONVERGENCE_FIELDS and measures
    how convergence counts change. Stable claims survive perturbation.
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")
