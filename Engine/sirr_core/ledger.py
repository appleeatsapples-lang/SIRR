from __future__ import annotations
from typing import Any, Dict, List, Optional

def add_ledger_entry(
    ledger: List[Dict[str, Any]],
    system_id: str,
    kind: str,
    computed: Any,
    claimed: Any,
    status: str,
    action: str,
    note: Optional[str] = None
) -> None:
    """Log a contradiction or action item."""
    ledger.append({
        "system": system_id,
        "kind": kind,
        "computed": computed,
        "claimed": claimed,
        "status": status,
        "action": action,
        "note": note
    })
