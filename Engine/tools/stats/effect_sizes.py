"""Effect size calculations for convergence claims.

Statistical significance alone is insufficient — a convergence of 27 systems
on number 3 needs an effect size to judge practical importance.

DeepSeek Recommendation: "Report Cohen's d or Cramér's V alongside p-values
for every convergence claim. A p=0.002 with tiny effect size is noise."
"""
from __future__ import annotations
from typing import Any


def cohens_d(observed: float, null_mean: float, null_std: float) -> float:
    """Calculate Cohen's d effect size.

    d = (observed - null_mean) / null_std
    Interpretation: 0.2 small, 0.5 medium, 0.8 large.
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")


def cramers_v(contingency_table: list[list[int]]) -> float:
    """Calculate Cramér's V for categorical convergence (elements, types).

    V = sqrt(chi2 / (n * min(r-1, c-1)))
    Interpretation: 0.1 small, 0.3 medium, 0.5 large.
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")


def compute_effect_sizes(convergences: list[dict], baseline: dict) -> list[dict[str, Any]]:
    """Add effect size metrics to convergence claims.

    Returns convergences augmented with cohens_d and interpretation labels.
    """
    raise NotImplementedError("Awaiting DeepSeek Round 2 specification")
