"""Simple JSON-based order store. Upgrade to SQLite/Postgres later.

§16.5 (P2G): the five PII fields below are encrypted at rest with
AES-256-GCM (per-order key derived via HKDF from the master secret),
mirroring the Tier 2 file-encryption pattern from P2F-PR2. Encryption
runs inside the module-level threading lock so concurrent writers can't
interleave a half-encrypted row. Reads decrypt on access; on
status="failed" rows the PII fields are stripped to None instead of
decrypted (the order is unrecoverable from the customer's view).

The "enc:v1:" sentinel is load-bearing: it both distinguishes
encrypted from grandfathered plaintext rows on read and pins the
on-disk format for future migrations.

Writes go through `_atomic_write_json` (temp file + fsync(file) +
os.replace + fsync(dir)) so a process kill mid-write cannot leave a
truncated row visible to the unlocked `get_order` reader path.

Fail-closed mode: if `DATA_DIR/.pii_encrypted_at_rest_v1` marker exists,
plaintext PII on read raises `OrderDecryptionError` (handled by callers
as strip-to-None). The marker is touched only by the migration script
after a clean pass; absent the marker, legacy plaintext rows pass
through (grandfather mode). This is the operator's ratchet to lock down
after the one-shot migration runs.
"""
from __future__ import annotations
import json, os, secrets, sys, uuid, threading, hashlib, re
from pathlib import Path
from datetime import datetime

from paths import ORDERS_DIR, DATA_DIR
# Import the crypto module by reference (not via `from crypto import ...`)
# so that test code which reloads crypto via importlib.reload (see
# test_crypto.py's _reload_crypto_with_env helper) doesn't leave us
# holding a stale class identity for DecryptionError. Attribute access
# at call/raise time resolves through sys.modules and picks up the
# current class, so `except crypto.DecryptionError` matches whatever
# `crypto.decrypt_str` currently raises.
import crypto
from sanitize import hash_oid

_lock = threading.Lock()

# PII fields encrypted at rest. Order matters only for readability.
_PII_FIELDS = ("name_latin", "name_arabic", "dob", "birth_time", "birth_location")
_ENC_PREFIX = "enc:v1:"
_FAIL_CLOSED_MARKER = DATA_DIR / ".pii_encrypted_at_rest_v1"


class OrderDecryptionError(Exception):
    """Raised when an order row's PII cannot be decrypted.

    Never carries plaintext, key, or IV bytes — safe to log directly.
    Callers should treat this the same as a corrupted row.
    """


class OrderStoreIOError(Exception):
    """Raised when an order row cannot be read or written.

    Type-name only — never carries the file path, the row contents, or
    the underlying exception's message. Wraps OSError / JSONDecodeError
    at the order_store boundary so every caller in server.py gets a
    sanitized exception without per-call-site hardening. The slug-bearing
    file path the underlying OSError would have surfaced encodes
    name+DOB by construction (§16.5 deferred slug surface), so leaking
    it would defeat the encryption-at-rest closure.
    """


def _is_fail_closed() -> bool:
    """Return True iff the migration marker is present. Read per-call so
    tests can toggle without module reload, and so an operator touching
    the marker takes effect on the next request without restart."""
    return _FAIL_CLOSED_MARKER.exists()


def _atomic_write_json(path: Path, obj) -> None:
    """Serialize `obj` and write to `path` atomically.

    temp file + fsync(file) + os.replace + fsync(dir). On POSIX the
    rename is atomic; the directory fsync makes it durable across a
    process or host crash. The unlocked reader path therefore sees
    either the prior fully-written row or the next fully-written row,
    never a truncated intermediate.

    The temp filename is suffixed with `.<pid>.<random-hex>.tmp` so two
    gunicorn workers writing the same order_id concurrently cannot race
    on the temp path. (The module-level _lock serializes within a
    process; this is the cross-process belt.) On any failure mid-write
    the orphaned temp is best-effort unlinked before the sanitized
    OrderStoreIOError propagates.
    """
    payload = json.dumps(obj, indent=2)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    try:
        with open(tmp, "w") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dir_fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as exc:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise OrderStoreIOError(type(exc).__name__) from None


def _safe_read_row(p: Path) -> dict:
    """Read + parse a row JSON file. Wraps every failure mode the read
    or the parse can hit as OrderStoreIOError so the slug-bearing path
    and any partial file contents never reach the caller. Validates
    that the parsed top-level value is a dict carrying an `order_id`
    field — a foreign file (JSON array, scalar) or a dict missing the
    canonical key is treated the same as a corrupt row, not as a
    silently-empty result.

    The orders directory also holds AES-GCM-encrypted engine output
    blobs (see paths.py:14); those binary contents fail UTF-8 decoding
    on read_text() and surface UnicodeDecodeError, which the wrapper
    catches alongside OSError and JSONDecodeError.
    """
    try:
        text = p.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        raise OrderStoreIOError(type(exc).__name__) from None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OrderStoreIOError(type(exc).__name__) from None
    if not isinstance(parsed, dict):
        raise OrderStoreIOError("not_a_dict")
    if "order_id" not in parsed:
        raise OrderStoreIOError("missing_order_id")
    return parsed


