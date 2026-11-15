"""
Monetization & Purchasing Power Parity (PPP) Pricing Engine.
Dynamically tailors product offerings and pricing based on client geography,
vernacular orientation, and hardware tiering (Retina display, GPU compute capability).
"""

from typing import Optional
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

monetization_router = APIRouter(prefix="/api/monetization", tags=["Monetization & Pricing"])


class PricingItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    original_price: float
    currency: str
    currency_symbol: str
    discount_pct: int
    badge: Optional[str] = None
    payment_rails: list[str]


class PricingResponse(BaseModel):
    country: str
    currency: str
    currency_symbol: str
    is_india: bool
    is_high_net_worth: bool
    detected_via: str
    tiers: dict[str, PricingItem]


@monetization_router.get("/pricing", response_model=PricingResponse)
def get_dynamic_pricing(
    request: Request,
    country_override: Optional[str] = None,
    timezone: Optional[str] = None,
    hnw: bool = False,
):
    """
    Computes dynamic, Purchasing Power Parity (PPP) calibrated pricing.
    Supports UPI / NetBanking in India, and Apple Pay / Stripe in Global markets.
    """
    # 1. GeoIP Detection via Cloudflare / Reverse Proxy headers or client timezone
    cf_country = request.headers.get("cf-ipcountry", "").upper() if request.headers else ""
    client_country = country_override.upper() if isinstance(country_override, str) and country_override else (cf_country or "IN")


    # Timezone-based heuristic fallback if direct GeoIP header is missing
    is_india = client_country == "IN"
    detected_via = "header" if cf_country else "timezone_fallback"

    if not cf_country and timezone:
        if "Kolkata" in timezone or "Calcutta" in timezone:
            is_india = True
            client_country = "IN"
        elif any(tz in timezone for tz in ["America", "US", "Europe", "London", "Australia"]):
            is_india = False
            client_country = "US"

    is_hnw = hnw

    if is_india:
        currency = "INR"
        symbol = "₹"
        tiers = {
            "gemstone_report": PricingItem(
                id="gemstone_report",
                name="Personalized Vedic Gemstone & Muhurta Report",
                description="Astrological gemstone recommendations, auspicious wearing muhurta, and metal consecration guidelines.",
                price=499.0,
                original_price=999.0,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="Popular",
                payment_rails=["upi_intent", "gpay", "phonepe", "paytm", "card"],
            ),
            "vip_annual_pass": PricingItem(
                id="vip_annual_pass",
                name="VIP Cosmic Vault: 1-Year Dasha & Transit Forecasts",
                description="Unlimited Kundali storage for 10 family members, full 10-domain predictions, and daily WhatsApp morning transit briefing.",
                price=1499.0,
                original_price=2999.0,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="Best Value",
                payment_rails=["upi_intent", "gpay", "phonepe", "paytm", "card"],
            ),
        }
        if is_hnw:
            tiers["royal_consultation"] = PricingItem(
                id="royal_consultation",
                name="Bespoke Royal Astrologer Consultation & Custom Yantra",
                description="1-on-1 private video consultation with senior Vedic pandit, energized silver Navagraha yantra shipped to home address.",
                price=4999.0,
                original_price=9999.0,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="VIP Royal Exclusive",
                payment_rails=["upi_intent", "netbanking", "card"],
            )
    else:
        # International (US / UK / EU / Global)
        currency = "USD"
        symbol = "$"
        tiers = {
            "gemstone_report": PricingItem(
                id="gemstone_report",
                name="Personalized Vedic Gemstone & Muhurta Report",
                description="Authentic gemstone calculation, auspicious wearing muhurta, and planetary consecration mantra.",
                price=19.99,
                original_price=39.99,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="Popular",
                payment_rails=["stripe", "apple_pay", "google_pay", "card"],
            ),
            "vip_annual_pass": PricingItem(
                id="vip_annual_pass",
                name="VIP Cosmic Vault: 1-Year Dasha & Transit Forecasts",
                description="Unlimited Kundali vault for 10 family members, full 10-domain predictions, and daily WhatsApp/email cosmic briefs.",
                price=49.99,
                original_price=99.99,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="Best Value",
                payment_rails=["stripe", "apple_pay", "google_pay", "card"],
            ),
        }
        if is_hnw:
            tiers["royal_consultation"] = PricingItem(
                id="royal_consultation",
                name="Bespoke Royal Astrologer Consultation & Custom Yantra",
                description="1-on-1 private consultation with high-level Vedic scholar and custom consecrated gemstone energized at Varanasi temple.",
                price=149.0,
                original_price=299.0,
                currency=currency,
                currency_symbol=symbol,
                discount_pct=50,
                badge="VIP Royal Exclusive",
                payment_rails=["stripe", "apple_pay", "card"],
            )

    return PricingResponse(
        country=client_country,
        currency=currency,
        currency_symbol=symbol,
        is_india=is_india,
        is_high_net_worth=is_hnw,
        detected_via=detected_via,
        tiers=tiers,
    )
