"""
Unit tests for Swiss Ephemeris runtime mode verification and observable diagnostics (CF-02).
"""

import pytest
from fastapi.testclient import TestClient

from shared.ephemeris.wrapper import get_ephemeris_diagnostics
from gateway.main import app


class TestEphemerisDiagnostics:
    """Tests for Swiss Ephemeris runtime detection, accuracy tiering, and licensing reporting."""

    def test_ephemeris_diagnostics_structure(self):
        diag = get_ephemeris_diagnostics()
        assert isinstance(diag, dict)
        assert diag["status"] == "operational"
        assert diag["runtime_mode"] in ["moshier", "swiss_ephemeris"]
        assert isinstance(diag["is_moshier_fallback"], bool)
        assert "swe_c_version" in diag
        assert "ephe_path" in diag
        assert "accuracy_level" in diag
        assert "commercial_licensing" in diag

    def test_current_repo_mode_is_moshier(self):
        """
        Verify that in the current repository without .se1 assets,
        the runtime safely and deterministically reports Moshier fallback mode.
        """
        diag = get_ephemeris_diagnostics()
        assert diag["runtime_mode"] == "moshier"
        assert diag["is_moshier_fallback"] is True
        assert diag["se1_files_found"] == 0
        assert "Moshier" in diag["accuracy_level"]
        assert "Open-source Moshier" in diag["commercial_licensing"]

    def test_health_endpoint_exposes_ephemeris_mode(self):
        client = TestClient(app)
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "ephemeris_mode" in data
        assert data["ephemeris_mode"] == "moshier"

    def test_system_ephemeris_api_endpoint(self):
        client = TestClient(app)
        res = client.get("/api/system/ephemeris")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "operational"
        assert data["runtime_mode"] == "moshier"
        assert data["is_moshier_fallback"] is True
