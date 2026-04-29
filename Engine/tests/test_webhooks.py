"""Tests for webhook signature verification.

Guards the §16 security hardening behavior:
  - LS webhook MUST fail-closed when LEMONSQUEEZY_WEBHOOK_SECRET is unset.
  - Missing / wrong signatures return 400.
  - Valid signatures pass through.

These tests import the full server app. If dependencies for the engine
stack aren't installed (anthropic, pyswisseph, etc.), the import will
fail and these tests are skipped via pytest.importorskip.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_backend"))


@pytest.fixture(autouse=True)
def _block_real_email_sends(monkeypatch):
    """Defense-in-depth: ensure NO test in this file can ever trigger
    a real Resend send, even if RESEND_API_KEY and EMAIL_FROM happen
    to be set in the test environment (e.g., a developer's .env
    loaded into the pytest process).

    Imports server eagerly inside the fixture body so the monkeypatch
    applies for every test — not conditionally, not dependent on
    whether the test uses the `client` fixture or on pytest
    collection order. The previous `if "server" in sys.modules`
    guard was removed (C-AUDIT-3): the autouse docstring promised
    universal protection, but the guard silently skipped on cold
    start and left the contract fragile to test-reordering.

    Tests that need to assert on email behavior should depend on the
    `mock_send_email` fixture below, which re-monkeypatches with an
    explicit capture list (last-monkeypatch-wins). This autouse
    backstop catches any test that forgets to mock.

    The V4 email-body test that exercises send_post_payment_email
    end-to-end through email_sender (not via the webhook handler)
    monkeypatches `email_sender.resend` directly, so this server-
    level backstop is orthogonal and does not interfere.
    """
    def _no_op_send(*, to, reading_url, order_id):
        return None

    import server
    monkeypatch.setattr(server, "send_post_payment_email", _no_op_send)


@pytest.fixture
def client(monkeypatch):
    """Return a TestClient for the real server app with a known LS secret.

    Sets the env BEFORE import so module-level LS_WEBHOOK_SECRET captures it.
    """
    monkeypatch.setenv("LEMONSQUEEZY_WEBHOOK_SECRET", "test-secret-for-webhook")
    # Fresh import so LS_WEBHOOK_SECRET picks up the patched env.
    for mod in ("server",):
        if mod in sys.modules:
            del sys.modules[mod]
    server = pytest.importorskip("server")
    # Re-apply the autouse backstop now that server is loaded — the
    # autouse fixture ran before the re-import and may have patched a
    # stale module reference (or skipped entirely on cold start).
    def _no_op_send(*, to, reading_url, order_id):
        return None
    monkeypatch.setattr(server, "send_post_payment_email", _no_op_send)
    from fastapi.testclient import TestClient
    return TestClient(server.app), server


def _sign(secret: str, payload_bytes: bytes) -> str:
    return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()


def test_ls_webhook_rejects_missing_signature(client):
    tc, _ = client
    body = json.dumps({"meta": {"event_name": "ping"}}).encode()
    r = tc.post(
        "/api/webhook/lemonsqueezy",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    assert "signature" in r.json()["detail"].lower()


def test_ls_webhook_rejects_wrong_signature(client):
    tc, _ = client
    body = json.dumps({"meta": {"event_name": "ping"}}).encode()
    r = tc.post(
        "/api/webhook/lemonsqueezy",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature": "deadbeef" * 8,  # wrong-length nonsense
        },
    )
    assert r.status_code == 400


def test_ls_webhook_accepts_valid_signature_non_order_event(client):
    """A correctly-signed payload for an event we don't handle (not
    order_created) still returns 200 — only the update_order+thread
    block is gated by event_name. This verifies the signature path
    succeeds without triggering a background engine run."""
    tc, _ = client
    body = json.dumps({"meta": {"event_name": "subscription_created"}}).encode()
    sig = _sign("test-secret-for-webhook", body)
    r = tc.post(
        "/api/webhook/lemonsqueezy",
        content=body,
        headers={"Content-Type": "application/json", "X-Signature": sig},
    )
    assert r.status_code == 200
    assert r.json() == {"received": True}


def test_ls_webhook_fails_closed_when_secret_unset(monkeypatch):
    """Regression guard for the audit fix (2026-04-20).

    An unset LEMONSQUEEZY_WEBHOOK_SECRET MUST cause the webhook to return
    503, not 200. Previously the webhook fell-open when the env var was
    empty: any attacker with a guessable order_id could trigger engine
    runs (Anthropic API burn).
    """
    monkeypatch.delenv("LEMONSQUEEZY_WEBHOOK_SECRET", raising=False)
    for mod in ("server",):
        if mod in sys.modules:
            del sys.modules[mod]
    server = pytest.importorskip("server")
    from fastapi.testclient import TestClient
    tc = TestClient(server.app)

    body = json.dumps({"meta": {"event_name": "order_created"}}).encode()
    r = tc.post(
        "/api/webhook/lemonsqueezy",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"].lower()


# ─────────────────────────────────────────────────────────────
# Launch Path-C — compare_and_swap_status unit tests
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_orders(monkeypatch, tmp_path):
    """Isolate order_store.ORDERS_DIR to a per-test tempdir so CAS
    unit tests don't collide with each other or with on-disk launch
    rows. Writes a row directly via _atomic_write_json with the
    minimum schema CAS reads (`order_id`, `status`) to keep the
    fixture independent of the PII-encryption code path."""
    import order_store
    monkeypatch.setattr(order_store, "ORDERS_DIR", tmp_path)

    def _seed(order_id: str, status: str) -> None:
        order_store._atomic_write_json(
            tmp_path / f"{order_id}.json",
            {"order_id": order_id, "status": status},
        )

    return order_store, _seed


def test_compare_and_swap_status_first_call_succeeds(tmp_orders):
    """Order in `pending` → CAS to `paid` returns True and persists."""
    order_store, seed = tmp_orders
    seed("ord-cas-first", "pending")

    swapped = order_store.compare_and_swap_status(
        "ord-cas-first", expected="pending", new="paid"
    )

    assert swapped is True
    assert order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-cas-first.json"
    )["status"] == "paid"


def test_compare_and_swap_status_second_call_returns_false(tmp_orders):
    """Idempotency invariant: a duplicate webhook delivery (LS retry)
    sees the row already at `paid` and the second CAS returns False
    so post-payment side-effects fire exactly once."""
    order_store, seed = tmp_orders
    seed("ord-cas-dup", "pending")

    first = order_store.compare_and_swap_status(
        "ord-cas-dup", expected="pending", new="paid"
    )
    second = order_store.compare_and_swap_status(
        "ord-cas-dup", expected="pending", new="paid"
    )

    assert first is True
    assert second is False
    # Status remains "paid" — second call did not regress or re-write.
    assert order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-cas-dup.json"
    )["status"] == "paid"


def test_cas_writes_extra_fields_atomically(tmp_orders):
    """V2: compare_and_swap_status with extra_fields writes status AND
    the extra plaintext index fields in one locked operation. Closes
    the paid-but-no-engine-spawn window where a post-CAS update_order
    could raise after the status flip."""
    order_store, seed = tmp_orders
    seed("ord-cas-extras", "pending")

    swapped = order_store.compare_and_swap_status(
        "ord-cas-extras",
        expected="pending",
        new="paid",
        ls_order_identifier="abcdef00-1111-2222-3333-444455556666",
    )

    assert swapped is True
    row = order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-cas-extras.json"
    )
    assert row["status"] == "paid"
    assert row["ls_order_identifier"] == "abcdef00-1111-2222-3333-444455556666"


def test_cas_silently_drops_disallowed_extra_fields(tmp_orders):
    """V2 defense-in-depth: extras outside _ALLOWED_PLAINTEXT_EXTRAS
    are silently dropped so a future caller cannot route PII (or any
    other field) through CAS. PII fields belong on update_order, which
    encrypts at rest."""
    order_store, seed = tmp_orders
    seed("ord-cas-pii-block", "pending")

    swapped = order_store.compare_and_swap_status(
        "ord-cas-pii-block",
        expected="pending",
        new="paid",
        ls_order_identifier="cafebabe-0000-1111-2222-333344445555",
        name_latin="Should Not Land",
        dob="1990-01-01",
    )

    assert swapped is True
    row = order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-cas-pii-block.json"
    )
    assert row["status"] == "paid"
    assert row["ls_order_identifier"] == "cafebabe-0000-1111-2222-333344445555"
    assert "name_latin" not in row
    assert "dob" not in row


# ─────────────────────────────────────────────────────────────
# Launch Path-C — webhook idempotency + ls_identifier persistence
# ─────────────────────────────────────────────────────────────


class _RecordingThread:
    """Stand-in for threading.Thread: records spawns without running
    the engine. The webhook idempotency tests assert spawn count, not
    target completion."""

    spawns: list = []

    def __init__(self, *args, **kwargs):
        self._target = kwargs.get("target")

    def start(self):
        type(self).spawns.append(
            self._target.__name__ if self._target else "<noname>"
        )


class _ImmediateThread:
    """Like _RecordingThread but invokes the target inline for the
    email-background path only. Engine-spawn target is recorded but
    NOT invoked — running _generate_reading_background inline would
    burn Anthropic API and write engine output, not what the unit
    tests want.

    Used by tests that need to assert side-effects of the email
    background thread (e.g., mock_send_email captures, EmailSendError
    swallowing). Pass kwargs= or args= through unchanged so the
    real-world call shape is exercised.
    """

    spawns: list = []

    def __init__(self, *args, **kwargs):
        self._target = kwargs.get("target")
        self._kwargs = kwargs.get("kwargs", {}) or {}
        self._args = kwargs.get("args", ()) or ()

    def start(self):
        name = self._target.__name__ if self._target else "<noname>"
        type(self).spawns.append(name)
        if name == "_send_post_payment_email_background" and self._target:
            self._target(*self._args, **self._kwargs)


def _signed_post(tc, secret: str, payload: dict):
    body = json.dumps(payload).encode()
    sig = _sign(secret, body)
    return tc.post(
        "/api/webhook/lemonsqueezy",
        content=body,
        headers={"Content-Type": "application/json", "X-Signature": sig},
    )


def test_ls_webhook_is_idempotent_on_duplicate_delivery(client, tmp_orders, monkeypatch):
    """LS retry scenario: two identical signed deliveries of
    order_created → engine spawned exactly once, status pinned at
    paid. Validates the compare_and_swap_status guard in the webhook
    handler."""
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-idemp", "pending")

    _RecordingThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _RecordingThread)

    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-idemp"},
        },
        "data": {
            "attributes": {
                "identifier": "550e8400-e29b-41d4-a716-446655440000",
                "user_email": "test@example.com",
            }
        },
    }
    r1 = _signed_post(tc, "test-secret-for-webhook", payload)
    r2 = _signed_post(tc, "test-secret-for-webhook", payload)

    assert r1.status_code == 200
    assert r2.status_code == 200
    # Both engine and email spawn for the first delivery only — CAS
    # gates the second delivery before any side-effect fires. With
    # V-AUDIT-1, the email is now off-thread, so it shows up as a
    # spawn alongside the engine.
    assert _RecordingThread.spawns.count("_generate_reading_background") == 1
    assert _RecordingThread.spawns.count("_send_post_payment_email_background") == 1
    assert len(_RecordingThread.spawns) == 2, (
        f"expected exactly 2 spawns total (engine + email), got {_RecordingThread.spawns}"
    )
    assert order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-idemp.json"
    )["status"] == "paid"


def test_ls_webhook_persists_ls_order_identifier(client, tmp_orders, monkeypatch):
    """Webhook must store data.attributes.identifier on the order row
    so /r/by-ls/{uuid} (commit 4) can resolve back to our internal
    order_id when the customer clicks the LS receipt button.

    V2 invariant: the persistence happens inside the same atomic CAS
    write as the status flip — NOT via a follow-up update_order call.
    Asserts update_order is never reached during the handler, so the
    paid-but-no-side-effects window is provably closed.
    """
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-idmark", "pending")

    _RecordingThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _RecordingThread)

    update_calls: list = []
    real_update = server.update_order

    def _spy_update(order_id, **kwargs):
        update_calls.append((order_id, dict(kwargs)))
        return real_update(order_id, **kwargs)

    monkeypatch.setattr(server, "update_order", _spy_update)

    ls_uuid = "abcdef00-0000-1111-2222-deadbeefcafe"
    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-idmark"},
        },
        "data": {"attributes": {"identifier": ls_uuid}},
    }
    r = _signed_post(tc, "test-secret-for-webhook", payload)

    assert r.status_code == 200
    row = order_store._safe_read_row(
        order_store.ORDERS_DIR / "ord-idmark.json"
    )
    assert row["ls_order_identifier"] == ls_uuid
    assert row["status"] == "paid"
    # V2: the LS UUID landed via CAS extras, not via a follow-up
    # update_order. The webhook handler must not call update_order
    # post-CAS at all (the engine background thread may, but the
    # handler proper has no further row writes).
    assert update_calls == [], (
        f"webhook handler called update_order post-CAS: {update_calls}"
    )


# ─────────────────────────────────────────────────────────────
# Launch Path-C — post-payment email wiring
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_send_email(monkeypatch):
    """Capture send_post_payment_email calls without touching Resend.
    Mocks at the boundary (the function exposed on the server module),
    not the resend SDK itself — keeps tests deterministic and
    independent of resend being installed."""
    sent: list = []

    def _fake_send(*, to, reading_url, order_id):
        sent.append({"to": to, "reading_url": reading_url, "order_id": order_id})

    return sent, _fake_send


def test_ls_webhook_order_created_triggers_email(client, tmp_orders, monkeypatch, mock_send_email):
    """First delivery of order_created with valid signature →
    send_post_payment_email called once with (to, reading_url, order_id)
    derived from the webhook payload.

    Uses _ImmediateThread so the email background target actually fires
    and mock_send_email captures. Engine target is recorded but skipped
    by _ImmediateThread (running engine inline would burn Anthropic API).
    """
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-mail", "pending")

    sent, fake_send = mock_send_email
    monkeypatch.setattr(server, "send_post_payment_email", fake_send)
    _ImmediateThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _ImmediateThread)

    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-mail"},
        },
        "data": {
            "attributes": {
                "identifier": "11111111-2222-3333-4444-555555555555",
                "user_email": "buyer@example.com",
            }
        },
    }
    r = _signed_post(tc, "test-secret-for-webhook", payload)

    assert r.status_code == 200
    assert len(sent) == 1
    assert sent[0]["to"] == "buyer@example.com"
    assert sent[0]["order_id"] == "ord-mail"
    assert sent[0]["reading_url"].startswith(server.BASE_URL + "/r/")


def test_ls_webhook_email_failure_returns_200(client, tmp_orders, monkeypatch):
    """If send_post_payment_email raises EmailSendError, the webhook
    must still return 200 (LS would retry forever otherwise; customer
    has the LS receipt button as a recovery path).

    Post V-AUDIT-1: the EmailSendError raises inside the daemon thread
    target (_send_post_payment_email_background), is caught by its
    own try/except, and never propagates back to the webhook return
    path. _ImmediateThread runs the email target inline so the raise
    actually fires under test.
    """
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-mailfail", "pending")

    def _raises(**kw):
        from email_sender import EmailSendError
        raise EmailSendError("simulated-resend-outage")

    monkeypatch.setattr(server, "send_post_payment_email", _raises)
    _ImmediateThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _ImmediateThread)

    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-mailfail"},
        },
        "data": {
            "attributes": {
                "identifier": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
                "user_email": "buyer@example.com",
            }
        },
    }
    r = _signed_post(tc, "test-secret-for-webhook", payload)

    assert r.status_code == 200
    # Engine + email both spawned; email target raised internally and
    # was swallowed by _send_post_payment_email_background — webhook
    # return path never saw the exception.
    assert "_generate_reading_background" in _ImmediateThread.spawns
    assert "_send_post_payment_email_background" in _ImmediateThread.spawns


def test_email_body_uses_hash_oid_not_name_derived_slug(monkeypatch):
    """V4: the order ID printed in the email body must be name-irreversible.

    order_store._make_slug derives order_id from name+DOB, so the first
    eight chars of the slug deterministically encode customer PII.
    Embedding that in the body shipped to Resend (third-party) would
    leak name-derivation to their logs, analytics, and any
    deliverability-debugging surface. hash_oid is the
    SHA-256-first-12-chars correlation ID used everywhere else for
    operational logging — name-irreversible by construction.
    """
    import email_sender
    from sanitize import hash_oid

    captured: dict = {}

    class _FakeEmails:
        @staticmethod
        def send(payload):
            captured.update(payload)

    class _FakeResend:
        api_key = None
        Emails = _FakeEmails

    monkeypatch.setattr(email_sender, "resend", _FakeResend)
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    monkeypatch.setenv("EMAIL_FROM", "noreply@example.com")

    # Mimics _make_slug output: the first 8 chars are name-derived.
    order_id = "janesmith-15mar1990-a7f3"
    expected_hash = hash_oid(order_id)
    name_derived_prefix = order_id[:8]  # "janesmi" + "t"

    email_sender.send_post_payment_email(
        to="buyer@example.com",
        reading_url="https://example.com/r/opaque-token",
        order_id=order_id,
    )

    assert f"Order: {expected_hash}" in captured["html"]
    assert f"Order: {expected_hash}" in captured["text"]
    # name-derived prefix must NOT leak into either body. 'janesmit' is
    # not a hex substring (j, n, s, m, i, t are all outside [0-9a-f]),
    # so the hash cannot collide with it by construction.
    assert name_derived_prefix not in captured["html"]
    assert name_derived_prefix not in captured["text"]


def test_ls_webhook_missing_user_email_skips_email_send(client, tmp_orders, monkeypatch, mock_send_email):
    """Webhook payload without data.attributes.user_email → no email
    attempted (don't crash). Engine still runs."""
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-noemail", "pending")

    sent, fake_send = mock_send_email
    monkeypatch.setattr(server, "send_post_payment_email", fake_send)
    _RecordingThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _RecordingThread)

    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-noemail"},
        },
        "data": {
            "attributes": {
                "identifier": "00000000-1111-2222-3333-444444444444",
                # no user_email
            }
        },
    }
    r = _signed_post(tc, "test-secret-for-webhook", payload)

    assert r.status_code == 200
    assert sent == []  # no email attempted
    assert _RecordingThread.spawns == ["_generate_reading_background"]


