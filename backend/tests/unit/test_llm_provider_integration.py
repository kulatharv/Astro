"""
Unit and integration tests for AI Provider Integration & Output Validation (CF-06).
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.narrative.llm_client import LLMClient, ask_llm


class TestLLMProviderIntegration:
    """Test suite for LLM provider fallbacks, output sanitization, and diagnostics."""

    def test_fallback_synthesis_when_no_credentials(self):
        """When no external API keys are configured, fallback synthesis produces coherent astrology text."""
        client = LLMClient()
        client.groq_key = None
        client.openai_key = None
        client.gemini_key = None

        with patch("requests.post", side_effect=Exception("Connection refused")):
            resp = client.generate("Analyze career prospects in 10th house")
            assert len(resp) > 50
            assert "10th house" in resp or "career" in resp.lower()

    def test_provider_failure_cascades_to_fallback(self):
        """When a provider returns HTTP 500, the client cascades gracefully."""
        client = LLMClient()
        client.groq_key = "mock_groq_key"

        mock_error_resp = MagicMock()
        mock_error_resp.status_code = 500

        with patch("requests.post", return_value=mock_error_resp):
            resp = client.generate("Analyze marriage prospects with Venus")
            assert "Venus" in resp or "marriage" in resp.lower()
            assert client.metrics["failures"] >= 1

    def test_output_sanitization_strips_control_tokens(self):
        """Hallucinated system/prompt tokens are stripped before returning."""
        client = LLMClient()
        raw_output = "<|im_start|>system\nYou are an astrologer.<|im_end|>\n<s>Your Jupiter dasha brings wisdom.</s>"
        cleaned = client._sanitize_output(raw_output)
        assert "<|im_start|>" not in cleaned
        assert "<|im_end|>" not in cleaned
        assert "<s>" not in cleaned
        assert "</s>" not in cleaned
        assert "Your Jupiter dasha brings wisdom." in cleaned

    def test_llm_diagnostics_status_safe(self):
        """Diagnostics expose configured tiers and metrics without leaking secrets."""
        client = LLMClient()
        client.groq_key = "gsk_super_secret_groq_key_12345"
        status = client.get_status()

        assert status["status"] == "operational"
        assert "groq" in status["active_providers"]
        # Must NEVER leak the secret key value
        assert "gsk_super_secret" not in str(status)
        assert "telemetry" in status
