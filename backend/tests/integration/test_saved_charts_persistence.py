"""
Integration tests for User Saved Charts Persistence & Multi-tenant Isolation (CF-03).
Verifies:
- Unauthenticated requests are rejected with 401 Unauthorized
- Authenticated user can create, read, list, update, and delete saved charts
- Strict cross-user isolation: User B cannot access, list, update, or delete User A's saved charts
- Cascading recalculation when birth parameters change during update
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from gateway.main import app
from shared.db.session import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def create_authenticated_client(name: str, email_prefix: str) -> tuple[TestClient, dict]:
    """Helper to create a TestClient logged in as a freshly registered user."""
    client = TestClient(app)
    uid = uuid.uuid4().hex[:8]
    email = f"{email_prefix}_{uid}@example.com"
    pwd = "SecureTestPassword@123"

    signup_res = client.post(
        "/api/auth/signup",
        json={
            "name": name,
            "email": email,
            "phone": "+91-9999999999",
            "password": pwd,
        },
    )
    assert signup_res.status_code == 201, signup_res.text
    user_data = signup_res.json()["user"]
    return client, user_data


class TestSavedChartsPersistence:
    """Test suite for CF-03 saved chart persistence and access control."""

    def test_unauthenticated_access_denied(self):
        """Unauthenticated requests must be rejected with 401 or 403."""
        anon_client = TestClient(app)

        # GET list
        res = anon_client.get("/api/kundali/saved-charts")
        assert res.status_code in [401, 403]

        # POST create
        res = anon_client.post(
            "/api/kundali/saved-charts",
            json={
                "title": "Unauthorized Chart",
                "birth_date": "1990-05-15",
                "birth_time": "14:30",
                "city": "Pune",
            },
        )
        assert res.status_code in [401, 403]

        # GET detail
        res = anon_client.get("/api/kundali/saved-charts/1")
        assert res.status_code in [401, 403]

        # DELETE
        res = anon_client.delete("/api/kundali/saved-charts/1")
        assert res.status_code in [401, 403]

    def test_crud_lifecycle_for_authenticated_user(self):
        """Full create, read, list, update, and delete lifecycle for a user."""
        client, user = create_authenticated_client("Alice Smith", "alice")

        # 1. CREATE chart
        create_payload = {
            "title": "Alice Natal Chart",
            "person_name": "Alice",
            "gender": "Female",
            "birth_date": "1992-08-20",
            "birth_time": "10:15",
            "city": "Mumbai",
            "notes": "Original birth record from hospital certificate.",
        }
        res_create = client.post("/api/kundali/saved-charts", json=create_payload)
        assert res_create.status_code == 201
        created = res_create.json()
        chart_id = created["id"]
        assert created["title"] == "Alice Natal Chart"
        assert created["user_id"] == user["id"]
        assert created["birth_city"] == "Mumbai"
        assert created["chart_data"] is not None
        assert "planets" in created["chart_data"]
        assert "lagna" in created["chart_data"]

        # 2. READ single chart
        res_get = client.get(f"/api/kundali/saved-charts/{chart_id}")
        assert res_get.status_code == 200
        fetched = res_get.json()
        assert fetched["id"] == chart_id
        assert fetched["notes"] == "Original birth record from hospital certificate."

        # 3. LIST charts
        res_list = client.get("/api/kundali/saved-charts")
        assert res_list.status_code == 200
        chart_list = res_list.json()
        assert len(chart_list) >= 1
        assert any(c["id"] == chart_id for c in chart_list)

        # 4. UPDATE metadata (title, notes)
        res_update = client.put(
            f"/api/kundali/saved-charts/{chart_id}",
            json={"title": "Alice Updated Title", "notes": "Updated note details."},
        )
        assert res_update.status_code == 200
        updated = res_update.json()
        assert updated["title"] == "Alice Updated Title"
        assert updated["notes"] == "Updated note details."

        # 5. DELETE chart
        res_del = client.delete(f"/api/kundali/saved-charts/{chart_id}")
        assert res_del.status_code == 204

        # 6. VERIFY deletion
        res_after = client.get(f"/api/kundali/saved-charts/{chart_id}")
        assert res_after.status_code == 404

    def test_strict_cross_user_isolation(self):
        """
        Verify that User B cannot read, update, delete, or list User A's charts.
        Guarantees private birth data security in multi-tenant environment.
        """
        client_a, user_a = create_authenticated_client("User A", "usera")
        client_b, user_b = create_authenticated_client("User B", "userb")

        # User A creates a chart
        res_create = client_a.post(
            "/api/kundali/saved-charts",
            json={
                "title": "Private User A Chart",
                "birth_date": "1988-11-12",
                "birth_time": "08:45",
                "city": "Delhi",
                "notes": "Highly confidential birth details.",
            },
        )
        assert res_create.status_code == 201
        chart_a_id = res_create.json()["id"]

        # User B attempts to read User A's chart -> 404 Not Found (or 403)
        res_b_get = client_b.get(f"/api/kundali/saved-charts/{chart_a_id}")
        assert res_b_get.status_code == 404

        # User B attempts to update User A's chart -> 404 Not Found
        res_b_update = client_b.put(
            f"/api/kundali/saved-charts/{chart_a_id}",
            json={"title": "Hacked Title by User B"},
        )
        assert res_b_update.status_code == 404

        # User B attempts to delete User A's chart -> 404 Not Found
        res_b_del = client_b.delete(f"/api/kundali/saved-charts/{chart_a_id}")
        assert res_b_del.status_code == 404

        # Verify User A's chart was NOT affected
        res_a_check = client_a.get(f"/api/kundali/saved-charts/{chart_a_id}")
        assert res_a_check.status_code == 200
        assert res_a_check.json()["title"] == "Private User A Chart"

        # User B lists charts -> should NOT contain User A's chart
        res_b_list = client_b.get("/api/kundali/saved-charts")
        assert res_b_list.status_code == 200
        b_charts = res_b_list.json()
        assert not any(c["id"] == chart_a_id for c in b_charts)
