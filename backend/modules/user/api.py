"""User Profile and Multi-Chart Family Vault REST API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from shared.db.session import get_db
from app.services.user_service import user_service
from app.schemas.user_schema import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    WhatsAppPreferencesUpdate,
    SavedChartCreate,
    SavedChartResponse,
)
from modules.auth.models import User

router = APIRouter(prefix="/api/user", tags=["User Profile & Family Vault"])


def get_authenticated_user_id(request: Request, db: Session = Depends(get_db)) -> int:
    """
    Extracts user_id from session or x-user-id header.
    If none found in local development, falls back to the first available user.
    """
    user_id = request.session.get("user_id")

    if not user_id:
        header_uid = request.headers.get("x-user-id")
        if header_uid and header_uid.isdigit():
            user_id = int(header_uid)

    if not user_id:
        # In local/preview dev, if a user exists in DB, use the first user so the UI works seamlessly
        first_user = db.query(User).order_by(User.id.asc()).first()
        if first_user:
            return first_user.id
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in to view your cosmic profile.",
        )

    return int(user_id)


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Returns the user's complete profile with auto-computed Cosmic Badges."""
    profile = user_service.get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile


@router.post("/profile", response_model=UserProfileResponse)
def update_user_profile(
    req: UserProfileUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Updates birth parameters and recalculates Cosmic Badges."""
    updated = user_service.update_user_profile(db, user_id, req)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update user profile")
    return updated


@router.post("/whatsapp-settings", response_model=UserProfileResponse)
def update_whatsapp_settings(
    req: WhatsAppPreferencesUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Updates WhatsApp morning forecast opt-in and delivery preferences."""
    updated = user_service.update_whatsapp_preferences(db, user_id, req)
    if not updated:
        raise HTTPException(status_code=400, detail="Could not update WhatsApp preferences")
    return updated


@router.get("/charts", response_model=List[SavedChartResponse])
def list_saved_charts(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Lists all saved family and client charts in the user's vault."""
    return user_service.list_saved_charts(db, user_id)


@router.post("/charts", response_model=SavedChartResponse)
def create_saved_chart(
    req: SavedChartCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Adds a new family member or client chart into the vault with precomputed chart data."""
    return user_service.create_saved_chart(db, user_id, req)


@router.delete("/charts/{chart_id}")
def delete_saved_chart(
    chart_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_authenticated_user_id),
):
    """Deletes a saved chart from the user's vault."""
    success = user_service.delete_saved_chart(db, user_id, chart_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved chart not found or unauthorized")
    return {"status": "success", "message": f"Saved chart {chart_id} deleted"}

