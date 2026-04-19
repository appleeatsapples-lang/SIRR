"""Null model generators for convergence significance testing.

Implements permutation-based and bootstrap null distributions to assess
whether observed convergence counts exceed chance expectation.

DeepSeek Recommendation: "Current MC baseline uses random name+DOB pairs.
Add permutation tests that shuffle module outputs while preserving the
independence group structure."
"""
from __future__ import annotations
from typing import Any


def permutation_null(results: list[dict], n_permutations: int = 10000,
                     seed: int = 42) -> dict[str, Any]:
    """Generate null distribution by permuting module outputs within groups.

    Preserves independence group structure while breaking genuine convergence.
    Returns distribution of max convergence counts under H0.
    """
    # TODO: Implement when DeepSeek raw validation spec arrives
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")


def bootstrap_null(results: list[dict], n_bootstrap: int = 10000,
                   seed: int = 42) -> dict[str, Any]:
    """Bootstrap resampling null distribution.

    Resamples modules with replacement within each independence group.
    Returns confidence intervals for convergence counts.
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")
