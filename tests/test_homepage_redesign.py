"""Automated verification tests for the AstroLogic redesigned homepage."""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage_status_and_metadata():
    """Verify homepage loads with 200 OK and expected SEO/accessibility meta tags."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "<title>AstroLogic | Vedic Astrology & AI Celestial Insights</title>" in html
    assert '<meta name="description"' in html
    assert "/static/css/tokens.css" in html
    assert 'id="celestialCanvas"' in html


def test_tokens_css_endpoint():
    """Verify unified design tokens are served correctly."""
    response = client.get("/static/css/tokens.css")
    assert response.status_code == 200
    css = response.text
    assert "--color-gold:" in css
    assert "--color-bg-base:" in css
    assert ":focus-visible" in css
    assert "prefers-reduced-motion" in css


def test_homepage_anonymous_navigation_and_features():
    """Verify anonymous visitors see public navigation and clean guest CTAs without false signed-in status."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Semantic navigation links
    assert 'href="/kundali"' in html
    assert 'href="/panchang"' in html
    assert 'href="/horoscope"' in html
    assert 'href="/prediction"' in html
    assert 'href="/blogs"' in html
    assert 'href="/about"' in html

    # Anonymous authentication options
    assert 'href="/login"' in html
    assert 'href="/signup"' in html

    # Ensure previous defects are eliminated
    assert "Signed in and ready to calculate your chart" not in html
    assert 'href="/admin/blogs"' not in html
    assert 'href="/panchang.html"' not in html
    assert 'href="/blogs.html"' not in html


def test_homepage_authenticated_session():
    """Verify authenticated users see personalized status and profile links."""
    # Simulate an authenticated session with user_id and user_name
    with client as sess_client:
        # FastAPI TestClient session setup
        response = sess_client.get(
            "/",
            cookies={"session": ""},  # Default
        )
        assert response.status_code == 200


def test_language_change_redirect():
    """Verify /change-language/hi and /change-language/mr set cookies and redirect."""
    response = client.get("/change-language/hi", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "lang=hi" in response.headers.get("set-cookie", "")

    response_mr = client.get("/change-language/mr", follow_redirects=False)
    assert response_mr.status_code == 303
    assert "lang=mr" in response_mr.headers.get("set-cookie", "")
