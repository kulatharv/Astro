"""
Admin Observatory & Monitoring API Router.
Provides real-time system health, identity funnel analytics, ghost session metrics,
cache observability, and automated operational triggers for AstroLogic administrators.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from shared.db.session import get_db
from shared.cache.metrics import cache_metrics
from shared.cache.redis_client import CacheService
from shared.ephemeris.wrapper import get_ephemeris_diagnostics
from modules.auth.models import User, UserProfile, GuestSession, UserActivity
from modules.kundali.models import UserSavedChart

logger = logging.getLogger("admin.api")

admin_monitoring_router = APIRouter(prefix="/api/admin", tags=["Admin Observatory"])


@admin_monitoring_router.get("/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    """
    Returns aggregated observatory metrics:
    - Identity & Conversion Funnel KPIs
    - Ghost Session Recovery Rate
    - WhatsApp Subscriber Reach
    - Ephemeris & Cache Vitality
    - Monetization & Commercial Run-rate
    """
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)

    # 1. User & Identity Counts
    total_users = db.query(func.count(User.id)).scalar() or 0
    new_users_24h = db.query(func.count(User.id)).filter(User.created_at >= last_24h).scalar() or 0

    google_users = db.query(func.count(User.id)).filter(User.auth_provider == "google").scalar() or 0
    whatsapp_users = db.query(func.count(User.id)).filter(User.auth_provider == "whatsapp").scalar() or 0
    email_users = db.query(func.count(User.id)).filter((User.auth_provider == "email") | (User.auth_provider == None)).scalar() or 0

    # 2. WhatsApp Opt-in Reach
    whatsapp_subscribers = (
        db.query(func.count(UserProfile.id))
        .filter(UserProfile.whatsapp_opt_in == True, UserProfile.whatsapp_number != None)
        .scalar()
        or 0
    )

    # 3. Guest Sessions & Conversion Funnel KPIs
    total_guest_sessions = db.query(func.count(GuestSession.id)).scalar() or 0
    claimed_guest_sessions = db.query(func.count(GuestSession.id)).filter(GuestSession.is_claimed == True).scalar() or 0
    active_unclaimed_ghosts = (
        db.query(func.count(GuestSession.id))
        .filter(GuestSession.is_claimed == False, GuestSession.expires_at > now)
        .scalar()
        or 0
    )

    # Conversion Rate calculation:
    # Denominator: Total distinct visitor interactions (Guest Sessions + Direct Signups)
    total_interactions = max(total_guest_sessions + email_users, 1)
    total_converted = claimed_guest_sessions + google_users + whatsapp_users + email_users
    conversion_rate_pct = min(round((total_converted / total_interactions) * 100.0, 1), 100.0)

    # Ghost Session Recovery Rate (% of guest sessions that converted into claimed charts)
    ghost_recovery_rate_pct = (
        round((claimed_guest_sessions / max(total_guest_sessions, 1)) * 100.0, 1)
        if total_guest_sessions > 0
        else 0.0
    )

    # 4. Total Charts in Vault
    total_saved_charts = db.query(func.count(UserSavedChart.id)).scalar() or 0

    # 5. System & Ephemeris Vitality
    ephe_diag = get_ephemeris_diagnostics()
    cache_stats = cache_metrics.get_stats()

    # 6. Commercial & Revenue Estimates
    est_domestic_inr = (google_users + whatsapp_users) * 499.0
    est_global_usd = max(int(total_users * 0.15), 1) * 19.99

    return {
        "status": "healthy",
        "timestamp": now.isoformat(),
        "kpis": {
            "total_users": total_users,
            "new_users_24h": new_users_24h,
            "conversion_rate_pct": conversion_rate_pct,
            "ghost_recovery_rate_pct": ghost_recovery_rate_pct,
            "total_guest_sessions": total_guest_sessions,
            "claimed_guest_sessions": claimed_guest_sessions,
            "active_unclaimed_ghosts": active_unclaimed_ghosts,
            "whatsapp_subscribers": whatsapp_subscribers,
            "total_saved_charts": total_saved_charts,
        },
        "identity_breakdown": {
            "google_fedcm": google_users,
            "whatsapp_otp": whatsapp_users,
            "email_password": email_users,
        },
        "monetization_overview": {
            "domestic_inr_pipeline": est_domestic_inr,
            "global_usd_pipeline": est_global_usd,
            "currency_distribution": {"INR_pct": 82.5, "USD_pct": 17.5},
        },
        "system_health": {
            "ephemeris_mode": ephe_diag.get("runtime_mode", "moshier"),
            "ephemeris_accuracy": ephe_diag.get("accuracy_tier", "standard"),
            "cache_hits": cache_stats.get("hits", 0),
            "cache_misses": cache_stats.get("misses", 0),
            "cache_hit_ratio_pct": cache_stats.get("hit_ratio_pct", 0.0),
        },
    }


@admin_monitoring_router.get("/users")
def get_admin_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Returns paginated user list with profiles, vault chart counts, and activity status."""
    users = (
        db.query(User)
        .order_by(desc(User.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for u in users:
        charts_count = len(u.saved_charts) if u.saved_charts else 0
        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "auth_provider": u.auth_provider or "email",
            "preferred_language": u.preferred_language or "en",
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "birth_city": u.profile.birth_city if u.profile else None,
            "birth_date": u.profile.birth_date if u.profile else None,
            "whatsapp_opt_in": u.profile.whatsapp_opt_in if u.profile else False,
            "whatsapp_number": u.profile.whatsapp_number if u.profile else None,
            "saved_charts_count": charts_count,
        })

    total_count = db.query(func.count(User.id)).scalar() or 0
    return {"total": total_count, "limit": limit, "offset": offset, "users": results}


@admin_monitoring_router.get("/ghost-sessions")
def get_admin_ghost_sessions(
    limit: int = Query(50, ge=1, le=200),
    claimed_only: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """Returns recent guest sessions for zero-cookie abandonment monitoring."""
    query = db.query(GuestSession).order_by(desc(GuestSession.created_at))
    if claimed_only is not None:
        query = query.filter(GuestSession.is_claimed == claimed_only)

    sessions = query.limit(limit).all()

    results = []
    for s in sessions:
        results.append({
            "id": s.id,
            "device_fingerprint": s.device_fingerprint,
            "session_token": s.session_token,
            "chart_type": s.chart_type,
            "person_name": s.person_name,
            "birth_date": s.birth_date,
            "birth_time": s.birth_time,
            "birth_place": s.birth_place,
            "is_claimed": s.is_claimed,
            "claimed_by_user_id": s.claimed_by_user_id,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
        })

    total_count = db.query(func.count(GuestSession.id)).scalar() or 0
    return {"total": total_count, "sessions": results}


@admin_monitoring_router.get("/activity-logs")
def get_admin_activity_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Returns recent user activity audit trail."""
    activities = (
        db.query(UserActivity)
        .order_by(desc(UserActivity.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for a in activities:
        results.append({
            "id": a.id,
            "user_id": a.user_id,
            "action": a.action,
            "details": a.details,
            "ip_address": a.ip_address,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })

    return {"total": len(results), "activities": results}


@admin_monitoring_router.post("/trigger-whatsapp")
def trigger_whatsapp_briefings(dry_run: bool = Query(True)):
    """Allows administrators to manually run or test the daily WhatsApp transit worker."""
    from scripts.daily_whatsapp_transit_worker import run_daily_briefings
    try:
        run_daily_briefings(dry_run=dry_run)
        mode_str = "Simulated (Dry-Run)" if dry_run else "Live Broadcast"
        return {
            "status": "success",
            "message": f"WhatsApp transit briefings executed in {mode_str} mode.",
            "dry_run": dry_run,
        }
    except Exception as e:
        logger.error(f"Failed to trigger WhatsApp transit worker: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@admin_monitoring_router.post("/flush-cache")
def admin_flush_cache():
    """Flushes in-memory and Redis chart caches and resets metrics."""
    CacheService.clear()
    cache_metrics.reset()
    return {"status": "success", "message": "Ephemeris chart cache flushed successfully."}

