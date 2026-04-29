import pytest
import sys
import importlib


def _force_reimport_server(monkeypatch):
    """Drop cached server module + put web_backend on path, so importlib
    actually re-executes the module-level startup checks."""
    sys.modules.pop("server", None)
    monkeypatch.syspath_prepend("Engine/web_backend")


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
