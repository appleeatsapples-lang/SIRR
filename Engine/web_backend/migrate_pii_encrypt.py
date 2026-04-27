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
     decrypt fails, the FULL ORIGINAL LITERAL (including the leading
     `enc:v1:` bytes) is re-encrypted via `update_order` so no bytes
     the customer/caller submitted are silently dropped.
  3. **Legacy `status="deleted"` rows with PII still present** —
     pre-P2G `/api/delete` only nulled `profile`/`email_hash`/
     `reading_url`/`error`, so historical deletions retained their
     name+DOB. Migration NULLs the five PII fields rather than
     encrypting them; this is what the original delete should have
     done.

The classifier has a third terminal state for files that look like
partial rows — top-level dict missing `order_id` but carrying any of
the five PII field keys. Those raise `SuspiciousRowAbort`, the
migration halts with exit code 3, and the marker is NOT set. The
operator must triage the file by hand before re-running.

On a clean pass — every row processed without raising — touches
`DATA_DIR/.pii_encrypted_at_rest_v1` to flip
`order_store._is_fail_closed()` to True. Per-row errors abort the
migration and skip the marker so a partial run does not flip the
system into fail-closed mode against unmigrated rows. Exit codes:
0 = clean pass, 2 = per-row exception, 3 = suspicious file
quarantined.

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


class SuspiciousRowAbort(Exception):
    """Raised when `_try_load_row` finds a foreign dict that
    resembles a partial or mismatched row.

    Two trigger conditions, both indicating a file the migration
    cannot safely auto-resolve:

      1. `missing-order_id-with-pii-keys` — top-level dict missing
         `order_id` but carrying any of the five PII field keys
         (could be a corrupted real row whose `order_id` was lost).

      2. `order_id-stem-mismatch` — top-level dict has `order_id`
         but it disagrees with `path.stem`. Processing this row
         would cause `update_order(row["order_id"], ...)` to write
         to a *different* file than the one we're reading
         (since `update_order` targets `ORDERS_DIR/{order_id}.json`),
         either silently no-op'ing on the wrong target's absence or
         mutating an unrelated row's data.

    Args: (basename, reason) — basename only, never row contents,
    key/value snippets, or the full slug-bearing path beyond the
    basename. The basename may still encode name+DOB for slug-shaped
    filenames per the §16.5 deferred `_make_slug` surface, out of
    scope here. The reason tag is a static string drawn from a
    closed set, so it's audit-surface-safe.

    The migration aborts on either trigger rather than silently
    skipping or auto-mutating. Silent skip would leave PII residue
    on disk and falsely activate fail-closed mode after marker-set;
    auto-mutating could corrupt unrelated rows. Better to halt and
    let the operator triage the file by hand.
    """


def _try_load_row(path: Path) -> dict | None:
    """Three-state classifier:

      - returns dict: genuine order row (caller processes it). The
        row's `order_id` field matches `path.stem` — required because
        `update_order` derives its target filename from `order_id`,
        so a mismatch would cause writes to land in the wrong file.
      - returns None: genuine non-row — engine output AES-GCM blob
        (raises UnicodeDecodeError on read_text), foreign JSON array
        or scalar, foreign dict that has neither `order_id` nor any
        PII field key. Caller skips silently.
      - raises SuspiciousRowAbort with one of:
          * reason="missing-order_id-with-pii-keys" — dict missing
            `order_id` but carrying at least one PII field key.
          * reason="order_id-stem-mismatch" — dict has `order_id`
            but it doesn't match `path.stem`.
        Caller aborts the migration without setting the marker.
    """
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if "order_id" in parsed:
        # `update_order` derives its target as `ORDERS_DIR/{order_id}.json`;
        # if the row's self-claim doesn't match the file we read it
        # from, processing the row would touch the wrong file (or no
        # file at all). Halt rather than auto-mutate.
        if parsed["order_id"] != path.stem:
            raise SuspiciousRowAbort(path.name, "order_id-stem-mismatch")
        return parsed
    # Dict missing order_id. If any PII field key is present, this
    # looks like a partial row — abort rather than skip.
    if any(field in parsed for field in _PII_FIELDS):
        raise SuspiciousRowAbort(path.name, "missing-order_id-with-pii-keys")
    return None


def _classify_prefixed_value(value: str, order_id: str) -> tuple[str, str | None]:
    """Inspect a value carrying the `enc:v1:` prefix.

    Returns ("validated", None) if the ciphertext genuinely decrypts
    (no action needed; row already encrypted).

    Returns ("spoofed", value) — preserving the FULL original literal,
    including the leading `enc:v1:` bytes — if the prefix is present
    but the bytes do not decrypt. The caller re-encrypts the literal
    via `update_order` so no bytes the customer/caller submitted are
    silently dropped, even bytes that look like a sentinel prefix.
    Pre-R5 this returned only the post-prefix portion, which corrupted
    any legitimate input whose actual literal happened to start with
    `enc:v1:` (Codex R6 V2 catch).
    """
    hex_blob = value[len(_ENC_PREFIX):]
    try:
        blob = bytes.fromhex(hex_blob)
        crypto.decrypt_str(blob, context=order_id)
        return ("validated", None)
    except (crypto.DecryptionError, ValueError):
        return ("spoofed", value)


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
                # `recovered` is the full original literal (V2 fix);
                # never None on a "spoofed" verdict.
                re_encrypt_kwargs[field] = recovered
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
        "files_quarantined_suspicious": 0,
    }
    paths = list(ORDERS_DIR.glob("*.json"))
    for p in paths:
        try:
            _migrate_one(p, counters)
        except SuspiciousRowAbort as e:
            counters["files_quarantined_suspicious"] += 1
            # e.args[0] is the path BASENAME, e.args[1] is a static
            # reason tag from a closed set. Neither carries row
            # contents, key/value snippets, or PII. The basename may
            # still encode name+DOB for slug-shaped filenames per the
            # deferred _make_slug §16.5 surface, out of scope here.
            basename, reason = e.args[0], e.args[1]
            print(
                f"[migrate-pii] QUARANTINED suspicious file "
                f"{basename} (reason: {reason}) — manual inspection "
                f"required, marker NOT set, rerun after triage. "
                f"files_quarantined_suspicious="
                f"{counters['files_quarantined_suspicious']}",
                file=sys.stderr,
            )
            return 3
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
