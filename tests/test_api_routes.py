"""Integration and regression tests for FastAPI endpoints and P0 UX fixes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_client():
    """Client authenticated with a test session."""
    ac = TestClient(app)
    # Register/login user
    email = f"authtest_runner_{id(ac)}@astrologic.ai"
    ac.post(
        "/signup",
        data={
            "name": "Integration Test User",
            "email": email,
            "phone": "9876543210",
            "password": "ValidPassword123!",
        },
    )
    return ac


def test_get_cities():
    response = client.get("/api/cities")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)
    assert "Pune" in cities
    assert "Mumbai" in cities


def test_default_deny_unauthenticated_api_protection():
    """Verify DefaultDenyAuthMiddleware rejects unauthenticated access to protected API routes."""
    protected_routes = [
        ("/api/kundali", {"year": 1990, "month": 7, "day": 22, "hour": 18, "minute": 30, "city": "Mumbai"}),
        ("/api/domains", {"year": 1993, "month": 3, "day": 10, "hour": 9, "minute": 15, "city": "Pune"}),
        ("/api/generate-chart", {"name": "Test", "year": 1995, "month": 5, "day": 15, "hour": 14.5, "place": "Pune"}),
    ]
    for route, payload in protected_routes:
        resp = client.post(route, json=payload)
        assert resp.status_code == 401
        assert "detail" in resp.json()


def test_generate_chart_endpoint(auth_client):
    payload = {
        "name": "Test Seeker",
        "year": 1995,
        "month": 5,
        "day": 15,
        "hour": 14.5,
        "place": "Pune",
    }
    response = auth_client.post("/api/generate-chart", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "basic_details" in data
    assert "planets" in data


def test_kundali_endpoint(auth_client):
    payload = {
        "year": 1990,
        "month": 7,
        "day": 22,
        "hour": 18,
        "minute": 30,
        "city": "Mumbai",
    }
    response = auth_client.post("/api/kundali", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "lagna" in data
    assert "planets" in data
    assert "scores" in data
    assert "yogas" in data
    assert "doshas" in data


def test_panchang_endpoint():
    payload = {"city": "Delhi"}
    response = client.post("/api/panchang", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Delhi"
    assert "tithi" in data
    assert "nakshatra" in data


def test_panchang_resolve_profile_endpoint():
    """Verify ISSUE-05 fix: profile resolution returns natal Moon, Rashi, and Nakshatra."""
    payload = {
        "name": "Arjun",
        "birth_date": "1995-05-15",
        "birth_time": "14:30",
        "birth_place": "Pune",
    }
    response = client.post("/api/panchang/resolve-profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "rashi" in data
    assert "nakshatra" in data
    assert "nakshatra_pada" in data
    assert data["name"] == "Arjun"


def test_panchang_decision_endpoint():
    """Verify ISSUE-05 fix: Vedic decision assistant computes activity recommendations."""
    payload = {
        "activity": "travel",
        "city": "Pune",
        "user_rashi": "Vrischika",
        "user_nakshatra": "Anuradha",
    }
    response = client.post("/api/panchang/decision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data
    assert data["recommendation"] in ["PROCEED", "CAUTION", "AVOID", "MIXED SIGNALS", "FAVORABLE", "NEUTRAL"]
    assert "reasons" in data


def test_panchang_calendar_ics_endpoint():
    """Verify ISSUE-05 fix: iCalendar (.ics) export is generated correctly."""
    response = client.get("/api/panchang/calendar.ics?city=Pune&limit=10")
    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert "BEGIN:VCALENDAR" in response.text
    assert "END:VCALENDAR" in response.text
    assert "PRODID" in response.text


def test_daily_horoscope_endpoint():
    response = client.get("/api/daily-horoscope/aries")
    assert response.status_code == 200
    data = response.json()
    assert data["sign"] == "Aries"
    assert "horoscope" in data

    # Test invalid sign
    bad_resp = client.get("/api/daily-horoscope/unknownsign")
    assert bad_resp.status_code == 400


def test_horoscope_by_index():
    response = client.get("/api/horoscope/0")
    assert response.status_code == 200
    data = response.json()
    assert data["sign"] == "Aries"


def test_festivals_endpoints():
    today_resp = client.get("/api/festivals/today")
    assert today_resp.status_code == 200
    assert "festivals" in today_resp.json()

    upcoming_resp = client.get("/api/festivals/upcoming")
    assert upcoming_resp.status_code == 200
    assert "festivals" in upcoming_resp.json()


def test_prediction_and_chat(auth_client):
    payload = {
        "year": 1995,
        "month": 5,
        "day": 15,
        "hour": 14.5,
        "city": "Pune",
    }
    pred_resp = auth_client.post("/api/prediction", json=payload)
    assert pred_resp.status_code == 200
    data = pred_resp.json()
    assert "marriage_prediction" in data
    assert "career_prediction" in data

    # Test chat
    chat_resp = auth_client.post("/api/chat", json={"message": "How is my career progression?"})
    assert chat_resp.status_code == 200
    assert "reply" in chat_resp.json()


def test_kundali_chat_endpoint(auth_client):
    k_payload = {
        "year": 1990,
        "month": 7,
        "day": 22,
        "hour": 18,
        "minute": 30,
        "city": "Mumbai",
    }
    k_resp = auth_client.post("/api/kundali", json=k_payload)
    chart = k_resp.json()

    chat_payload = {
        "message": "When will I get married and how is my spouse?",
        "chart": chart,
    }
    chat_resp = auth_client.post("/api/kundali-chat", json=chat_payload)
    assert chat_resp.status_code == 200
    assert "reply" in chat_resp.json()
    assert chat_resp.json()["topic"] == "marriage"


def test_domains_endpoint(auth_client):
    payload = {
        "year": 1993,
        "month": 3,
        "day": 10,
        "hour": 9,
        "minute": 15,
        "city": "Pune",
    }
    resp = auth_client.post("/api/domains", json=payload)
    assert resp.status_code == 200
    assert "domains" in resp.json()


def test_blogs_public_endpoints():
    resp = client.get("/api/blogs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_blog_article_routing_issue_01():
    """Verify ISSUE-01 fix: both /blog/{id} and /blogs/{id} render blog-detail page."""
    resp1 = client.get("/blog/1")
    assert resp1.status_code == 200
    assert "text/html" in resp1.headers["content-type"]
    assert "AstroLogic | Blog" in resp1.text

    resp2 = client.get("/blogs/1")
    assert resp2.status_code == 200
    assert "text/html" in resp2.headers["content-type"]
    assert "AstroLogic | Blog" in resp2.text


def test_blog_invalid_id_not_found():
    """Verify API returns 404 for non-existent blog ID."""
    resp = client.get("/api/blogs/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Blog not found"


def test_login_error_feedback_issue_02():
    """Verify ISSUE-02 fix: failed login displays error alert in HTML."""
    resp = client.post(
        "/login",
        data={"email": "nonexistent_user@astrologic.ai", "password": "wrongpassword"},
    )
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Invalid email or password" in resp.text
    assert 'class="alert error"' in resp.text
    assert 'style="display:flex;"' in resp.text


def test_login_success_redirect():
    """Verify successful authentication issues session and redirects."""
    temp_client = TestClient(app)
    email = f"success_login_{id(temp_client)}@astrologic.ai"
    # Create user
    temp_client.post(
        "/signup",
        data={"name": "Success User", "email": email, "phone": "1234567890", "password": "SecurePassword123!"},
    )
    # Logout
    temp_client.get("/logout")

    # Login
    login_resp = temp_client.post(
        "/login",
        data={"email": email, "password": "SecurePassword123!"},
        follow_redirects=False,
    )
    assert login_resp.status_code == 303
    assert login_resp.headers["location"] == "/"


def test_prediction_nonblocking_feedback_issue_03():
    """Verify ISSUE-03 fix: prediction page includes non-blocking feedback button and dismissible modal."""
    resp = client.get("/prediction")
    assert resp.status_code == 200
    # Check that non-blocking banner and trigger function are present
    assert "triggerPredictionFeedback" in resp.text
    assert "Share Feedback on Predictions" in resp.text
    assert "closeFeedbackModalBtn" in resp.text


def test_web_pages_render():
    routes = [
        "/",
        "/prediction",
        "/panchang.html",
        "/blogs",
        "/blog/1",
        "/blogs/1",
        "/about",
        "/horoscope",
        "/kundali",
        "/login",
        "/signup",
    ]
    for route in routes:
        resp = client.get(route)
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