def test_ls_webhook_email_send_does_not_block_webhook_response(client, tmp_orders, monkeypatch):
    """V-AUDIT-1: a slow Resend call must NOT delay the webhook
    response. Pre-fix, a 30s Resend timeout would block past LS's
    ~10-15s webhook window — LS would time out, retry, and the retry
    would CAS=False silently. Customer paid, no email, no recovery.

    Asserts the webhook returns within 1 second even when
    send_post_payment_email is configured to sleep 5 seconds.

    Uses _RecordingThread (records but does NOT run the target) so the
    5-second sleep never actually fires in the test. The invariant is
    structural: the webhook calls threading.Thread(target=email_bg)
    rather than calling send_post_payment_email inline. A real prod
    trace would show webhook returning ~10ms while Resend is still
    in-flight on the daemon thread.
    """
    import time as _time
    tc, server = client
    order_store, seed = tmp_orders
    seed("ord-slowsend", "pending")

    def _slow_send(*, to, reading_url, order_id):
        _time.sleep(5)

    monkeypatch.setattr(server, "send_post_payment_email", _slow_send)
    _RecordingThread.spawns = []
    monkeypatch.setattr(server.threading, "Thread", _RecordingThread)

    payload = {
        "meta": {
            "event_name": "order_created",
            "custom_data": {"order_id": "ord-slowsend"},
        },
        "data": {
            "attributes": {
                "identifier": "550e8400-e29b-41d4-a716-446655440000",
                "user_email": "buyer@example.com",
            }
        },
    }
    start = _time.time()
    r = _signed_post(tc, "test-secret-for-webhook", payload)
    elapsed = _time.time() - start

    assert r.status_code == 200
    assert elapsed < 1.0, (
        f"webhook blocked for {elapsed:.2f}s (V-AUDIT-1 regression — "
        "email must spawn in a daemon thread, never block the webhook)"
    )
    assert "_send_post_payment_email_background" in _RecordingThread.spawns


