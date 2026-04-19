#!/usr/bin/env python3
"""
SIRR CLI Tools — Swift app integration helpers.

Usage:
  python sirr_tools.py transliterate "JAMES SMITH"
  python sirr_tools.py transliterate_json '["JAMES", "SMITH"]'
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modules.transliterate import transliterate_to_arabic


def cmd_transliterate(name: str) -> None:
    """Print Arabic transliteration of a Latin name."""
    result = transliterate_to_arabic(name.upper())
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sirr_tools.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "transliterate":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd_transliterate(name)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