def is_row_already_fully_deleted(order_id: str) -> bool:
    """Idempotency probe for /api/delete.

    Reads the raw on-disk row directly (no decrypt, no status="failed"
    refusal, no fail-closed strip-to-None) and returns True iff the row
    has status="deleted" AND every PII field is literally None on disk.

    The sanitized get_order() view cannot be used for this check: under
    fail-closed mode (post-migration marker), get_order strips plaintext
    PII to None on read, masking on-disk residue from the short-circuit
    decision. A row that escaped the migration with status="deleted"
    but PII still present would falsely look "already cleaned" via
    get_order, locking the residue in place permanently.

    Returns False on any read/parse error or shape mismatch — the
    cautious answer is "fall through to the cleanup pass," not "skip
    cleanup because we couldn't tell."
    """
    p = ORDERS_DIR / f"{order_id}.json"
    if not p.exists():
        return False
    try:
        text = p.read_text()
    except (OSError, UnicodeDecodeError):
        return False
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        return False
    if not isinstance(raw, dict):
        return False
    if raw.get("status") != "deleted":
        return False
    return all(raw.get(f) is None for f in _PII_FIELDS)


def _wrap_pii_value(value, order_id: str):
    """Encrypt a single PII string. None and "" pass through unchanged
    so absence stays distinguishable from ciphertext.

    Note: there is no idempotent skip on the enc:v1: prefix. Callers
    only ever pass caller-supplied kwargs (from `create_order` data or
    `update_order` kwargs), never re-read row fields, so a value
    arriving here that already starts with the prefix is treated as
    user input — encrypted again, surfacing any caller bug rather than
    silently storing user-controlled "enc:v1:..." strings as plaintext.
    """
    if value is None or value == "":
        return value
    if not isinstance(value, str):
        raise TypeError("PII fields must be str, None, or empty string")
    blob = crypto.encrypt_str(value, context=order_id)
    return _ENC_PREFIX + blob.hex()


def _unwrap_pii_value(value, order_id: str):
    """Inverse of _wrap_pii_value.

    Grandfather behavior is gated on the migration marker:
      - marker absent: legacy plaintext (no prefix) passes through unchanged
      - marker present (post-migration): plaintext raises OrderDecryptionError
    """
    if value is None or value == "":
        return value
    if not isinstance(value, str):
        return value
    if not value.startswith(_ENC_PREFIX):
        if _is_fail_closed():
            # Operator has run the migration; any plaintext PII at this
            # point is a bug (missed row, bypassed write path, or marker
            # touched prematurely). Refuse to serve.
            raise OrderDecryptionError("plaintext_after_migration")
        return value
    hex_blob = value[len(_ENC_PREFIX):]
    try:
        blob = bytes.fromhex(hex_blob)
        return crypto.decrypt_str(blob, context=order_id)
    except (crypto.DecryptionError, ValueError) as exc:
        # Wrap the class name only; never the str(exc) body, which on
        # some exception types could surface bytes from the failed
        # decrypt attempt.
        raise OrderDecryptionError(type(exc).__name__) from None


def _encrypt_pii(order: dict, order_id: str) -> dict:
    """Mutate `order` so PII fields hold ciphertext. Returns the same dict."""
    for field in _PII_FIELDS:
        if field in order:
            order[field] = _wrap_pii_value(order[field], order_id)
    return order


def _decrypt_pii(order: dict, order_id: str) -> dict:
    """Mutate `order` so PII fields hold plaintext. Returns the same dict."""
    for field in _PII_FIELDS:
        if field in order:
            order[field] = _unwrap_pii_value(order[field], order_id)
    return order


def _make_slug(name: str, dob: str) -> str:
    """Generate a readable URL slug from name + DOB.

    'JANE SMITH' + '1990-03-15' → 'jane-smith-15mar1990-a7f3'

    NOTE (§16.5 deferred): the slug encodes name+DOB into both the
    on-disk filename and the row's `order_id` field. After the delete
    path nulls the five PII fields, the slug remains as a name+DOB-
    derived identifier. Tracked separately from `hash_oid`'s log
    correlation truncation; see SIRR_MASTER_REGISTRY.md §16.5 deferred
    surfaces.
    """
    parts = name.strip().split()[:3]
    slug_parts = [re.sub(r'[^a-z]', '', p.lower()) for p in parts]
    slug_parts = [p for p in slug_parts if p]

    try:
        dt = datetime.strptime(dob, "%Y-%m-%d")
        dob_str = dt.strftime("%d%b%Y").lower()
    except ValueError:
        dob_str = dob.replace("-", "")

    raw = f"{name}:{dob}:{uuid.uuid4().hex[:8]}"
    short_hash = hashlib.sha256(raw.encode()).hexdigest()[:4]

    return "-".join(slug_parts + [dob_str, short_hash])