# ─────────────────────────────────────────────────────────────
# Launch Path-C — /r/by-ls/{uuid} redirect endpoint
# ─────────────────────────────────────────────────────────────


def test_redirect_by_ls_uuid_to_token(client, tmp_orders):
    """Order with stored ls_order_identifier → /r/by-ls/{uuid}
    302-redirects to /r/{token}."""
    tc, server = client
    order_store, _seed = tmp_orders

    ls_uuid = "12345678-90ab-cdef-1234-567890abcdef"
    # Seed a row with the ls_order_identifier index field directly.
    order_store._atomic_write_json(
        order_store.ORDERS_DIR / "ord-redir.json",
        {
            "order_id": "ord-redir",
            "status": "paid",
            "ls_order_identifier": ls_uuid,
        },
    )

    r = tc.get(f"/r/by-ls/{ls_uuid}", follow_redirects=False)

    assert r.status_code == 302
    location = r.headers["location"]
    assert location.startswith("/r/"), f"unexpected redirect target: {location}"
    # The token is opaque; verify it round-trips back to the same order_id
    # via the same try_verify_token path the real /r/{token} uses.
    token = location[len("/r/"):]
    assert server.try_verify_token(token) == "ord-redir"


def test_redirect_by_ls_uuid_accepts_uppercase(client, tmp_orders):
    """C-AUDIT-1: RFC 4122 UUIDs are case-insensitive. If LS ever
    emits uppercase (or mixed-case) in receipt-button substitution,
    the redirect must still resolve. The regex carries IGNORECASE
    and the lookup lowercases before matching the stored value
    (which is itself lowercased on webhook persist)."""
    tc, server = client
    order_store, _seed = tmp_orders

    # Stored value is lowercase (matches webhook-persist normalization).
    ls_uuid_lower = "550e8400-e29b-41d4-a716-446655440000"
    order_store._atomic_write_json(
        order_store.ORDERS_DIR / "ord-case.json",
        {
            "order_id": "ord-case",
            "status": "paid",
            "ls_order_identifier": ls_uuid_lower,
        },
    )

    # LS sends the uppercase variant — must still 302 to the same order.
    r = tc.get(
        "/r/by-ls/550E8400-E29B-41D4-A716-446655440000",
        follow_redirects=False,
    )

    assert r.status_code == 302
    location = r.headers["location"]
    assert location.startswith("/r/"), f"unexpected redirect target: {location}"
    token = location[len("/r/"):]
    assert server.try_verify_token(token) == "ord-case"


