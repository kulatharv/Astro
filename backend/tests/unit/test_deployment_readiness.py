"""
Unit and integration tests for Database and Deployment Readiness (CF-07).
"""

import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from gateway.main import app
from shared.db.session import check_db_health, engine
from scripts.backup_restore import backup_database, verify_backup


class TestDeploymentReadiness:
    """Test suite for deployment readiness probes, connection pooling, and backup verification."""

    def test_readiness_probe_healthy(self):
        """Readiness probe returns 200 when database and core services are active."""
        client = TestClient(app)
        res = client.get("/ready")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"
        assert data["cache"] == "operational"
        assert "ephemeris" in data

    def test_readiness_probe_database_failure(self):
        """Readiness probe returns 503 when primary database connectivity drops."""
        client = TestClient(app)
        with patch("shared.db.session.check_db_health", return_value=False):
            res = client.get("/ready")
            assert res.status_code == 503
            data = res.json()
            assert data["status"] == "not_ready"
            assert data["database"] == "disconnected"

    def test_database_backup_and_integrity_verification(self, tmp_path):
        """Verify automated database backup generation and SQLite PRAGMA integrity verification."""
        backup_dir = tmp_path / "test_backups"
        backup_file = backup_database(destination_dir=str(backup_dir))

        assert os.path.exists(backup_file)
        assert os.path.getsize(backup_file) > 0

        # Run integrity verification
        assert verify_backup(backup_file) is True

    def test_connection_pooling_configuration(self):
        """Verify that engine has pool_pre_ping enabled for reliable connection health."""
        assert engine.pool._pre_ping is True
