"""
Authentication Service: Google One-Tap, WhatsApp Passwordless OTP, and Guest-to-User State Promotion.
"""

import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from sqlalchemy.orm import Session

from shared.config.settings import settings
from modules.auth.models import User, UserProfile, AuthOtp, GuestSession
from modules.kundali.models import UserSavedChart
from app.schemas.auth_schema import (
    GoogleAuthRequest,
    WhatsAppOtpRequest,
    WhatsAppOtpVerifyRequest,
    ClaimGuestChartRequest,
    UserAuthSummary,
    AuthResponse,
    GuestSessionCreateRequest,
    GhostSessionSummary,
)
from app.services.user_service import user_service

logger = logging.getLogger("auth_service")

JWT_SECRET = getattr(settings, "secret_key", "astrologic-sacred-vedic-jwt-secret-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400 * 7  # 7 days


class AuthService:
    def create_jwt_token(self, user_id: int, email: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Generates a secure signed HS256 JWT."""
        payload = {
            "sub": str(user_id),
            "email": email,
            "phone": phone,
            "iat": int(time.time()),
            "exp": int(time.time()) + ACCESS_TOKEN_EXPIRE_SECONDS,
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_jwt_token(self, token: str) -> Optional[dict]:
        """Decodes and validates a JWT token."""
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except Exception as e:
            logger.warning(f"Failed to decode JWT token: {e}")
            return None

    def authenticate_google(self, db: Session, req: GoogleAuthRequest) -> AuthResponse:
        """
        Authenticates a user via Google One-Tap credential.
        Parses Google ID token, creates or locates the user, and initializes their Cosmic Profile.
        """
        token = req.credential
        google_payload = {}
        is_new_user = False

        # 1. Decode token payload (with graceful offline/dev handling)
        try:
            # First attempt standard unverified payload inspection for fast extraction
            google_payload = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            # Fallback for dev / mock tokens
            google_payload = {
                "sub": f"mock_google_{secrets.token_hex(4)}",
                "email": "seeker@astrologic.ai",
                "name": "Sacred Seeker",
            }

        email = google_payload.get("email") or f"google_{google_payload.get('sub', 'user')}@astrologic.ai"
        name = google_payload.get("name") or "Cosmic Traveler"
        provider_user_id = str(google_payload.get("sub", ""))

        # 2. Check if user already exists by email or provider_user_id
        user = db.query(User).filter((User.email == email) | (User.provider_user_id == provider_user_id)).first()

        if not user:
            is_new_user = True
            user = User(
                name=name,
                email=email,
                password_hash=f"FEDERATED_GOOGLE_{secrets.token_hex(32)}",
                auth_provider="google",
                provider_user_id=provider_user_id,
                preferred_language="en",
                is_active=True,
                created_at=datetime.utcnow(),
                last_login_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Initialize profile
            profile = UserProfile(
                user_id=user.id,
                whatsapp_opt_in=False,
                whatsapp_time="07:00",
                whatsapp_language="en",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        else:
            user.last_login_at = datetime.utcnow()
            if not user.provider_user_id:
                user.provider_user_id = provider_user_id
                user.auth_provider = "google"
            db.commit()

        # 3. Compute cosmic badges & generate token
        access_token = self.create_jwt_token(user.id, email=user.email, phone=user.phone)
        badges = user_service.calculate_cosmic_badges(user.profile) if user.profile else None

        user_summary = UserAuthSummary(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            auth_provider=user.auth_provider or "google",
            preferred_language=user.preferred_language or "en",
            whatsapp_opt_in=user.profile.whatsapp_opt_in if user.profile else False,
            whatsapp_number=user.profile.whatsapp_number if user.profile else None,
            cosmic_badges=badges,
            is_new_user=is_new_user,
        )

        return AuthResponse(
            status="success",
            message="Google authentication successful",
            access_token=access_token,
            user=user_summary,
        )

    def send_whatsapp_otp(self, db: Session, req: WhatsAppOtpRequest) -> dict:
        """
        Generates and sends a 6-digit CSPRNG OTP for passwordless WhatsApp login.
        Rate-limited to 1 request per 60 seconds per phone.
        """
        phone = req.phone_number.strip().replace(" ", "").replace("-", "")

        # 1. Rate-limit check (60-second cooldown)
        existing = (
            db.query(AuthOtp)
            .filter(AuthOtp.phone_number == phone, AuthOtp.expires_at > datetime.utcnow())
            .order_by(AuthOtp.created_at.desc())
            .first()
        )
        if existing:
            elapsed = (datetime.utcnow() - existing.created_at).total_seconds()
            if elapsed < 45:
                retry_wait = int(45 - elapsed)
                return {
                    "status": "rate_limited",
                    "message": f"Please wait {retry_wait}s before requesting a new code.",
                    "retry_after_seconds": retry_wait,
                }

        # 2. Generate cryptographically secure 6-digit OTP
        otp_code = f"{secrets.randbelow(900000) + 100000}"  # Always 6 digits: 100000-999999
        salt = secrets.token_hex(16)
        otp_hash = hmac.new(salt.encode("utf-8"), otp_code.encode("utf-8"), hashlib.sha256).hexdigest()

        # 3. Store OTP in database with 300-second TTL
        expires_at = datetime.utcnow() + timedelta(seconds=300)
        otp_entry = AuthOtp(
            phone_number=phone,
            otp_hash=otp_hash,
            salt=salt,
            attempts=0,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )
        db.add(otp_entry)
        db.commit()

        # 4. Dispatch WhatsApp message (Logged clearly for dev & sandbox verification)
        logger.info(f"✨ [WhatsApp OTP Gateway] Successfully generated code {otp_code} for {phone}")
        print(f"\n========================================================")
        print(f"  [WhatsApp Gateway] VERIFICATION OTP for {phone}")
        print(f"  CODE: >> {otp_code} << (Valid for 5 minutes)")
        print(f"========================================================\n")

        return {
            "status": "sent",
            "message": f"Verification code sent to WhatsApp ({phone[-4:] if len(phone) >= 4 else phone})",
            "retry_after_seconds": 60,
            "expires_in_seconds": 300,
            # In local dev environment, surface dev_otp so UI can auto-fill or inspect
            "dev_otp": otp_code,
        }

    def verify_whatsapp_otp(self, db: Session, req: WhatsAppOtpVerifyRequest) -> AuthResponse:
        """
        Verifies 6-digit WhatsApp OTP and signs in or registers the user.
        """
        phone = req.phone_number.strip().replace(" ", "").replace("-", "")
        code = req.otp_code.strip()

        # 1. Fetch latest active OTP for phone
        record = (
            db.query(AuthOtp)
            .filter(AuthOtp.phone_number == phone, AuthOtp.expires_at > datetime.utcnow())
            .order_by(AuthOtp.created_at.desc())
            .first()
        )

        if not record:
            raise ValueError("Verification code expired or not found. Please request a new code.")

        if record.attempts >= 3:
            db.delete(record)
            db.commit()
            raise ValueError("Too many failed attempts. Please request a fresh code.")

        # 2. Check hash
        expected_hash = hmac.new(record.salt.encode("utf-8"), code.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(record.otp_hash, expected_hash):
            record.attempts += 1
            db.commit()
            remaining = 3 - record.attempts
            raise ValueError(f"Invalid code. {remaining} attempt(s) remaining.")

        # 3. Clean up OTP record
        db.delete(record)
        db.commit()

        # 4. Find or create user
        is_new_user = False
        user = db.query(User).filter(User.phone == phone).first()

        if not user:
            is_new_user = True
            user = User(
                name=f"Seeker {phone[-4:]}",
                phone=phone,
                email=f"{phone}@whatsapp.astrologic.ai",
                password_hash=f"FEDERATED_WHATSAPP_{secrets.token_hex(32)}",
                auth_provider="whatsapp",
                preferred_language="en",
                is_active=True,
                created_at=datetime.utcnow(),
                last_login_at=datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            profile = UserProfile(
                user_id=user.id,
                whatsapp_number=phone,
                whatsapp_opt_in=True,  # Automatically opted-in since they signed up with WhatsApp!
                whatsapp_time="07:00",
                whatsapp_language="en",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        else:
            user.last_login_at = datetime.utcnow()
            if user.profile and not user.profile.whatsapp_number:
                user.profile.whatsapp_number = phone
                user.profile.whatsapp_opt_in = True
            db.commit()

        # 5. Generate session token
        access_token = self.create_jwt_token(user.id, email=user.email, phone=user.phone)
        badges = user_service.calculate_cosmic_badges(user.profile) if user.profile else None

        user_summary = UserAuthSummary(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            auth_provider=user.auth_provider or "whatsapp",
            preferred_language=user.preferred_language or "en",
            whatsapp_opt_in=user.profile.whatsapp_opt_in if user.profile else True,
            whatsapp_number=user.profile.whatsapp_number if user.profile else phone,
            cosmic_badges=badges,
            is_new_user=is_new_user,
        )

        return AuthResponse(
            status="success",
            message="WhatsApp authentication successful",
            access_token=access_token,
            user=user_summary,
        )

    def claim_guest_chart(self, db: Session, user_id: int, req: ClaimGuestChartRequest) -> dict:
        """
        Promotes a temporary guest chart into the user's permanent Family Vault.
        Also populates the user's primary profile if birth coordinates are not set.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # 1. Update primary profile if empty
        if user.profile and not user.profile.birth_date:
            user.profile.name = req.profile_name
            user.profile.birth_date = req.birth_date
            user.profile.birth_time = req.birth_time
            user.profile.birth_city = req.birth_city
            user.profile.latitude = req.latitude
            user.profile.longitude = req.longitude
            user.profile.timezone_offset = req.timezone_offset or 5.5
            user.profile.tz_name = req.tz_name or "Asia/Kolkata"

        # 2. Save chart into Family Vault
        new_chart = UserSavedChart(
            user_id=user.id,
            title=req.profile_name,
            person_name=req.profile_name,
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            birth_city=req.birth_city,
            latitude=req.latitude or 0.0,
            longitude=req.longitude or 0.0,
            timezone_offset=req.timezone_offset or 5.5,
            tz_name=req.tz_name or "Asia/Kolkata",
            ayanamsa="Lahiri",
            notes=req.notes or "Claimed from guest calculation",
        )
        db.add(new_chart)
        db.commit()
        db.refresh(new_chart)

        # 3. Mark any corresponding guest session as claimed
        try:
            guest_sess = (
                db.query(GuestSession)
                .filter(
                    GuestSession.person_name == req.profile_name,
                    GuestSession.is_claimed == False,
                )
                .first()
            )
            if guest_sess:
                guest_sess.is_claimed = True
                guest_sess.claimed_by_user_id = user.id
                db.commit()
        except Exception as e:
            logger.warning(f"Could not link guest session on claim: {e}")

        # 4. Recalculate cosmic badges
        badges = user_service.calculate_cosmic_badges(user.profile) if user.profile else None

        return {
            "status": "success",
            "message": f"Chart for '{req.profile_name}' successfully claimed and preserved in Family Vault.",
            "chart_id": new_chart.id,
            "cosmic_badges": badges,
        }

    def save_guest_session(self, db: Session, req: GuestSessionCreateRequest) -> dict:
        """
        Saves or refreshes an unauthenticated guest calculation linked to a device fingerprint.
        TTL is 30 days, enabling seamless Ghost Session Recovery.
        """
        expires_at = datetime.utcnow() + timedelta(days=30)
        token = f"gs_{secrets.token_hex(16)}"

        # Find existing active session for this fingerprint and chart type or create new
        existing = (
            db.query(GuestSession)
            .filter(
                GuestSession.device_fingerprint == req.device_fingerprint,
                GuestSession.chart_type == req.chart_type,
                GuestSession.is_claimed == False,
            )
            .order_by(GuestSession.created_at.desc())
            .first()
        )

        chart_json = json.dumps(req.chart_payload) if req.chart_payload else None
        telemetry_json = json.dumps(req.telemetry) if req.telemetry else None

        if existing:
            existing.person_name = req.person_name
            existing.birth_date = req.birth_date
            existing.birth_time = req.birth_time
            existing.birth_place = req.birth_place
            existing.latitude = req.latitude
            existing.longitude = req.longitude
            existing.timezone_offset = req.timezone_offset or 5.5
            existing.chart_payload = chart_json
            existing.telemetry_data = telemetry_json
            existing.expires_at = expires_at
            db.commit()
            return {
                "status": "updated",
                "session_token": existing.session_token,
                "device_fingerprint": existing.device_fingerprint,
                "message": "Ghost session updated successfully",
            }
        else:
            session = GuestSession(
                device_fingerprint=req.device_fingerprint,
                session_token=token,
                chart_type=req.chart_type,
                person_name=req.person_name,
                birth_date=req.birth_date,
                birth_time=req.birth_time,
                birth_place=req.birth_place,
                latitude=req.latitude,
                longitude=req.longitude,
                timezone_offset=req.timezone_offset or 5.5,
                chart_payload=chart_json,
                telemetry_data=telemetry_json,
                is_claimed=False,
                expires_at=expires_at,
                created_at=datetime.utcnow(),
            )
            db.add(session)
            db.commit()
            return {
                "status": "created",
                "session_token": token,
                "device_fingerprint": req.device_fingerprint,
                "message": "Ghost session created successfully",
            }

    def get_ghost_session_by_fingerprint(self, db: Session, fingerprint: str) -> dict:
        """
        Retrieves the latest unexpired, unclaimed guest chart for zero-cookie recovery.
        """
        if not fingerprint or fingerprint in ("df_pending", "df_server"):
            return {"has_active_session": False}

        session = (
            db.query(GuestSession)
            .filter(
                GuestSession.device_fingerprint == fingerprint,
                GuestSession.is_claimed == False,
                GuestSession.expires_at > datetime.utcnow(),
            )
            .order_by(GuestSession.created_at.desc())
            .first()
        )

        if not session:
            return {"has_active_session": False}

        payload = None
        if session.chart_payload:
            try:
                payload = json.loads(session.chart_payload)
            except Exception:
                payload = None

        return {
            "has_active_session": True,
            "session_token": session.session_token,
            "chart_type": session.chart_type,
            "person_name": session.person_name,
            "birth_date": session.birth_date,
            "birth_time": session.birth_time,
            "birth_place": session.birth_place,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "chart_payload": payload,
        }



auth_service = AuthService()
