"""Rate limiting middleware.

Uses slowapi (FastAPI wrapper around limits) with in-memory storage.
For multi-replica deployments, switch to Redis via the RATELIMIT_STORAGE
env var slowapi reads automatically.

Design:
- Per-IP limits by default (slowapi.util.get_remote_address)
- Honors X-Forwarded-For when Railway sets it (trust proxy header)
- Rate-limit exceeded (429) renders the same styled error page for
  browsers that the 404/401/500 paths use, JSON for API clients
- Strict-by-design: once a limit fires, caller gets 429 until the
  window expires

Limits chosen per-endpoint based on attack surface:
  /api/delete            → 5/minute  (guessed-order-ID spam deterrent)
  /api/checkout          → 10/minute (stops abuse of Stripe/LS hits)
  /api/internal/*        → 60/minute (auth-gated, but still capped)
  /api/analyze           → 30/minute (demo endpoint, no auth)
  /api/transliterate     → 60/minute (cheap but abusable)
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from errors import render_page


def _key_func(request: Request) -> str:
    """Identify the caller. Prefer X-Forwarded-For (Railway sets it for
    real client IP), fall back to peer address."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        # First entry is the original client
        return fwd.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return styled HTML to browsers, JSON to API callers. Mirrors the
    shape of the existing StarletteHTTPException handler in server.py."""
    path = request.url.path or ""
    retry_after = getattr(exc, "detail", "too many requests")

    if path.startswith("/api/"):
        return JSONResponse(
            status_code=429,
            content={"detail": "rate limit exceeded", "retry_after": str(retry_after)},
            headers={"Retry-After": "60"},
        )

    body = render_page(
        title="Rate limited",
        code="429",
        headline="Slow down, please.",
        detail=(
            "You've made a lot of requests in a short time. "
            "Wait a minute, then try again."
        ),
        actions=[("Return home", "/", True)],
    )
    return HTMLResponse(content=body, status_code=429, headers={"Retry-After": "60"})
