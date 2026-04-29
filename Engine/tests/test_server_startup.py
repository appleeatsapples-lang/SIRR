import pytest
import sys
import importlib
from pathlib import Path


# Resolve web_backend path from this test file's location, NOT cwd.
# Relative paths like "Engine/web_backend" leak through pytest cwd
# (Codex T5 round 1 finding 2026-04-29).
WEB_BACKEND_PATH = Path(__file__).resolve().parents[1] / "web_backend"


@pytest.fixture(autouse=True)
def _server_module_cleanup():
    """Ensure server module is dropped from sys.modules before AND after
    each test, so test order cannot leak cached state. Belt-and-suspenders
    alongside the explicit sys.modules.pop calls inside tests — protects
    against the case where a test raises an unexpected exception before
    reaching its trailing cleanup line."""
    sys.modules.pop("server", None)
    yield
    sys.modules.pop("server", None)


def _force_reimport_server(monkeypatch):
    """Drop cached server module + put web_backend on path, so importlib
    actually re-executes the module-level startup checks.

    Uses absolute path computed from __file__ rather than relative path
    to be cwd-independent (test runs correctly from repo root or Engine/).
    """
    sys.modules.pop("server", None)
    monkeypatch.syspath_prepend(str(WEB_BACKEND_PATH))


def _seed_prod_baseline(monkeypatch):
    """Seed production indicator + crypto secret so the import hits the
    BASE_URL check rather than the crypto fail-fast."""
    monkeypatch.setenv("RAILWAY_DEPLOYMENT_ID", "test-deploy")
    monkeypatch.setenv("SIRR_ENCRYPTION_KEY", "a" * 64)


def test_base_url_missing_in_production_rejected(monkeypatch):
    """Path A: BASE_URL unset under RAILWAY_DEPLOYMENT_ID → RuntimeError."""
    _seed_prod_baseline(monkeypatch)
    monkeypatch.delenv("BASE_URL", raising=False)
    _force_reimport_server(monkeypatch)
    with pytest.raises(RuntimeError, match="BASE_URL"):
        importlib.import_module("server")
    sys.modules.pop("server", None)  # cleanup for next test


def test_base_url_localhost_rejected_in_production(monkeypatch):
    """Path A: http://localhost prefix rejected."""
    _seed_prod_baseline(monkeypatch)
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
    _force_reimport_server(monkeypatch)
    with pytest.raises(RuntimeError, match="BASE_URL"):
        importlib.import_module("server")
    sys.modules.pop("server", None)


def test_base_url_127_loopback_rejected_in_production(monkeypatch):
    """Path A: http://127.0.0.1 prefix rejected."""
    _seed_prod_baseline(monkeypatch)
    monkeypatch.setenv("BASE_URL", "http://127.0.0.1:8000")
    _force_reimport_server(monkeypatch)
    with pytest.raises(RuntimeError, match="BASE_URL"):
        importlib.import_module("server")
    sys.modules.pop("server", None)


def test_base_url_unspecified_rejected_in_production(monkeypatch):
    """Path A: http://0.0.0.0 prefix rejected."""
    _seed_prod_baseline(monkeypatch)
    monkeypatch.setenv("BASE_URL", "http://0.0.0.0:8000")
    _force_reimport_server(monkeypatch)
    with pytest.raises(RuntimeError, match="BASE_URL"):
        importlib.import_module("server")
    sys.modules.pop("server", None)


def test_base_url_valid_https_proceeds_in_production(monkeypatch):
    """Path A positive: a public HTTPS URL passes the check."""
    _seed_prod_baseline(monkeypatch)
    monkeypatch.setenv("BASE_URL", "https://web-production-ec2871.up.railway.app")
    _force_reimport_server(monkeypatch)
    # Should NOT raise. We don't assert anything about the imported module —
    # just that import completes without RuntimeError on BASE_URL.
    importlib.import_module("server")
    sys.modules.pop("server", None)