def _log_decrypt_failure(order_id: str, exc: OrderDecryptionError) -> None:
    """Single source of truth for the decrypt-failure log line. Class
    name only — never the message body or the wrapped exception's
    str() — to keep the log surface PII-/IV-/key-clean."""
    print(
        f"[order_store-decrypt] failed for order {hash_oid(order_id)}: "
        f"{type(exc).__name__}",
        file=sys.stderr,
    )


def create_order(data: dict) -> str:
    order_id = _make_slug(data["name_latin"], data["dob"])
    order = {
        "order_id": order_id,
        "status": "pending",          # pending → paid → processing → ready → failed
        "created_at": datetime.utcnow().isoformat(),
        "name_latin": data["name_latin"],
        "name_arabic": data.get("name_arabic", ""),
        "dob": data["dob"],
        "birth_time": data.get("birth_time"),
        "birth_location": data.get("birth_location"),
        "lang": data.get("lang", "en"),
        "stripe_session_id": None,
        "reading_url": None,
        "error": None,
    }
    with _lock:
        # Encrypt inside the lock so a concurrent reader/writer can't
        # observe a partially-encrypted state. If encryption raises,
        # nothing has been written yet — FIX E parity at the row layer.
        _encrypt_pii(order, order_id)
        _atomic_write_json(ORDERS_DIR / f"{order_id}.json", order)
    return order_id


def get_order(order_id: str) -> dict | None:
    p = ORDERS_DIR / f"{order_id}.json"
    if not p.exists():
        return None
    order = _safe_read_row(p)
    if order.get("status") == "failed":
        # Refuse to decrypt unrecoverable rows; mirror the P2F serve-side
        # refusal pattern at server.py:415. Strip PII to None so callers
        # still get the dict | None contract and can render error pages.
        for field in _PII_FIELDS:
            if field in order:
                order[field] = None
        return order
    try:
        return _decrypt_pii(order, order_id)
    except OrderDecryptionError as exc:
        _log_decrypt_failure(order_id, exc)
        for field in _PII_FIELDS:
            if field in order:
                order[field] = None
        return order


def update_order(order_id: str, **kwargs):
    with _lock:
        p = ORDERS_DIR / f"{order_id}.json"
        if not p.exists():
            return
        order = _safe_read_row(p)
        # PII kwargs (including explicit None for the delete path) are
        # encrypted before merge; non-PII kwargs pass through. Existing
        # encrypted PII fields already in `order` are not iterated, so
        # there is no double-encryption path.
        for field in _PII_FIELDS:
            if field in kwargs:
                kwargs[field] = _wrap_pii_value(kwargs[field], order_id)
        order.update(kwargs)
        _atomic_write_json(p, order)


def compare_and_swap_status(order_id: str, *, expected, new: str) -> bool:
    """Atomically transition order status from `expected` to `new`.

    Returns True iff the row existed AND its status matched `expected`
    AND the swap was written. Returns False otherwise (missing row,
    corrupt row, or status not in `expected`).

    Used by the LS webhook handler to make `order_created` idempotent
    against LS-side delivery retries — only the first delivery for a
    given order_id transitions pending→paid, so post-payment
    side-effects (engine spawn, email send) fire exactly once.

    `expected` accepts a single status string or an iterable of allowed
    statuses; the swap fires if the current status is any of them.

    Within-process: protected by the module-level `_lock` plus the
    atomic file rename in `_atomic_write_json`. Cross-process
    (gunicorn multi-worker) the race remains theoretically open;
    deferred until the JSON store is replaced with a real DB. At
    launch volume (10-100 orders/mo) the race is extremely unlikely
    in practice.
    """
    with _lock:
        p = ORDERS_DIR / f"{order_id}.json"
        if not p.exists():
            return False
        try:
            row = _safe_read_row(p)
        except OrderStoreIOError:
            return False
        expected_set = (expected,) if isinstance(expected, str) else tuple(expected)
        if row.get("status") not in expected_set:
            return False
        row["status"] = new
        _atomic_write_json(p, row)
        return True


def get_order_by_stripe_session(session_id: str) -> dict | None:
    # Match on the plaintext stripe_session_id field; only decrypt PII
    # for the matching row so the scan stays O(N) reads, not O(N) decrypts.
    # A single corrupt row is logged and skipped rather than aborting
    # the lookup — one bad row should not break session-id resolution
    # for every other order.
    for p in ORDERS_DIR.glob("*.json"):
        try:
            o = _safe_read_row(p)
        except OrderStoreIOError as exc:
            print(
                f"[order_store-read] failed for row {hash_oid(p.stem)}: "
                f"{type(exc).__name__}",
                file=sys.stderr,
            )
            continue
        if o.get("stripe_session_id") == session_id:
            order_id = o.get("order_id") or p.stem
            if o.get("status") == "failed":
                for field in _PII_FIELDS:
                    if field in o:
                        o[field] = None
                return o
            try:
                return _decrypt_pii(o, order_id)
            except OrderDecryptionError as exc:
                _log_decrypt_failure(order_id, exc)
                for field in _PII_FIELDS:
                    if field in o:
                        o[field] = None
                return o
    return None
