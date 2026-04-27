"""Private overlay loader — V-3c calibration boundary.

The public engine never embeds personally-identifying name calibration data.
When a deployment provides a private overlay path (via SIRR_PRIVATE_OVERLAY
env var or constructor kwarg), the overlay's name_roots and name_morphology
dicts are merged with the public arabic_linguistics_tables before module
compute. When no overlay is provided or the file is missing, modules read
the empty merged tables and degrade gracefully (returning APPROX certainty
for lookup-dependent fields).
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional


_OVERLAY_KEYS = ("name_roots", "name_morphology")


def load_private_overlay(overlay_path: Optional[str] = None) -> dict:
    """Load the private overlay if available, else return empty dict.

    Resolution order:
      1. Explicit ``overlay_path`` argument (passed by caller).
      2. ``SIRR_PRIVATE_OVERLAY`` environment variable.
      3. Empty dict (no overlay).

    Any failure to read or parse the file is treated as "no overlay" — the
    engine never raises on a missing or malformed overlay. This keeps the
    public engine safe to ship without PRIVATE/ mounted.
    """
    path_str = overlay_path or os.environ.get("SIRR_PRIVATE_OVERLAY")
    if not path_str:
        return {}
    p = Path(path_str)
    if not p.exists() or not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def merge_tables(public_tables: dict, overlay: dict) -> dict:
    """Merge a public tables dict with a private overlay.

    Only the overlay's ``name_roots`` and ``name_morphology`` keys are merged
    (overlay values win on conflict). Other public keys, including universal
    tables like ``al_buni_letter_table`` and ``letter_color_map``, pass
    through unchanged. If ``overlay`` is empty or missing the relevant keys,
    the public tables are returned as-is (after a shallow copy).
    """
    merged = dict(public_tables)
    if not overlay:
        return merged
    for key in _OVERLAY_KEYS:
        public_val = merged.get(key) or {}
        overlay_val = overlay.get(key) or {}
        if overlay_val:
            merged[key] = {**public_val, **overlay_val}
    return merged


def load_and_merge(public_tables: dict, overlay_path: Optional[str] = None) -> dict:
    """Convenience: ``merge_tables(public_tables, load_private_overlay(overlay_path))``."""
    return merge_tables(public_tables, load_private_overlay(overlay_path))


def overlay_provides_lookups(merged_tables: dict) -> bool:
    """Return True if the merged tables contain non-empty lookup data.

    Used by modules to decide between COMPUTED_STRICT/LOOKUP_FIXED (when
    lookup data is present) and APPROX (when only the public engine is
    deployed without an overlay).
    """
    for key in _OVERLAY_KEYS:
        if merged_tables.get(key):
            return True
    return False
