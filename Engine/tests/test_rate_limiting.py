"""Tests for rate limiting (middleware.py).

Each test registers its own uniquely-pathed endpoint. slowapi keys its
internal counters by endpoint, so each test gets an isolated budget
without any reset-between-tests logic needed.
"""
from __future__ import annotations

import os
import sys

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web_backend"))
from middleware import limiter, rate_limit_exceeded_handler, _key_func  # noqa: E402


# One app at module level — but each test hits a different path, so
# slowapi's per-endpoint counters are naturally isolated per test.
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# — Endpoint per test, unique path, unique budget —

@app.get("/api/under_limit")
@limiter.limit("3/minute")
async def _under_limit(request: Request):
    return {"ok": True}


@app.get("/api/over_limit_api")
@limiter.limit("3/minute")
async def _over_limit_api(request: Request):
    return {"ok": True}


@app.get("/browser_over_limit")
@limiter.limit("3/minute")
async def _browser_over_limit(request: Request):
    return {"ok": True}


@app.get("/api/per_ip_a")
@limiter.limit("3/minute")
async def _per_ip_a(request: Request):
    return {"ok": True}


client = TestClient(app)


def test_under_limit_allows_requests():
    # 3 requests allowed, 0 blocked
    for i in range(3):
        r = client.get("/api/under_limit", headers={"X-Forwarded-For": "192.0.2.10"})
        assert r.status_code == 200, f"request {i + 1} should have succeeded"


def test_over_limit_returns_429_json_for_api():
    # Exhaust budget from a fresh IP
    for _ in range(3):
        client.get("/api/over_limit_api", headers={"X-Forwarded-For": "192.0.2.20"})
    r = client.get("/api/over_limit_api", headers={"X-Forwarded-For": "192.0.2.20"})
    assert r.status_code == 429
    assert r.headers.get("content-type", "").startswith("application/json")
    body = r.json()
    assert "detail" in body
    assert "rate limit" in body["detail"].lower()
    assert r.headers.get("retry-after") == "60"


def test_over_limit_returns_styled_html_for_browser_path():
    for _ in range(3):
        client.get("/browser_over_limit", headers={"X-Forwarded-For": "192.0.2.30"})
    r = client.get("/browser_over_limit", headers={"X-Forwarded-For": "192.0.2.30"})
    assert r.status_code == 429
    assert r.headers.get("content-type", "").startswith("text/html")
    assert "slow down" in r.text.lower()
    assert "429" in r.text
    assert r.headers.get("retry-after") == "60"


def test_rate_limit_is_per_ip():
    """Different X-Forwarded-For values have separate budgets on the
    same endpoint."""
    # Use up IP A's budget
    for _ in range(3):
        r = client.get("/api/per_ip_a", headers={"X-Forwarded-For": "192.0.2.40"})
        assert r.status_code == 200
    # IP A blocked
    r = client.get("/api/per_ip_a", headers={"X-Forwarded-For": "192.0.2.40"})
    assert r.status_code == 429
    # IP B still works (fresh budget on same endpoint, different key)
    r = client.get("/api/per_ip_a", headers={"X-Forwarded-For": "192.0.2.41"})
    assert r.status_code == 200


def test_x_forwarded_for_first_ip_is_used():
    """If X-Forwarded-For has multiple IPs (proxy chain), use the first."""
    class FakeRequest:
        class _Client:
            host = "127.0.0.1"
        def __init__(self, xff):
            self.headers = {"x-forwarded-for": xff} if xff else {}
            self.client = self._Client()

    # Multi-hop chain
    assert _key_func(FakeRequest("10.0.0.1, 10.0.0.2, 10.0.0.3")) == "10.0.0.1"
    # Single IP
    assert _key_func(FakeRequest("10.0.0.5")) == "10.0.0.5"
    # No header falls back to remote address
    assert _key_func(FakeRequest(None)) == "127.0.0.1"