def test_redirect_by_ls_uuid_unknown_returns_404(client, tmp_orders):
    """No order has this LS UUID → 404. Don't leak existence info; the
    response shape must be identical to the malformed-UUID case below."""
    tc, _server = client
    # tmp_orders isolates ORDERS_DIR to an empty tempdir; no rows match.
    r = tc.get(
        "/r/by-ls/99999999-8888-7777-6666-555555555555",
        follow_redirects=False,
    )
    assert r.status_code == 404


@pytest.mark.parametrize(
    "bad_uuid",
    [
        "..%2F..%2Fetc%2Fpasswd",          # path traversal (URL-encoded)
        "%27%3B%20DROP%20TABLE%20orders",   # SQLi shape (URL-encoded)
        "abc",                              # too short
        "G2345678-90ab-cdef-1234-567890abcdef",  # non-hex char
        "12345678901234567890123456789012",      # no dashes
        # V1 defensive: if LS ever fails to substitute the placeholder
        # (template typo, account misconfig, etc.) the literal
        # [order_identifier] must 404 at the regex, not 500.
        "%5Border_identifier%5D",
    ],
)
def test_redirect_by_ls_uuid_malformed_returns_404(client, tmp_orders, bad_uuid):
    """Path-traversal / SQLi / non-UUID-shaped inputs → 404 at the
    regex boundary, never reaching find_order_by_ls_identifier or
    touching disk."""
    tc, _server = client
    r = tc.get(f"/r/by-ls/{bad_uuid}", follow_redirects=False)
    assert r.status_code == 404
