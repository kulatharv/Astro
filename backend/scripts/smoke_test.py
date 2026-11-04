"""
Comprehensive Staging Smoke Test Suite for AstroLogic AI.
Executes all verification checks defined in CRITICAL_FIXES_REPORT.md.
"""

import sys
import uuid
import time
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from gateway.main import app
from scripts.backup_restore import backup_database, verify_backup

def log_step(name: str, passed: bool, details: str = ""):
    symbol = "[PASS]" if passed else "[FAIL]"
    print(f"{symbol} {name}: {details}")

def run_smoke_test():
    print("=" * 65)
    print(" AstroLogic AI — Staging Smoke Test Execution")
    print("=" * 65)
    
    client = TestClient(app)
    all_passed = True

    # 1. Readiness Probe
    try:
        res = client.get("/ready")
        data = res.json()
        is_ready = res.status_code == 200 and data.get("database") == "ok"
        log_step("1. Orchestrator Readiness Probe (/ready)", is_ready, f"HTTP {res.status_code}, db={data.get('database')}, ephe={data.get('ephemeris_mode')}")
        all_passed = all_passed and is_ready
    except Exception as e:
        log_step("1. Orchestrator Readiness Probe (/ready)", False, str(e))
        all_passed = False

    # 2. Ephemeris Diagnostics
    try:
        res = client.get("/api/system/ephemeris")
        data = res.json()
        ephe_ok = res.status_code == 200 and "mode" in data and "commercial_license_notice" in data
        log_step("2. Ephemeris Diagnostics (/api/system/ephemeris)", ephe_ok, f"mode={data.get('mode')}, se1_files={data.get('se1_files_count')}")
        all_passed = all_passed and ephe_ok
    except Exception as e:
        log_step("2. Ephemeris Diagnostics (/api/system/ephemeris)", False, str(e))
        all_passed = False

    # 3. Rate Limiting Throttling (Auth route limit = 15/min)
    try:
        test_ip_client = TestClient(app, client=("198.51.100.99", 50000))
        statuses = []
        for i in range(16):
            r = test_ip_client.post("/signup", data={"name": "Throttled", "email": f"t_{i}@ex.com", "password": "Pwd!"})
            statuses.append(r.status_code)
        rate_limited = 429 in statuses
        log_step("3. Security Rate Limiting (/signup 15/min limit)", rate_limited, f"16 rapid requests yielded: 1st={statuses[0]}, 16th={statuses[-1]}")
        all_passed = all_passed and rate_limited
    except Exception as e:
        log_step("3. Security Rate Limiting", False, str(e))
        all_passed = False

    # 4. Saved Charts Multi-Tenant CRUD & Isolation
    try:
        u1 = uuid.uuid4().hex[:6]
        u2 = uuid.uuid4().hex[:6]
        c1 = TestClient(app)
        c2 = TestClient(app)

        c1.post("/signup", data={"name": f"User {u1}", "email": f"u_{u1}@example.com", "password": "Password123!"})
        c2.post("/signup", data={"name": f"User {u2}", "email": f"u_{u2}@example.com", "password": "Password123!"})

        # User 1 saves a chart
        save_res = c1.post("/api/kundali/saved-charts", json={
            "person_name": "Albert Einstein",
            "date_of_birth": "1879-03-14",
            "time_of_birth": "11:30:00",
            "latitude": 48.4011,
            "longitude": 9.9876,
            "place_name": "Ulm, Germany",
            "notes": "Relativity pioneer chart",
            "tags": "physics, genius",
            "is_favorite": True
        })
        chart_id = save_res.json()["chart_id"]

        # User 1 reads it back
        get_res = c1.get(f"/api/kundali/saved-charts/{chart_id}")
        u1_ok = get_res.status_code == 200 and get_res.json()["person_name"] == "Albert Einstein"

        # User 2 attempts to read User 1's chart -> must get 404
        cross_res = c2.get(f"/api/kundali/saved-charts/{chart_id}")
        isolation_ok = cross_res.status_code == 404

        # User 1 deletes their chart -> 204
        del_res = c1.delete(f"/api/kundali/saved-charts/{chart_id}")
        del_ok = del_res.status_code == 204

        saved_charts_ok = u1_ok and isolation_ok and del_ok
        log_step("4. Multi-Tenant Saved Charts Persistence", saved_charts_ok, f"Saved ID={chart_id[:8]}..., User2 cross-access denied (404), Delete (204)")
        all_passed = all_passed and saved_charts_ok
    except Exception as e:
        log_step("4. Multi-Tenant Saved Charts Persistence", False, str(e))
        all_passed = False

    # 5. Database Online Backup & Verification
    try:
        backup_path = backup_database()
        verified = verify_backup(backup_path)
        log_step("5. Point-in-Time Database Backup & Integrity", verified, f"Artifact: {Path(backup_path).name}")
        all_passed = all_passed and verified
    except Exception as e:
        log_step("5. Point-in-Time Database Backup & Integrity", False, str(e))
        all_passed = False

    print("=" * 65)
    if all_passed:
        print(" [ALL CHECKS PASSED] AstroLogic AI is verified production-ready!")
    else:
        print(" [WARNING] One or more staging smoke checks failed.")
    print("=" * 65)
    return all_passed

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
