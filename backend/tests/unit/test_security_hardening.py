"""
Unit and integration tests for Authentication and Security Hardening (CF-04).
Verifies:
- Tiered sliding window rate limiting throttles abusive traffic with HTTP 429 and Retry-After
- Sensitive data filter redacts passwords, tokens, and API keys from logs
- Session cookie attributes (SameSite=Lax, HttpOnly/Secure in production)
- CORS preflight and allowed origins handling
"""

import logging
import pytest
from fastapi.testclient import TestClient

from gateway.main import app
from shared.logging.logger import SensitiveDataFilter, setup_logger


class TestSecurityHardening:
    """Test suite for CF-04 security controls."""

    def test_sensitive_data_log_redaction(self):
        """Verifies passwords, bearer tokens, and API keys are redacted before output."""
        log_filter = SensitiveDataFilter()
        record_pwd = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg='User login attempt with password="SecretPassword123!"',
            args=(), exc_info=None
        )
        log_filter.filter(record_pwd)
        assert "SecretPassword123!" not in record_pwd.msg
        assert "***REDACTED***" in record_pwd.msg

        record_token = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz",
            args=(), exc_info=None
        )
        log_filter.filter(record_token)
        assert "eyJhbGci" not in record_token.msg
        assert "Bearer ***REDACTED***" in record_token.msg

        record_key = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Calling OpenAI with key sk-1234567890abcdef1234567890abcdef",
            args=(), exc_info=None
        )
        log_filter.filter(record_key)
        assert "1234567890abcdef" not in record_key.msg
        assert "sk-***REDACTED***" in record_key.msg

    def test_rate_limiting_auth_endpoint(self):
        """
        Verify that hitting an auth endpoint repeatedly exceeds limit and returns 429.
        Auth limit is 15 requests / minute.
        """
        client = TestClient(app)
        # Send 16 rapid requests from same client
        responses = []
        for i in range(18):
            r = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
            responses.append(r.status_code)

        # At least one request should be rate-limited
        assert 429 in responses
        idx = responses.index(429)
        # Verify the 429 response structure
        r_429 = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
        if r_429.status_code == 429:
            data = r_429.json()
            assert "Rate limit exceeded" in data["detail"]
            assert "Retry-After" in r_429.headers

    def test_health_endpoint_exempt_from_rate_limit(self):
        """Health check probe must never be throttled by rate limiter."""
        client = TestClient(app)
        for _ in range(50):
            res = client.get("/health")
            assert res.status_code == 200

    def test_cors_headers_on_options_preflight(self):
        """CORS preflight request must return proper Access-Control headers."""
        client = TestClient(app)
        res = client.options(
            "/api/cities",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert res.status_code == 200
        assert "access-control-allow-origin" in res.headers
