"""One-shot migration: encrypt plaintext PII in existing order rows,
null PII in legacy `status="deleted"` rows, and validate any
prefixed values are genuinely encrypted (not spoofed-plaintext).

Idempotent. Walks `ORDERS_DIR/*.json` and only processes files whose
top-level JSON is a dict containing an `order_id` field — the
directory also holds engine output files (encrypted via P2F-PR2's
`crypto.write_encrypted`, binary blobs that won't decode as UTF-8 or
parse as JSON), and those are silently skipped.

Three classes of legacy PII content are handled:

  1. **Plaintext PII fields** — encrypted via `update_order(...)` so
     the canonical write path applies (atomic temp+replace + fsync).
  2. **Spoofed `enc:v1:` prefix** — a pre-R3 caller could have written
     a string like `name_latin="enc:v1:DEADBEEF"` as plaintext, since
     R3's V3 fix only sanitized the write path going forward. On read,
     these decrypt-fail and silently strip to None under fail-closed
     mode, but on disk they still look encrypted to a glob-and-grep.
     Migration validates each prefixed value by attempting decrypt; if
     decrypt fails, the post-prefix portion is treated as the user's
     literal plaintext and re-encrypted.
  3. **Legacy `status="deleted"` rows with PII still present** —
     pre-P2G `/api/delete` only nulled `profile`/`email_hash`/
     `reading_url`/`error`, so historical deletions retained their
     name+DOB. Migration NULLs the five PII fields rather than
     encrypting them; this is what the original delete should have
     done.

On a clean pass — every row processed without raising — touches
`DATA_DIR/.pii_encrypted_at_rest_v1` to flip
`order_store._is_fail_closed()` to True. Per-row errors abort the
migration and skip the marker so a partial run does not flip the
system into fail-closed mode against unmigrated rows.

Run before flipping the production deploy that ships the §16.5 P2G
closure:

    SIRR_ENCRYPTION_KEY=<hex> SIRR_DATA_DIR=/data \\
        python3 -m migrate_pii_encrypt

Or via Railway CLI:

    railway run --service <svc> -- python3 -m migrate_pii_encrypt

Output is intentionally PII-free: counts of each migration category
plus the marker path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make this script runnable both as `python3 -m migrate_pii_encrypt`
# from the web_backend directory and as a direct script invocation.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import crypto  # noqa: E402
from paths import ORDERS_DIR  # noqa: E402
from order_store import (  # noqa: E402
    _PII_FIELDS,
    _ENC_PREFIX,
    _FAIL_CLOSED_MARKER,
    update_order,
)
from sanitize import hash_oid  # noqa: E402


def _try_load_row(path: Path) -> dict | None:
    """Return the parsed row dict if `path` looks like an order row;
    otherwise None. Engine output files (AES-GCM binary blobs) raise on
    `read_text` or `json.loads`; foreign files lack the `order_id`
    field. Both cases are skipped silently."""
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict) or "order_id" not in parsed:
        return None
    return parsed


def _classify_prefixed_value(value: str, order_id: str) -> tuple[str, str | None]:
    """Inspect a value carrying the `enc:v1:` prefix.

    Returns ("validated", None) if the ciphertext genuinely decrypts
    (no action needed; row already encrypted).

    Returns ("spoofed", recovered_plaintext) if the prefix is present
    but the bytes do not decrypt — the caller should re-encrypt
    `recovered_plaintext` and overwrite the field. The recovered
    plaintext is the post-prefix portion of the original value, on the
    interpretation that an attacker or buggy caller submitted a
    `enc:v1:<arbitrary>` string as plaintext input.
    """
    hex_blob = value[len(_ENC_PREFIX):]
    try:
        blob = bytes.fromhex(hex_blob)
        crypto.decrypt_str(blob, context=order_id)
        return ("validated", None)
    except (crypto.DecryptionError, ValueError):
        return ("spoofed", hex_blob)


def _migrate_one(path: Path, counters: dict) -> None:
    """Apply one row of migration logic. Mutates `counters` in place."""
    row = _try_load_row(path)
    if row is None:
        counters["files_skipped_non_row"] += 1
        return
    order_id = row.get("order_id") or path.stem

    # Class 3: legacy deleted rows. Null the PII rather than encrypt it.
    if row.get("status") == "deleted":
        null_kwargs = {}
        for field in _PII_FIELDS:
            if row.get(field) is not None:
                null_kwargs[field] = None
        if null_kwargs:
            update_order(order_id, **null_kwargs)
            counters["deleted_rows_nulled"] += 1
        else:
            counters["already_clean"] += 1
        return

    # Classes 1 + 2 walk the PII fields. Plaintext → encrypt.
    # Prefixed-but-invalid → recover post-prefix portion as plaintext
    # and re-encrypt. Prefixed-and-valid → no-op.
    re_encrypt_kwargs = {}
    for field in _PII_FIELDS:
        v = row.get(field)
        if v is None or v == "" or not isinstance(v, str):
            continue
        if v.startswith(_ENC_PREFIX):
            verdict, recovered = _classify_prefixed_value(v, order_id)
            if verdict == "validated":
                counters["prefix_validated"] += 1
            else:
                re_encrypt_kwargs[field] = recovered or ""
                counters["prefix_spoofed_recovered"] += 1
            continue
        # plaintext path
        re_encrypt_kwargs[field] = v
        counters["plaintext_encrypted_fields"] += 1

    if re_encrypt_kwargs:
        update_order(order_id, **re_encrypt_kwargs)
        counters["rows_changed"] += 1
    else:
        counters["already_clean"] += 1


def main() -> int:
    counters = {
        "rows_changed": 0,
        "already_clean": 0,
        "deleted_rows_nulled": 0,
        "plaintext_encrypted_fields": 0,
        "prefix_validated": 0,
        "prefix_spoofed_recovered": 0,
        "files_skipped_non_row": 0,
    }
    paths = list(ORDERS_DIR.glob("*.json"))
    for p in paths:
        try:
            _migrate_one(p, counters)
        except Exception as e:
            order_id = p.stem
            print(
                f"[migrate-pii] FAILED on {hash_oid(order_id)}: "
                f"{type(e).__name__} — marker NOT set, fix and rerun",
                file=sys.stderr,
            )
            return 2
    _FAIL_CLOSED_MARKER.touch()
    parts = " ".join(f"{k}={v}" for k, v in counters.items())
    print(f"{parts} total_files={len(paths)} marker={_FAIL_CLOSED_MARKER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
