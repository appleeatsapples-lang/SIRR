# S4 Architecture Audit — 2026-04-29

**Author:** Claude orchestrator
**Method:** Adversarial pass on `Engine/web_backend/` + `pip-audit` on `requirements.txt`
**Scope:** Pre-launch security baseline per `PRIVATE/Orchestration/Plans/MULTI_STREAM_AUDIT_PLAN_2026-04-27.md` Stream S4
**Engine commit at audit time:** `4044e3c` (post PR #54 merge)

This document records the S4 self-audit pass per the Apr 27 multi-stream audit plan's S4 stream. Per the plan's gating logic, S4 must clear before live-mode flip. This is the aggressive-path version (self-audit + monitoring) rather than external pen-test.

---

## Headline finding

**Web layer is genuinely well-hardened.** Zero P0 (launch-blocking) findings. One P1 finding (BASE_URL startup validation, 5 lines of code to fix). One P2 finding (X-Forwarded-For trust). Five known-vulnerability dependencies — none directly exploitable in current code paths, all with safe upgrade paths.

The web layer reflects the work that PRs through P2D, P2E, P2F, P2G, and the V-3 wave shipped: AES-GCM AEAD tokens, per-record HKDF-derived encryption keys, fail-closed webhook signatures, comprehensive log scrubs, Pydantic input validation, slowapi rate limiting, comprehensive security headers. The audit found no class of vulnerability uncaught by previous Codex rounds.

---

## P0 — Launch-blocking findings

**None.** The web layer is launch-ready as of `4044e3c`.

---

## P1 — Should fix this week (pre-launch)

### P1.1 — `BASE_URL` not validated at startup

**File:** `Engine/web_backend/server.py:57`

**Current state:**
```python
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
```

**Issue:** if Railway env var `BASE_URL` is unset in production, defaults to `localhost:8000`. The value is embedded in:
- Stripe `success_url`, `cancel_url` (line 1273-1274)
- Lemon Squeezy `redirect_url`, `receipt_link_url` (line 1225, 1234)
- Resend post-payment email body via `reading_url = f"{BASE_URL}/r/..."` (line 1390)

If unset, customers complete payment, get redirected to `http://localhost:8000/success?token=...`, and the post-payment flow breaks silently from the customer's perspective.

**Fix:** mirror the `SIRR_ENCRYPTION_KEY` fail-fast pattern (`crypto.py:_is_production()` check). When `RAILWAY_DEPLOYMENT_ID` is set, require `BASE_URL` to be present and not localhost:

```python
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
if os.environ.get("RAILWAY_DEPLOYMENT_ID"):
    _is_local = (
        not BASE_URL
        or BASE_URL.startswith("http://localhost")
        or BASE_URL.startswith("http://127.")
        or BASE_URL.startswith("http://0.")
    )
    if _is_local:
        raise RuntimeError(
            "BASE_URL must be set to a public HTTPS URL in production. "
            f"Detected Railway deployment but BASE_URL={BASE_URL!r}. "
            "Customer-facing checkout URLs and email links would point "
            "to localhost. Set BASE_URL in the Railway dashboard."
        )
```

**Risk class:** R2 (touches `Engine/web_backend/server.py`, an R0 path-trigger that promotes minimum to R2 per LANE_DOCTRINE_v3 §2).

**Tracking:** opens as PR with separate brief; mandates Codex T2 pre-review.

### P1.2 — Five known dep vulnerabilities (none directly exploitable)

`pip-audit` against `requirements.txt` (run 2026-04-29):

| Package | Current | Patched | CVE | Affected API | SIRR usage | Verdict |
|---|---|---|---|---|---|---|
| python-dotenv | 1.2.1 | 1.2.2 | CVE-2026-28684 | `set_key()`, `unset_key()` symlink-follow | Only `load_dotenv()` (read-only) | NOT exploitable |
| pytest | 8.4.2 | 9.0.3 | CVE-2025-71176 | `/tmp/pytest-of-{user}` directory pattern | Test runtime only | NOT exploitable in production |
| pillow | 11.3.0 | 12.1.1 | CVE-2026-25990 | PSD image OOB write | No PIL/PSD usage in code | NOT exploitable (transitive dep) |
| pillow | 11.3.0 | 12.2.0 | CVE-2026-40192 | FITS image GZIP bomb | No PIL/FITS usage in code | NOT exploitable (transitive dep) |
| requests | 2.32.5 | 2.33.0 | CVE-2026-25645 | `extract_zipped_paths()` predictable temp filename | No `requests` usage in code | NOT exploitable (transitive dep) |

All five are transitive deps or use APIs SIRR doesn't call. Audit confirmed by grep:
- `grep -rn "set_key\|unset_key" Engine/` → empty
- `grep -rn "import requests\|from requests" Engine/` → empty
- `grep -rn "from PIL\|import PIL" Engine/` → empty
- `grep -rn "extract_zipped_paths" Engine/` → empty

**Fix:** upgrade `requirements.txt` constraints. Single PR, R1 risk class (only `requirements.txt` touched).

---

## P2 — Post-launch hardening (not blocking)

### P2.1 — `X-Forwarded-For` trust in rate limiter

**File:** `Engine/web_backend/middleware.py:30-37`

```python
def _key_func(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return get_remote_address(request)
```

Takes the FIRST entry of the X-Forwarded-For chain. Correct only if Railway's edge strips client-supplied XFF headers and prepends the actual client IP. Need to verify Railway's behavior. If Railway just appends, an attacker can spoof XFF to evade per-IP rate limits.

**Mitigation if found exploitable:** trust only the LAST entry of XFF (closest to our server) or use a known-trusted proxy IP list.

**Severity:** Moderate. Even if spoofable, abuse-rate limits are not the only defense (webhook signatures, internal-secret HMAC, AES-GCM tokens are all rate-limit-independent).

### P2.2 — Number-SIGNIFICANT classification depends on undeployed baseline

**Already documented in `Docs/engine/S3_FINDINGS_2026-04-29.md` §"Concrete deferrals"** item #2. Production currently deploys without `Engine/reports/monte_carlo_results.json`, so `percentile = None` and the SIGNIFICANT gate cannot fire. Either deploy the file (and SIGNIFICANT starts firing at ~30-50% rate) or remove the SIGNIFICANT detection logic. Cleaner: remove, since it matches actual behavior.

### P2.3 — CSP `'unsafe-inline'` for script-src and style-src

**Already documented in `security_headers.py` module docstring.** Retained because `html_reading.py`, `unified_view.py`, `admin.html`, and `success.html` all embed inline `<style>` and `<script>` blocks. Future hardening pass: move to nonces. Not launch-blocking — `'unsafe-inline'` with frame-ancestors `'none'` and X-Frame-Options DENY is still substantially better than no CSP.

### P2.4 — `_make_slug` and `hash_oid` §16.5 deferred items

**Already documented in `Docs/engine/SIRR_MASTER_REGISTRY.md` §16.5 deferred surfaces.** Both have explicit revisit thresholds (~10⁵ active orders or transition to multi-tenant). Not launch-blocking.

### P2.5 — Stripe webhook event-type filter logging

**File:** `Engine/web_backend/server.py:1283-1304`

Stripe webhook handler verifies signature, then acts only on `checkout.session.completed`. Other event types are silently dropped with `{"received": True}`. Could log unknown events at INFO level for monitoring. Cosmetic.

### P2.6 — C-CODEX-FINAL-1 (post-CAS dispatch durability outbox)

**Already in `Tools/handoff/SIRR_FUTURE_WORK.md`.** Codex final audit on PR #49 surfaced this — between the order_paid CAS and the email/engine dispatch, a thread/token failure can strand side effects. Outbox pattern recommended at scale. Threshold: 1000+ orders/month or production incident. Not launch-blocking at first-100-customer scale.

---

## Confirmed strong (zero findings)

The audit verified the following surfaces are genuinely well-hardened. Each item below was specifically inspected for the listed concern and passed.

### Token model (`Engine/web_backend/tokens.py`)
- AES-256-GCM AEAD via `crypto.encrypt_bytes`
- Distinct context string `"sirr-token-v1"` (compromise of token keys does not affect Tier 2 storage keys)
- Expiry timestamp embedded in payload, enforced on verify
- Distinct exception classes (TokenMalformed / TokenSignatureInvalid / TokenExpired) — caller chooses which to surface to user
- Verify error messages are constants (no info leak about which step failed)
- O(1) verify, no DB lookup
- Migration handled (HMAC-signed legacy tokens reject cleanly via decryption failure path)

### At-rest encryption (`Engine/web_backend/crypto.py`)
- Per-record keys via HKDF-SHA256 with `salt = order_id`, `info = b"sirr-tier2-v1"`. Compromise of one record's derived key does not compromise any other record.
- Master secret cascade: SIRR_ENCRYPTION_KEY → STRIPE_WEBHOOK_SECRET-derived (dev) → per-process random + warning (dev)
- Production hard-fail (`_is_production()` checks `RAILWAY_DEPLOYMENT_ID`) if no explicit key set
- Magic prefix `b'SIRR' || version_byte` distinguishes encrypted blobs from legacy plaintext
- 12-byte nonce + 16-byte auth tag = AEAD properly applied

### Webhook signatures (`Engine/web_backend/server.py:1283-1356`)
- Stripe via `stripe.Webhook.construct_event` (library-provided, constant-time)
- Lemon Squeezy via `hmac.new(secret, payload, sha256).hexdigest()` + `hmac.compare_digest`
- Both fail-closed: missing secret → 503, signature mismatch → 400 with constant message
- Generic exception catch returns constant `"invalid_signature"` (no detail leak)

### Internal auth (`Engine/web_backend/auth.py`)
- `hmac.compare_digest` for constant-time comparison
- Fail-closed if `SIRR_INTERNAL_SECRET` env var unset (returns 503, not 401 — distinguishes "endpoint disabled" from "wrong secret")

### Input validation (Pydantic on all `@app.post` endpoints)
- `AnalyzeRequest`, `CheckoutRequest`, `DeleteRequest` all explicitly typed
- Optional fields explicitly defaulted to `""` or `None`
- Pydantic enforces type coercion at request boundary

### Error sanitization (`Engine/web_backend/sanitize.py`)
- `sanitize_exception` drops `str(exc)` entirely, keeps only class name + frame paths
- `sanitize_traceback` redacts emails, ISO dates, long digit sequences, non-ASCII bursts (Arabic/CJK names), quoted strings
- Length-cap (default 500 chars) prevents log bloat
- `hash_oid` produces non-reversible 12-char SHA-256 prefix for log correlation

### Log scrubs (verified by grep across server.py, retention.py, order_store.py, email_sender.py)
Every site that interpolates an order_id into a log line uses `hash_oid(order_id)`. The remaining bare-`order_id` `print()` calls are in `[checkout-ls] HTTP {resp.status_code}` (no PII) and `print(json.dumps(result, indent=2))` in `retention.py` (script CLI mode, not web runtime).

### Email sender (`Engine/web_backend/email_sender.py`)
- Resend SDK exception wrapped to type-name only via `EmailSendError(type(exc).__name__) from None` — auth failures often include token prefix in upstream error message; `from None` suppresses chaining
- Order ID shown to customer in email body uses `hash_oid` — name-derived slug doesn't leak to Resend's logs/analytics
- Customer email address transient — not persisted, not logged

### PRIVATE overlay isolation (`Engine/sirr_core/private_overlay.py` + 3 tests)
- Env-var-gated (`SIRR_PRIVATE_OVERLAY` path)
- Graceful degradation when path unset OR file missing
- Tests verify: (a) engine runs cleanly without overlay, (b) overlay loads when present, (c) missing path gracefully degrades

### Rate limiting (`Engine/web_backend/middleware.py`)
- Per-endpoint thresholds proportional to attack surface:
  - `/api/delete` 5/min (guessed-order-ID spam)
  - `/api/checkout` 10/min (Stripe/LS abuse)
  - `/api/internal/*` 60/min (auth-gated, still capped)
  - `/api/analyze` 30/min (demo, no auth)
  - `/api/transliterate` 60/min (cheap but abusable)
- 429 response is styled HTML for browsers, JSON for API callers
- Slowapi in-memory storage (single-replica deployment compatible)

### Security headers (`Engine/web_backend/security_headers.py`)
- HSTS 2-year preload-eligible
- CSP with frame-ancestors `'none'`, upgrade-insecure-requests, conservative source allowlist
- X-Content-Type-Options nosniff
- X-Frame-Options DENY (belt-and-suspenders with CSP)
- Referrer-Policy strict-origin-when-cross-origin
- Permissions-Policy disables geolocation/mic/camera/payment
- Middleware runs response-time, doesn't overwrite if route handler set explicit value

### Customer email handling (path-c)
- Extracted transiently from LS webhook payload at send time
- Never persisted to disk
- Never logged
- Never written to encryption-at-rest surface
- LS UUID normalized to lowercase on persist (RFC 4122 case-insensitive)

---

## What this audit did NOT cover

The aggressive-path S4 explicitly omits items that the conservative-path version would include. Listed for transparency:

- **External pen-test.** Self-audit only. First-100-customer launch tolerance.
- **Engine internals** (S1 stream territory). Convergence-input traditions only got Codex passes during PRs through P2F.
- **Independence-group correctness** (S2 stream territory). Per memory, ~3 of ~10 cross-tradition convergences are genuinely independent vs cognate-derived. PRs #50 + #51 already softened the customer-facing claim; Grok S2 R3 audit defers post-launch.
- **Performance / load testing.** Single-tenant assumptions. First-100-customer scale.
- **Database backup posture.** Railway volume mount exists but backup cadence not externally verified.
- **DNS DNSSEC / DMARC ramp.** Resend setup pending; full email auth not yet exercised end-to-end.

---

## Reproducibility

```bash
cd ~/Desktop/MKB/SIRR\ 2/REPO

# Dep audit
python3 -m pip_audit -r requirements.txt --format json > /tmp/sirr_pip_audit.json

# Vuln-API usage check
grep -rn "set_key\|unset_key" Engine/  # empty = NOT exploitable
grep -rn "import requests\|from requests" Engine/  # empty = NOT exploitable
grep -rn "from PIL\|import PIL" Engine/  # empty = NOT exploitable
grep -rn "extract_zipped_paths" Engine/  # empty = NOT exploitable

# Log-scrub regression check
grep -rnE "print\(.*order_id" Engine/web_backend/ | grep -v hash_oid | grep -v "_short"
# expect: only the [checkout-ls] HTTP status line + retention.py CLI dump

# BASE_URL fail-fast verification (after fix)
RAILWAY_DEPLOYMENT_ID=test python3 -c "import sys; sys.path.insert(0, 'Engine/web_backend'); import server"
# expect: RuntimeError if BASE_URL unset or localhost
```

---

## Closure

S4 audit pass complete. Two follow-up PRs to ship before live-mode flip:

1. **R1 PR — dep upgrades.** `requirements.txt` only. No Codex audit required.
2. **R2 PR — BASE_URL startup validation.** `server.py` startup block. Brief drafted; T2 Codex pre-review required per LANE_DOCTRINE_v3 §3.

Other findings deferred per their own revisit thresholds, all already on `Tools/handoff/SIRR_FUTURE_WORK.md` ledger.

**S4 launch gate: CLEAR pending the two follow-up PRs.**

---

*Filed against Stream S4 of `MULTI_STREAM_AUDIT_PLAN_2026-04-27.md`. Aggressive-path version: self-audit + monitoring. External pen-test deferred to post-first-100-customers per audit plan §"When can LemonSqueezy live-mode flip" aggressive path.*
