"""
Integration Test Suite for Telemetry, Ghost Session Recovery, and PPP Dynamic Monetization.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from shared.db.session import SessionLocal
from modules.auth.models import User, UserProfile, GuestSession
from app.services.auth_service import auth_service
from app.schemas.auth_schema import GuestSessionCreateRequest, ClaimGuestChartRequest
from modules.monetization.api import get_dynamic_pricing
from fastapi import Request


def run_tests():
    db = SessionLocal()
    print("\n========================================================")
    print("  RUNNING TELEMETRY, GHOST SESSION & PPP PRICING TESTS  ")
    print("========================================================")

    # 1. Test Guest Session Creation
    test_fp = "df_test_8a7b6c5d4e3f2a1b"
    req = GuestSessionCreateRequest(
        device_fingerprint=test_fp,
        chart_type="kundali",
        person_name="Vikramaditya Rao",
        birth_date="1992-04-14",
        birth_time="10:30",
        birth_place="Ujjain",
        latitude=23.1765,
        longitude=75.7885,
        timezone_offset=5.5,
        chart_payload={"lagna": "Mesha", "moon_sign": "Simha", "planets": ["Surya", "Chandra"]},
        telemetry={"screen": "1920x1080", "tz": "Asia/Kolkata"},
    )

    save_res = auth_service.save_guest_session(db, req)
    print(f"1. Save Guest Session: {save_res['status']} | Token: {save_res['session_token']}")
    assert save_res["status"] in ("created", "updated")

    # 2. Test Ghost Session Retrieval (Zero-Cookie Recovery)
    ghost_data = auth_service.get_ghost_session_by_fingerprint(db, test_fp)
    print(f"2. Ghost Session Retrieved: has_active_session={ghost_data['has_active_session']}, Name={ghost_data['person_name']}")
    assert ghost_data["has_active_session"] is True
    assert ghost_data["person_name"] == "Vikramaditya Rao"
    assert ghost_data["chart_payload"]["lagna"] == "Mesha"

    # 3. Test Claiming Guest Session into Permanent Vault
    # Create temporary user with unique email
    import secrets
    unique_suffix = secrets.token_hex(6)
    temp_user = User(
        name="Vikramaditya",
        email=f"vikram_{unique_suffix}@example.com",
        password_hash="FEDERATED_GOOGLE_test_hash",
        auth_provider="google",
        provider_user_id=f"google_test_{unique_suffix}",
    )
    temp_profile = UserProfile(user=temp_user)
    db.add(temp_user)
    db.add(temp_profile)
    db.commit()
    db.refresh(temp_user)

    claim_req = ClaimGuestChartRequest(
        profile_name="Vikramaditya Rao",
        relationship="self",
        birth_date="1992-04-14",
        birth_time="10:30",
        birth_city="Ujjain",
        latitude=23.1765,
        longitude=75.7885,
        timezone_offset=5.5,
        tz_name="Asia/Kolkata",
    )
    claim_res = auth_service.claim_guest_chart(db, temp_user.id, claim_req)
    print(f"3. Claim Guest Chart: {claim_res['status']} | Chart ID: {claim_res['chart_id']}")
    assert claim_res["status"] == "success"

    # Verify ghost session is marked is_claimed = True
    recovered = auth_service.get_ghost_session_by_fingerprint(db, test_fp)
    print(f"   Ghost session after claim: has_active_session={recovered['has_active_session']} (Should be False)")
    assert recovered["has_active_session"] is False

    # 4. Test PPP Pricing Engine
    # Mock FastAPI request
    class MockRequest:
        def __init__(self, headers=None):
            self.headers = headers or {}

    # India Request
    in_req = MockRequest(headers={"cf-ipcountry": "IN"})
    in_pricing = get_dynamic_pricing(in_req, timezone="Asia/Kolkata", hnw=False)
    print(f"4. India Pricing: Currency={in_pricing.currency} {in_pricing.currency_symbol} | Gemstone: {in_pricing.tiers['gemstone_report'].price} | VIP Pass: {in_pricing.tiers['vip_annual_pass'].price}")
    assert in_pricing.currency == "INR"
    assert in_pricing.tiers["gemstone_report"].price == 499.0
    assert in_pricing.tiers["vip_annual_pass"].price == 1499.0
    assert "upi_intent" in in_pricing.tiers["gemstone_report"].payment_rails

    # US Request
    us_req = MockRequest(headers={"cf-ipcountry": "US"})
    us_pricing = get_dynamic_pricing(us_req, timezone="America/New_York", hnw=False)
    print(f"5. US/Global Pricing: Currency={us_pricing.currency} {us_pricing.currency_symbol} | Gemstone: {us_pricing.tiers['gemstone_report'].price} | VIP Pass: {us_pricing.tiers['vip_annual_pass'].price}")
    assert us_pricing.currency == "USD"
    assert us_pricing.tiers["gemstone_report"].price == 19.99
    assert us_pricing.tiers["vip_annual_pass"].price == 49.99
    assert "stripe" in us_pricing.tiers["gemstone_report"].payment_rails

    # High-Net-Worth Hardware Tier
    hnw_req = MockRequest(headers={"cf-ipcountry": "IN"})
    hnw_pricing = get_dynamic_pricing(hnw_req, timezone="Asia/Kolkata", hnw=True)
    print(f"6. HNW Device Tier: Available Tiers={list(hnw_pricing.tiers.keys())}")
    assert "royal_consultation" in hnw_pricing.tiers
    assert hnw_pricing.tiers["royal_consultation"].price == 4999.0

    print("\n========================================================")
    print("  ALL 6 TELEMETRY, GHOST SESSION & PPP TESTS PASSED 100% ")
    print("========================================================\n")

    # Cleanup test records
    db.delete(temp_user)
    db.commit()
    db.close()


if __name__ == "__main__":
    run_tests()
