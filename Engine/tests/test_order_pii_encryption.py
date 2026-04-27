"""Tests for §16.5 P2G — order_store.py PII encryption-at-rest +
delete-endpoint PII null-out.

All test PII is synthetic per §13.11 audit-surface rule: no real names,
no real DOBs, no real locations.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Stable encryption key + isolated data dir BEFORE any import that
# resolves the crypto master secret or the orders directory.
os.environ["SIRR_ENCRYPTION_KEY"] = "a" * 64  # 32 bytes hex
os.environ["SIRR_TOKEN_SECRET"] = "test-secret-for-unit-tests-only"
_TMPROOT = tempfile.mkdtemp(prefix="sirr-p2g-test-")
os.environ["SIRR_DATA_DIR"] = _TMPROOT

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_backend"))

import crypto  # noqa: E402
import order_store  # noqa: E402
from order_store import (  # noqa: E402
    create_order,
    get_order,
    update_order,
    get_order_by_stripe_session,
    _PII_FIELDS,
    _ENC_PREFIX,
)
from paths import ORDERS_DIR  # noqa: E402


@pytest.fixture(autouse=True)
def _disable_rate_limiter():
    """The 5/minute limit on /api/delete isn't what these tests verify;
    rate-limiting is covered by tests/test_rate_limiting.py. Disable the
    limiter for the duration of each test so multiple POSTs in a single
    test (e.g., the idempotency check) don't trip the budget when the
    full suite runs."""
    from middleware import limiter
    prior = limiter.enabled
    limiter.enabled = False
    try:
        yield
    finally:
        limiter.enabled = prior


# Synthetic placeholder PII — not real personal data.
SYNTH = {
    "name_latin": "FIXTURE NAME ALPHA",
    "name_arabic": "تجربة",
    "dob": "2000-01-01",
    "birth_time": "12:00",
    "birth_location": "Synthetic Locality",
    "lang": "en",
}

PII_VALUES = (
    SYNTH["name_latin"],
    SYNTH["name_arabic"],
    SYNTH["birth_location"],
    # dob and birth_time are short structured tokens — also asserted
    SYNTH["dob"],
    SYNTH["birth_time"],
)


def _raw_row_text(order_id: str) -> str:
    return (ORDERS_DIR / f"{order_id}.json").read_text()


# ── 1. PII never appears in plaintext on disk after create_order ──────────

def test_create_order_encrypts_pii_on_disk():
    order_id = create_order(SYNTH)
    raw = _raw_row_text(order_id)
    for value in PII_VALUES:
        assert value not in raw, (
            f"plaintext PII {value!r} found on disk in {order_id}"
        )
    parsed = json.loads(raw)
    for field in _PII_FIELDS:
        v = parsed.get(field)
        # Either an encrypted blob or empty/None pass-through
        if v is None or v == "":
            continue
        assert isinstance(v, str) and v.startswith(_ENC_PREFIX), (
            f"field {field} not encrypted on disk: {v!r}"
        )


# ── 2. get_order returns the original plaintext ────────────────────────────

def test_get_order_decrypts_pii_round_trip():
    order_id = create_order(SYNTH)
    row = get_order(order_id)
    assert row is not None
    for field in ("name_latin", "name_arabic", "dob", "birth_time", "birth_location"):
        assert row[field] == SYNTH[field], f"round-trip mismatch on {field}"


# ── 3. status="failed" rows refuse decrypt and strip PII to None ──────────

def test_get_order_failed_status_strips_pii_to_none(caplog):
    order_id = create_order(SYNTH)
    update_order(order_id, status="failed", error="synthetic-failure")
    row = get_order(order_id)
    assert row is not None
    assert row["status"] == "failed"
    for field in _PII_FIELDS:
        assert row[field] is None, f"failed row leaked plaintext on {field}"


# ── 4. FIX E parity: encryption failure leaves no plaintext file ──────────

def test_create_order_atomic_on_encryption_failure(monkeypatch):
    import crypto

    def boom(*_a, **_kw):
        raise RuntimeError("simulated encrypt failure")

    # order_store resolves crypto.encrypt_str at call time (the module
    # is imported by reference to survive importlib.reload across the
    # crypto-test suite), so patching crypto alone is sufficient.
    monkeypatch.setattr(crypto, "encrypt_str", boom)

    before = set(p.name for p in ORDERS_DIR.glob("*.json"))
    with pytest.raises(RuntimeError):
        create_order(
            {
                "name_latin": "FIXTURE NAME BETA",
                "dob": "2000-02-02",
                "lang": "en",
            }
        )
    after = set(p.name for p in ORDERS_DIR.glob("*.json"))
    assert before == after, (
        f"encryption failure left a row on disk: {after - before}"
    )


# ── 5. /api/delete nulls PII fields ────────────────────────────────────────

def test_delete_nulls_pii_fields():
    from fastapi.testclient import TestClient
    import server

    client = TestClient(server.app)

    order_id = create_order(SYNTH)
    # Stamp an email_hash so the email auth path can authenticate the delete.
    # The handler reads order.get("email", "") which our store never sets;
    # use the token path instead — mint a token for this order.
    from tokens import mint_token

    token = mint_token(order_id)
    r = client.post("/api/delete", json={"token": token})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "deleted"

    raw = _raw_row_text(order_id)
    parsed = json.loads(raw)
    assert parsed["status"] == "deleted"
    for field in _PII_FIELDS:
        assert parsed.get(field) is None, (
            f"delete left non-null {field}: {parsed.get(field)!r}"
        )
    # Also: no encrypted blob lingers — None means the row carries no
    # ciphertext for these fields.
    for value in PII_VALUES:
        assert value not in raw


# ── 6. Repeat-delete is idempotent ────────────────────────────────────────

def test_delete_idempotent():
    from fastapi.testclient import TestClient
    import server
    from tokens import mint_token

    client = TestClient(server.app)
    order_id = create_order(SYNTH)
    token = mint_token(order_id)

    r1 = client.post("/api/delete", json={"token": token})
    r2 = client.post("/api/delete", json={"token": token})
    assert r1.status_code == 200, f"r1={r1.status_code} body={r1.text}"
    assert r2.status_code == 200, f"r2={r2.status_code} body={r2.text}"
    assert r2.json()["status"] == "deleted"
    assert r2.json()["files_removed"] == 0


# ── 7. No plaintext PII across stderr + Python-logging surfaces ──────────

def test_no_plaintext_pii_in_logs(caplog, capfd, monkeypatch):
    """order_store logs decrypt failures via print(file=sys.stderr) — caplog
    alone misses them. Capture both surfaces and assert PII-cleanliness
    across the create + happy-get + failed-status get + decrypt-failure
    get + delete + repeat-delete trace.

    The decrypt-failure trigger uses a monkey-patched crypto.decrypt_str
    that raises with the synthetic PII fixture string in its message
    body. This gives the assertion teeth: a future regression that
    re-introduces `{exc}` interpolation anywhere in the chain
    (`_unwrap_pii_value` → `OrderDecryptionError(...)` → log line)
    would surface the PII through to capfd and fail the test. With the
    R3+R5 chain — wrap as `OrderDecryptionError(type(exc).__name__)`
    and log via `type(exc).__name__` — no PII reaches stderr."""
    from fastapi.testclient import TestClient
    import server
    from tokens import mint_token

    client = TestClient(server.app)

    leaky_msg = (
        f"forensic dump of plaintext payload: {SYNTH['name_latin']} / "
        f"{SYNTH['dob']} / {SYNTH['birth_location']}"
    )

    def leaky_decrypt(*_a, **_kw):
        raise crypto.DecryptionError(leaky_msg)

    with caplog.at_level(logging.DEBUG):
        order_id = create_order(SYNTH)
        _ = get_order(order_id)
        update_order(order_id, status="failed", error="synthetic-failure")
        _ = get_order(order_id)  # exercise failed-status branch
        update_order(order_id, status="pending", error=None)

        # Force the decrypt-failure path so we exercise the new
        # _log_decrypt_failure stderr line, with a PII-bearing exception
        # so the test catches any chain regression.
        monkeypatch.setattr(crypto, "decrypt_str", leaky_decrypt)
        _ = get_order(order_id)  # triggers decrypt-failure log line
        monkeypatch.undo()

        token = mint_token(order_id)
        client.post("/api/delete", json={"token": token})
        client.post("/api/delete", json={"token": token})  # idempotent path

    captured = capfd.readouterr()
    log_blob = (
        "\n".join(rec.getMessage() for rec in caplog.records)
        + "\n" + captured.out
        + "\n" + captured.err
    )
    for value in PII_VALUES:
        assert value not in log_blob, (
            f"plaintext PII {value!r} appeared on a log surface"
        )
    # Also assert the leaky exception message itself didn't leak — if a
    # regression interpolates {exc} anywhere, the leaky_msg would surface.
    assert leaky_msg not in log_blob, (
        f"PII-bearing exception message leaked through to log surface"
    )
    # Positive assertion: the decrypt-failure log line did fire and
    # contains the hash_oid + class name only, not the wrapped message.
    assert "[order_store-decrypt] failed" in captured.err
    assert "OrderDecryptionError" in captured.err


# ── 8. V3 regression: user input starting with the enc: prefix ────────────

def test_user_input_with_encrypted_prefix_is_re_encrypted():
    """If a user submits name_latin starting with 'enc:v1:' (whether by
    mistake or to attempt injection), the value must still be encrypted
    on disk and round-trip back to the original plaintext on read.
    Pre-fix this was silently stored as plaintext via a sentinel skip."""
    payload = dict(SYNTH)
    payload["name_latin"] = "enc:v1:DEADBEEFCAFEBABE"  # looks-like-ciphertext input
    order_id = create_order(payload)

    raw = _raw_row_text(order_id)
    parsed = json.loads(raw)
    # The value on disk must be a freshly-encrypted blob, not the
    # caller's literal input. Two encryptions of the same plaintext
    # produce different ciphertexts (random nonce), so a strict
    # inequality is the cleanest assertion.
    assert parsed["name_latin"] != payload["name_latin"]
    assert isinstance(parsed["name_latin"], str)
    assert parsed["name_latin"].startswith(_ENC_PREFIX)
    # And it round-trips back to the original literal on read.
    row = get_order(order_id)
    assert row["name_latin"] == payload["name_latin"]


# ── 9. V4: atomic write leaves no torn row on mid-write failure ───────────

def test_atomic_write_no_torn_row_on_failure(monkeypatch):
    """If the temp-file write or the os.replace fails mid-way, the
    final row file must not be left truncated or partially written.
    Either the row is the prior fully-written contents, or it does
    not exist (in the create_order case). The raised exception must be
    a sanitized OrderStoreIOError that does NOT carry the slug-bearing
    file path in its args (V4)."""
    import order_store as os_mod
    real_replace = os.replace

    # First create a healthy row, then fail the next update_order's
    # os.replace step. The original row file must remain readable.
    order_id = create_order(SYNTH)
    before = _raw_row_text(order_id)
    # The slug carries name+DOB by construction — it must not surface.
    slug_path = str(ORDERS_DIR / f"{order_id}.json")

    def boom_replace(*_a, **_kw):
        # The real OSError carries the slug-bearing path. Replicate that
        # in the message to prove the wrapper strips it.
        raise OSError(f"simulated replace failure leaking path: {slug_path}")

    monkeypatch.setattr(os_mod.os, "replace", boom_replace)
    with pytest.raises(os_mod.OrderStoreIOError) as excinfo:
        update_order(order_id, status="processing")
    monkeypatch.setattr(os_mod.os, "replace", real_replace)

    # Sanitization: the slug-path must not appear anywhere in the args
    # of the wrapped exception. The exception body must be exactly the
    # underlying class name — not the message.
    rendered = " ".join(str(a) for a in excinfo.value.args) + " " + str(excinfo.value)
    assert order_id not in rendered, f"slug leaked through OrderStoreIOError: {rendered!r}"
    assert slug_path not in rendered, f"path leaked through OrderStoreIOError: {rendered!r}"
    assert "OSError" in rendered, (
        f"type-name not preserved for log forensics: {rendered!r}"
    )

    after = _raw_row_text(order_id)
    assert after == before, "torn row left on disk after replace failure"
    # No lingering temp files in the orders dir for this order.
    leftovers = list(ORDERS_DIR.glob(f"{order_id}.json.*.tmp"))
    assert leftovers == [], f"orphan tmp files left: {leftovers}"


# ── 10. V2 migration: plaintext rows get encrypted; marker is set ─────────

def test_migration_encrypts_plaintext_rows_and_sets_marker(tmp_path, monkeypatch):
    """End-to-end: plant a plaintext row, run the migration, assert (a)
    the row is now encrypted on disk, (b) the marker file exists, (c)
    a re-run is a no-op (idempotent skipped count)."""
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    # Use a fresh sub-dir so we control the row population. Rebind
    # ORDERS_DIR + marker on both modules so the migration sees it.
    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    plaintext_row = {
        "order_id": "fixture-legacy-1",
        "status": "pending",
        "created_at": "2026-04-25T00:00:00",
        "name_latin": "FIXTURE LEGACY ONE",
        "name_arabic": "",
        "dob": "1999-09-09",
        "birth_time": "09:09",
        "birth_location": "Legacy City",
        "lang": "en",
    }
    (isolated / "fixture-legacy-1.json").write_text(json.dumps(plaintext_row, indent=2))

    rc = mig.main()
    assert rc == 0
    assert marker.exists(), "marker not set after clean migration"

    raw = (isolated / "fixture-legacy-1.json").read_text()
    parsed = json.loads(raw)
    for field in ("name_latin", "dob", "birth_time", "birth_location"):
        assert parsed[field].startswith(_ENC_PREFIX), (
            f"field {field} not encrypted post-migration: {parsed[field]!r}"
        )
    # Re-run is a no-op.
    rc2 = mig.main()
    assert rc2 == 0


# ── 11. V2 fail-closed: marker present + plaintext row → strip-to-None ────

def test_fail_closed_mode_refuses_plaintext(tmp_path, monkeypatch, capfd):
    """With the marker present, _unwrap_pii_value raises on plaintext;
    get_order strips PII to None and logs the decrypt-failure line."""
    import order_store as os_mod

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    marker.touch()  # fail-closed mode active
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)

    plaintext_row = {
        "order_id": "fixture-legacy-2",
        "status": "pending",
        "created_at": "2026-04-25T00:00:00",
        "name_latin": "FIXTURE LEGACY TWO",
        "dob": "1999-10-10",
        "lang": "en",
    }
    (isolated / "fixture-legacy-2.json").write_text(json.dumps(plaintext_row, indent=2))

    row = os_mod.get_order("fixture-legacy-2")
    assert row is not None
    assert row["name_latin"] is None
    assert row["dob"] is None
    err = capfd.readouterr().err
    assert "[order_store-decrypt] failed" in err


# ── 12. V5: /api/delete returns 500 if update_order raises ─────────────────

def test_delete_surfaces_500_on_update_order_failure(monkeypatch):
    """Right-to-delete must not lie. If update_order fails (disk full,
    fsync error, etc.) the customer must see 500, not a misleading
    'deleted' response with PII still on disk."""
    from fastapi.testclient import TestClient
    import server
    from tokens import mint_token

    order_id = create_order(SYNTH)
    token = mint_token(order_id)

    def boom(*_a, **_kw):
        raise OSError("simulated row write failure")

    monkeypatch.setattr(server, "update_order", boom)
    client = TestClient(server.app)
    r = client.post("/api/delete", json={"token": token})
    assert r.status_code == 500, f"expected 500, got {r.status_code}: {r.text}"


# ── 13. V1 migration ignores foreign files (engine output blobs etc.) ─────

def test_migration_skips_non_row_files(tmp_path, monkeypatch):
    """ORDERS_DIR also holds engine output files (AES-GCM binary blobs
    via crypto.write_encrypted) and may pick up other foreign files.
    Migration must shape-filter to row JSONs only — anything that
    doesn't read+parse as a dict with an `order_id` field gets silently
    skipped, not reported as a migration failure."""
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    # 1. Engine output file: encrypted binary blob masquerading as .json
    output_path = isolated / "fixture-legacy-3_output.json"
    crypto.write_encrypted(output_path, b'{"engine":"fake"}', "fixture-legacy-3")
    # 2. Foreign JSON without order_id (e.g., a backup someone left)
    (isolated / "foreign.json").write_text(json.dumps({"hello": "world"}))
    # 3. Genuine plaintext row that should be migrated
    (isolated / "fixture-legacy-3.json").write_text(json.dumps({
        "order_id": "fixture-legacy-3",
        "status": "pending",
        "created_at": "2026-04-25T00:00:00",
        "name_latin": "FIXTURE LEGACY THREE",
        "dob": "1999-11-11",
        "lang": "en",
    }, indent=2))

    rc = mig.main()
    assert rc == 0, "migration aborted on a foreign file (V1 regression)"
    assert marker.exists(), "marker missing — migration treated foreigns as failures"

    # Output blob and foreign JSON untouched.
    assert crypto.is_encrypted(output_path.read_bytes()), (
        "engine output file mutated by migration"
    )
    assert json.loads((isolated / "foreign.json").read_text()) == {"hello": "world"}
    # Genuine row encrypted.
    real = json.loads((isolated / "fixture-legacy-3.json").read_text())
    assert real["name_latin"].startswith(_ENC_PREFIX)


# ── 14. V2 migration recovers spoofed enc:v1: prefix on existing rows ─────

def test_migration_recovers_spoofed_prefix(tmp_path, monkeypatch):
    """A row written before R3 could carry name_latin='enc:v1:DEADBEEF'
    as plaintext (the R2-V3 attack vector). Migration must detect that
    the prefixed value does not actually decrypt, then re-encrypt the
    FULL ORIGINAL LITERAL — including the leading `enc:v1:` bytes —
    so no bytes the customer/caller submitted are silently dropped.
    The resulting field must round-trip back to the original literal
    string on a subsequent get_order call (P2G-followup V2 fix; R5
    pinned the lossy `DEADBEEF`-only round-trip behavior, this PR
    flips it to preserve the full literal).
    """
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    spoof = "DEADBEEFCAFEBABE"
    spoofed_literal = _ENC_PREFIX + spoof
    spoofed_row = {
        "order_id": "fixture-spoofed-1",
        "status": "pending",
        "created_at": "2026-04-25T00:00:00",
        "name_latin": spoofed_literal,  # looks encrypted, isn't
        "dob": "1999-12-12",
        "lang": "en",
    }
    (isolated / "fixture-spoofed-1.json").write_text(json.dumps(spoofed_row, indent=2))

    rc = mig.main()
    assert rc == 0
    assert marker.exists()

    # The field is now genuinely encrypted: starts with the prefix and
    # differs from the spoofed literal byte-for-byte (random nonce per
    # encryption).
    raw = json.loads((isolated / "fixture-spoofed-1.json").read_text())
    assert raw["name_latin"].startswith(_ENC_PREFIX)
    assert raw["name_latin"] != spoofed_literal, (
        "migration left the spoofed literal in place (no encrypt happened)"
    )
    # Round-trip preserves the FULL original literal — leading `enc:v1:`
    # bytes are NOT dropped (V2 lossless invariant).
    row = os_mod.get_order("fixture-spoofed-1")
    assert row["name_latin"] == spoofed_literal, (
        f"V2 lossless invariant broken: got {row['name_latin']!r}, "
        f"expected the full original literal {spoofed_literal!r}"
    )


# ── 15. V3 migration nulls PII on legacy status="deleted" rows ───────────

def test_migration_nulls_pii_on_legacy_deleted_rows(tmp_path, monkeypatch):
    """Pre-P2G /api/delete only nulled four operational fields, leaving
    name+DOB on disk. Migration must NULL the five PII fields on any
    status='deleted' row (rather than encrypting them, which would turn
    the legacy gap into a permanent encrypted residue)."""
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    legacy_deleted = {
        "order_id": "fixture-legacy-deleted-1",
        "status": "deleted",  # already deleted under pre-P2G code
        "created_at": "2026-03-01T00:00:00",
        "name_latin": "FIXTURE LEGACY DELETED",
        "name_arabic": "",
        "dob": "1980-05-05",
        "birth_time": "05:05",
        "birth_location": "Legacy Pre-P2G City",
        "lang": "en",
        "profile": None,
        "email_hash": None,
        "reading_url": None,
        "error": None,
    }
    p = isolated / "fixture-legacy-deleted-1.json"
    p.write_text(json.dumps(legacy_deleted, indent=2))

    rc = mig.main()
    assert rc == 0
    assert marker.exists()

    parsed = json.loads(p.read_text())
    for field in ("name_latin", "name_arabic", "dob", "birth_time", "birth_location"):
        assert parsed[field] is None, (
            f"legacy deleted row's {field} not nulled: {parsed[field]!r}"
        )
    # No encrypted blobs were produced for the deleted row — the
    # migration nulled, didn't encrypt.
    raw = p.read_text()
    assert _ENC_PREFIX not in raw


# ── 16. V3 belt-and-suspenders: tightened idempotent short-circuit ───────

def test_delete_runs_null_pass_on_legacy_deleted_row_with_pii(monkeypatch):
    """A row that is status='deleted' but still carries non-None PII
    (escaped the migration somehow) must NOT be short-circuited as a
    no-op — the handler must run the null+update pass to clean it up."""
    from fastapi.testclient import TestClient
    import server
    from tokens import mint_token

    # Plant a legacy-shaped row directly on disk: status=deleted but
    # PII still present. Bypass create_order to avoid the encrypt path.
    legacy = {
        "order_id": "fixture-escaped-1",
        "status": "deleted",
        "created_at": "2026-03-01T00:00:00",
        "name_latin": "FIXTURE ESCAPED THE MIGRATION",
        "name_arabic": "",
        "dob": "1985-06-06",
        "birth_time": "06:06",
        "birth_location": "Escapee City",
        "lang": "en",
        "profile": None, "email_hash": None,
        "reading_url": None, "error": None,
    }
    (ORDERS_DIR / "fixture-escaped-1.json").write_text(json.dumps(legacy, indent=2))

    token = mint_token("fixture-escaped-1")
    client = TestClient(server.app)
    r = client.post("/api/delete", json={"token": token})
    assert r.status_code == 200, r.text

    parsed = json.loads((ORDERS_DIR / "fixture-escaped-1.json").read_text())
    for field in ("name_latin", "name_arabic", "dob", "birth_time", "birth_location"):
        assert parsed[field] is None, (
            f"tightened short-circuit failed: {field} still {parsed[field]!r}"
        )


# ── 17. C2 _atomic_write_json tmp paths are observed, unique, and patterned

def test_atomic_write_tmp_paths_are_unique(tmp_path, monkeypatch):
    """`_atomic_write_json`'s tmp suffix is `.{pid}.{secrets.token_hex(4)}.tmp`
    so two writers cannot race on the same temp filename. Verify by
    monkey-patching `os.replace` to capture the `src` argument on each
    call AND `os.getpid` to return a sentinel value (Codex R2 C1 catch
    — without the sentinel, a `\\d+` pid match could equally satisfy
    a regression that swapped getpid for a monotonic counter), driving
    16 `_atomic_write_json` invocations, and asserting:

      (a) all 16 captures fired — proves the patch is actually
          installed (R5's version defined `capturing_replace` but
          never installed it, R6 C2 catch) AND proves the helper
          actually invokes os.replace;
      (b) every captured tmp path matches the regex including the
          literal sentinel pid `999999` — proves the helper uses
          BOTH `os.getpid()` (specifically, not just any integer)
          AND `secrets.token_hex(4)`, so a regression dropping
          either component would be caught;
      (c) all 16 captures are unique — the actual cross-write
          collision-free guarantee the tmp-suffix design provides.
    """
    import order_store as os_mod
    import re

    seen_tmps = []
    real_replace = os.replace

    def capturing_replace(src, dst):
        seen_tmps.append(str(src))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", capturing_replace)
    monkeypatch.setattr(os, "getpid", lambda: 999999)

    target = tmp_path / "fixture-tmp-c2.json"
    # Regex includes the literal sentinel pid; a regression that
    # replaces os.getpid() with anything else (counter, hardcoded
    # value, time.time(), etc.) fails the match.
    pattern = re.compile(r"fixture-tmp-c2\.json\.999999\.[0-9a-f]{8}\.tmp$")

    for i in range(16):
        os_mod._atomic_write_json(target, {"order_id": "fixture-tmp-c2", "k": i})

    assert len(seen_tmps) == 16, (
        f"expected 16 os.replace calls, got {len(seen_tmps)} — "
        f"monkeypatch may not be installed against the call site"
    )
    for tmp in seen_tmps:
        assert pattern.search(tmp), (
            f"tmp path {tmp!r} doesn't match expected "
            f"`{{stem}}.999999.<8-hex>.tmp` pattern — "
            f"helper may have lost os.getpid() or secrets.token_hex(4)"
        )
    assert len(set(seen_tmps)) == 16, (
        f"tmp paths collided across 16 _atomic_write_json invocations: "
        f"{[t for t in seen_tmps if seen_tmps.count(t) > 1][:3]}"
    )


# ── 18. R6 V1: idempotent short-circuit reads raw row, not sanitized view ─

def test_delete_cleans_escaped_row_in_fail_closed_mode(monkeypatch):
    """A row that escaped the migration with status='deleted' but
    plaintext PII still in place must be cleaned by /api/delete even
    when fail-closed mode is active. The R5 short-circuit relied on
    get_order(), which under fail-closed mode strips plaintext PII to
    None on read — that masked on-disk residue and locked the row into
    a permanent leak. R7 fix: short-circuit reads the raw row directly
    via is_row_already_fully_deleted()."""
    from fastapi.testclient import TestClient
    import server
    import order_store as os_mod
    from tokens import mint_token

    legacy = {
        "order_id": "fixture-escaped-fc-1",
        "status": "deleted",
        "created_at": "2026-03-01T00:00:00",
        "name_latin": "FIXTURE ESCAPED FAILCLOSED",
        "name_arabic": "",
        "dob": "1985-07-07",
        "birth_time": "07:07",
        "birth_location": "Escapee Failclosed City",
        "lang": "en",
        "profile": None, "email_hash": None,
        "reading_url": None, "error": None,
    }
    row_path = ORDERS_DIR / "fixture-escaped-fc-1.json"
    row_path.write_text(json.dumps(legacy, indent=2))

    # Activate fail-closed mode by touching the marker. This is the
    # state that masked the residue under R5's short-circuit.
    marker = os_mod._FAIL_CLOSED_MARKER
    marker.touch()
    try:
        # Sanity check the precondition the bug depended on: get_order
        # under fail-closed mode strips the plaintext PII to None.
        sanitized = os_mod.get_order("fixture-escaped-fc-1")
        assert sanitized is not None
        assert sanitized["name_latin"] is None  # the masking happens
        assert sanitized["status"] == "deleted"
        # ...but the raw probe correctly reports the row is NOT fully deleted.
        assert os_mod.is_row_already_fully_deleted("fixture-escaped-fc-1") is False

        token = mint_token("fixture-escaped-fc-1")
        client = TestClient(server.app)
        r = client.post("/api/delete", json={"token": token})
        assert r.status_code == 200, r.text

        parsed = json.loads(row_path.read_text())
        for field in ("name_latin", "name_arabic", "dob", "birth_time", "birth_location"):
            assert parsed[field] is None, (
                f"escaped row still has plaintext {field}: "
                f"{parsed[field]!r} — V1 regression"
            )
        # And after the cleanup, the raw probe agrees the row is fully
        # deleted, so a subsequent /api/delete will short-circuit.
        assert os_mod.is_row_already_fully_deleted("fixture-escaped-fc-1") is True
    finally:
        if marker.exists():
            marker.unlink()
        if row_path.exists():
            row_path.unlink()


# ── 19. R6 V4: glob loop survives binary blobs and foreign JSON ──────────

def test_get_order_by_stripe_session_skips_foreign_files(tmp_path, monkeypatch):
    """ORDERS_DIR co-locates engine output AES-GCM blobs with row
    JSONs (paths.py:14). The glob loop in get_order_by_stripe_session
    must catch UnicodeDecodeError on binary content, JSONDecodeError /
    not_a_dict / missing_order_id on foreign-shaped files, and skip
    them — not propagate the failure and break session-id resolution
    for every other order."""
    import order_store as os_mod

    isolated = tmp_path / "orders"
    isolated.mkdir()
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)

    # 1. Engine output AES-GCM binary blob (binary content, fails utf-8 decode).
    crypto.write_encrypted(
        isolated / "fixture-foreign-output.json",
        b'{"engine":"output"}',
        "fixture-foreign",
    )
    # 2. Foreign JSON top-level array (not a dict).
    (isolated / "foreign-array.json").write_text(json.dumps([1, 2, 3]))
    # 3. Foreign dict missing order_id field.
    (isolated / "foreign-dict.json").write_text(json.dumps({"hello": "world"}))
    # 4. Genuine row with a stripe_session_id we'll search for.
    real_row = {
        "order_id": "fixture-real-target",
        "status": "paid",
        "created_at": "2026-04-25T00:00:00",
        "name_latin": "FIXTURE REAL TARGET",
        "name_arabic": "",
        "dob": "1990-04-04",
        "birth_time": "04:04",
        "birth_location": "Real City",
        "lang": "en",
        "stripe_session_id": "cs_test_target_123",
    }
    # Use a directly-encrypted plant rather than create_order so we
    # don't depend on ORDERS_DIR being the live one when crypto runs.
    encrypted = dict(real_row)
    for f in _PII_FIELDS:
        v = encrypted.get(f)
        if v is None or v == "":
            continue
        encrypted[f] = _ENC_PREFIX + crypto.encrypt_str(v, context=real_row["order_id"]).hex()
    (isolated / "fixture-real-target.json").write_text(json.dumps(encrypted, indent=2))

    # The glob loop must not raise — must traverse all four files,
    # skip the three foreign ones, find the real match, and return
    # the decrypted row.
    found = os_mod.get_order_by_stripe_session("cs_test_target_123")
    assert found is not None
    assert found["name_latin"] == real_row["name_latin"]

    # And for an unmatched session_id, the loop returns None cleanly
    # (still doesn't raise on the foreign files).
    missing = os_mod.get_order_by_stripe_session("cs_test_does_not_exist")
    assert missing is None


# ── 20. V3 migration aborts on suspicious foreign dict (looks-like-row) ──

def test_migration_aborts_on_suspicious_row(tmp_path, monkeypatch, capfd):
    """A foreign dict that contains any of the 5 PII field keys but
    lacks `order_id` is suspicious — could be a corrupted real row
    whose `order_id` was lost. Migration MUST abort with a non-zero
    exit code, NOT set the marker, increment the
    `files_quarantined_suspicious` counter, and surface a PII-clean
    operator message identifying the file by basename only.

    Pre-V3 fix this would silently increment `files_skipped_non_row`,
    leave PII residue on disk, and then set the marker — flipping the
    system into fail-closed mode against a row that needed encryption.
    """
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    # Synthetic placeholders (§13.7): no real PII, no date-shaped
    # values that an audit would flag as PII-adjacent. The test
    # depends on the PII field KEYS being present, not their values.
    suspicious = {
        # No order_id; two PII field keys present → V3 abort trigger
        "name_latin": "FIXTURE PARTIAL ROW",
        "dob": "FIXTURE DOB",
        "status": "pending",
    }
    suspicious_file = isolated / "corrupted-row.json"
    suspicious_file.write_text(json.dumps(suspicious, indent=2))

    # Capture the on-disk source byte-for-byte before main() runs;
    # the abort path must NOT mutate the file (Codex R4 C1 catch —
    # the implementation aborts before update_order is reached, but
    # a future regression that re-orders the validation could mutate
    # the source on the abort path; assert byte equality to catch it).
    before = suspicious_file.read_text()

    rc = mig.main()
    assert rc == 3, f"expected exit code 3 for suspicious quarantine, got {rc}"
    assert not marker.exists(), (
        "marker was set despite suspicious-file abort — fail-closed mode "
        "would activate against an unmigrated row"
    )
    assert suspicious_file.read_text() == before, (
        "abort path mutated the source file — V3 fix regressed"
    )

    err = capfd.readouterr().err
    # PII-clean operator message: the planted PII string MUST NOT
    # appear in stderr — belt-and-suspenders against a future
    # regression that interpolates row contents into the message.
    assert "FIXTURE PARTIAL ROW" not in err, (
        f"V3 abort message leaked planted PII: {err!r}"
    )
    assert "FIXTURE DOB" not in err
    # Positive operator-affordance assertions: the message names the
    # file (basename), explains the action, names the trigger reason
    # from the closed `AbortReason` enum set, and surfaces the running
    # counter so dashboards can detect repeated quarantines without
    # re-grepping.
    assert "corrupted-row.json" in err
    assert "QUARANTINED" in err
    assert "marker NOT set" in err
    assert mig.AbortReason.MISSING_ORDER_ID.value in err, (
        f"V3 abort message missing reason tag "
        f"{mig.AbortReason.MISSING_ORDER_ID.value!r}: {err!r}"
    )
    assert "files_quarantined_suspicious=1" in err, (
        f"V3 abort message missing counter readout: {err!r}"
    )


# ── 21. V3 migration safely skips foreign dicts without PII keys ─────────

def test_migration_skips_foreign_dict_without_pii(tmp_path, monkeypatch):
    """A foreign dict that has neither `order_id` nor any PII field
    key is genuinely non-row content (backup metadata, app config,
    debug dump). Migration treats it as `files_skipped_non_row`,
    leaves the suspicious counter at zero, and still sets the marker
    on a clean pass — proves V3's three-state classifier doesn't
    over-trigger and quarantine benign files."""
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    foreign = {"hello": "world", "build_id": 42, "app_config": {"mode": "test"}}
    (isolated / "foreign-config.json").write_text(json.dumps(foreign, indent=2))

    rc = mig.main()
    assert rc == 0, f"expected clean rc=0, got {rc}"
    assert marker.exists(), "marker not set after a clean foreign-skip pass"


# ── 22. V1 (R3): order_id ↔ filename mismatch quarantines ────────────────

def test_migration_aborts_on_id_filename_mismatch(tmp_path, monkeypatch, capfd):
    """A row whose `order_id` field disagrees with `path.stem` cannot
    be safely migrated: `update_order` derives its target from
    `order_id` and would either silently no-op (if no file at the
    derived path exists) or mutate an UNRELATED row's data.

    Migration must detect the mismatch in `_try_load_row` and abort
    via SuspiciousRowAbort with reason="order_id-stem-mismatch".
    Exit code 3, marker unset, files_quarantined_suspicious counter
    incremented, operator message PII-clean (no row contents, only
    the basename + reason tag + counter).

    Pre-R3 fix this would silently increment files_skipped_non_row
    (no — actually pre-R3 it'd flow to update_order with the
    wrong-id and silently no-op against a missing target file, OR
    corrupt an unrelated row whose filename matched). Either way
    the source file would never be touched and the marker would
    land. Codex R2 V1 catch.
    """
    import order_store as os_mod
    import migrate_pii_encrypt as mig

    isolated = tmp_path / "orders"
    isolated.mkdir()
    marker = tmp_path / ".pii_encrypted_at_rest_v1"
    monkeypatch.setattr(os_mod, "ORDERS_DIR", isolated)
    monkeypatch.setattr(os_mod, "_FAIL_CLOSED_MARKER", marker)
    monkeypatch.setattr(mig, "ORDERS_DIR", isolated)
    monkeypatch.setattr(mig, "_FAIL_CLOSED_MARKER", marker)

    # Filename "mismatched.json" but row claims order_id "wrong-id".
    # Synthetic placeholders (§13.7): no real PII, no date-shaped
    # values. The test depends on the IDs differing, not on values.
    mismatched = {
        "order_id": "wrong-id",
        "name_latin": "FIXTURE MISMATCH",
        "dob": "FIXTURE DOB",
        "status": "pending",
    }
    src_file = isolated / "mismatched.json"
    src_file.write_text(json.dumps(mismatched, indent=2))

    # Byte-for-byte snapshot before main() — the abort path must NOT
    # mutate or unlink the source file (Codex R4 C1 catch).
    before = src_file.read_text()

    rc = mig.main()
    assert rc == 3, f"expected rc=3 for id-mismatch quarantine, got {rc}"
    assert not marker.exists(), (
        "marker was set despite id-mismatch abort — fail-closed mode "
        "would activate against a file that never got written"
    )
    # The source file is untouched (no side effects from the failed
    # auto-mutation). Byte equality catches both deletion and any
    # rewrite-then-restore pattern that .exists() would miss.
    assert src_file.exists(), "source file should not have been deleted"
    assert src_file.read_text() == before, (
        "abort path mutated the source file — V1 fix regressed"
    )

    err = capfd.readouterr().err
    # PII-clean operator message: planted PII strings MUST NOT appear.
    assert "FIXTURE MISMATCH" not in err, (
        f"V1 abort message leaked planted PII: {err!r}"
    )
    assert "FIXTURE DOB" not in err
    assert "wrong-id" not in err, (
        f"V1 abort message leaked the row's claimed order_id: {err!r}"
    )
    # Positive operator-affordance assertions: filename, action,
    # reason tag from the closed `AbortReason` enum, counter readout.
    assert "mismatched.json" in err
    assert "QUARANTINED" in err
    assert "marker NOT set" in err
    assert mig.AbortReason.STEM_MISMATCH.value in err, (
        f"V1 abort message missing reason tag "
        f"{mig.AbortReason.STEM_MISMATCH.value!r}: {err!r}"
    )
    assert "files_quarantined_suspicious=1" in err, (
        f"V1 abort message missing counter readout: {err!r}"
    )


# ── 23. R5 C2: AbortReason set is closed (catches silent additions) ──────

def test_abort_reason_set_is_closed():
    """The `AbortReason` enum codifies the operator-message contract:
    every quarantine surfaces a reason from a known closed set, so
    dashboards/alerts/runbooks can rely on the exhaustive list. A
    future addition that introduces a new reason without updating the
    operator-message format (or without updating tests #20/#22) would
    silently bypass the audit surface; this test fails fast on any
    unexpected addition or removal so the contributor is forced to
    either extend coverage or strip the new value."""
    import migrate_pii_encrypt as mig

    expected = {
        mig.AbortReason.MISSING_ORDER_ID,
        mig.AbortReason.STEM_MISMATCH,
    }
    assert set(mig.AbortReason) == expected, (
        f"AbortReason membership drifted; expected {expected!r}, "
        f"got {set(mig.AbortReason)!r} — extend tests #20/#22 or strip "
        f"the new value"
    )

    # Wire-format invariant: every member's `.value` is a string and
    # `member == member.value` (the (str, Enum) inheritance contract).
    # This is what lets the operator-side f-string on `.value` return
    # a plain string across Python 3.9+ regardless of the str-Enum
    # __str__ change in 3.11.
    for member in mig.AbortReason:
        assert isinstance(member.value, str), (
            f"reason {member!r}.value must be str, got {type(member.value)}"
        )
        assert member == member.value, (
            f"(str, Enum) equality contract broken for {member!r}"
        )
