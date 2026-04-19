from __future__ import annotations
from typing import List, Dict, Any, Optional
from sirr_core.types import SystemResult

CERT_ICONS = {
    "COMPUTED_STRICT": "[LOCKED]",
    "LOOKUP_FIXED": "[METHOD]",
    "APPROX": "[~APPROX]",
    "NEEDS_EPHEMERIS": "[EPHEM?]",
    "NEEDS_CORRELATION": "[CORR?]",
    "NEEDS_INPUT": "[INPUT?]",
    "META": "[SYNTH]"
}

def render_terminal(results: List[SystemResult], synthesis: Optional[Dict] = None) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("  SIRR v2 - NEW SYSTEMS DISCOVERY RUN (Deterministic Core)")
    lines.append("=" * 72)

    for r in results:
        icon = CERT_ICONS.get(r.certainty, "[?]")
        lines.append("")
        lines.append("-" * 72)
        lines.append(f"  {r.id.upper()} - {r.name}  {icon}")
        if r.question:
            lines.append(f"  Answers: {r.question}")
        lines.append("-" * 72)
        lines.append(f"  Certainty: {r.certainty}")
        for k, v in r.data.items():
            if isinstance(v, list):
                lines.append(f"  {k}:")
                for row in v:
                    lines.append(f"    {row}")
            else:
                lines.append(f"  {k}: {v}")
        if r.interpretation:
            lines.append("  ---")
            for chunk in r.interpretation.split("\n"):
                lines.append(f"  {chunk}")

    if synthesis:
        lines.append("")
        lines.append("=" * 72)
        lines.append("  CROSS-SYSTEM SYNTHESIS")
        lines.append("=" * 72)
        for key, val in synthesis.items():
            if isinstance(val, dict):
                lines.append(f"\n  {key}:")
                for k2, v2 in val.items():
                    lines.append(f"    {k2}: {v2}")
            elif isinstance(val, list):
                lines.append(f"\n  {key}:")
                for item in val:
                    if isinstance(item, dict):
                        for k2, v2 in item.items():
                            lines.append(f"    {k2}: {v2}")
                        lines.append("")
                    else:
                        lines.append(f"    - {item}")
            else:
                lines.append(f"  {key}: {val}")

    return "\n".join(lines)

def render_ledger(ledger: List[Dict[str, Any]]) -> str:
    if not ledger:
        return ""
    lines = []
    lines.append("")
    lines.append("!" * 72)
    lines.append("  CONTRADICTION LEDGER")
    lines.append("!" * 72)
    for item in ledger:
        lines.append(f"  [{item['status']}] {item['system']} / {item['kind']}")
        lines.append(f"    computed: {item['computed']}")
        lines.append(f"    claimed:  {item['claimed']}")
        lines.append(f"    action:   {item['action']}")
        if item.get("note"):
            lines.append(f"    note:     {item['note']}")
    return "\n".join(lines)
