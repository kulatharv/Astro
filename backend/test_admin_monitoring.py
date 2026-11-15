"""
Integration Test Suite for Admin Observatory & Monitoring API.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from shared.db.session import SessionLocal
from modules.admin.api import (
    get_admin_metrics,
    get_admin_users,
    get_admin_ghost_sessions,
    get_admin_activity_logs,
    trigger_whatsapp_briefings,
    admin_flush_cache,
)


def run_tests():
    db = SessionLocal()
    print("\n========================================================")
    print("      RUNNING ADMIN OBSERVATORY MONITORING TESTS        ")
    print("========================================================")

    # 1. Test Aggregated Observatory Metrics
    metrics = get_admin_metrics(db)
    print("1. Metrics Status:", metrics["status"])
    print(f"   Total Users: {metrics['kpis']['total_users']}")
    print(f"   Conversion Rate: {metrics['kpis']['conversion_rate_pct']}%")
    print(f"   WhatsApp Opt-in Subscribers: {metrics['kpis']['whatsapp_subscribers']}")
    print(f"   Ephemeris Mode: {metrics['system_health']['ephemeris_mode']}")
    assert metrics["status"] == "healthy"
    assert "kpis" in metrics
    assert "identity_breakdown" in metrics
    assert "system_health" in metrics

    # 2. Test User Directory Endpoint
    users = get_admin_users(limit=10, offset=0, db=db)
    print(f"2. User Directory: Total={users['total']}, Retrieved={len(users['users'])}")
    assert users["total"] >= 0
    assert isinstance(users["users"], list)

    # 3. Test Ghost Sessions Monitoring Endpoint
    ghosts = get_admin_ghost_sessions(limit=10, claimed_only=None, db=db)
    print(f"3. Ghost Sessions: Total={ghosts['total']}, Retrieved={len(ghosts['sessions'])}")
    assert ghosts["total"] >= 0
    assert isinstance(ghosts["sessions"], list)

    # 4. Test Activity Logs
    logs = get_admin_activity_logs(limit=10, db=db)
    print(f"4. User Activity Audit Trail: Total Retrieved={logs['total']}")
    assert isinstance(logs["activities"], list)

    # 5. Test Simulated WhatsApp Briefing Trigger
    wa_res = trigger_whatsapp_briefings(dry_run=True)
    print(f"5. Trigger WhatsApp Transit Pipeline: {wa_res['status']} | {wa_res['message']}")
    assert wa_res["status"] == "success"

    # 6. Test Cache Flush
    cache_res = admin_flush_cache()
    print(f"6. Ephemeris Cache Flush: {cache_res['status']} | {cache_res['message']}")
    assert cache_res["status"] == "success"

    print("\n========================================================")
    print("    ALL 6 ADMIN OBSERVATORY TESTS PASSED 100%           ")
    print("========================================================\n")

    db.close()


if __name__ == "__main__":
    run_tests()

