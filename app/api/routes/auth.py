"""Authentication and user session routes."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.activity import UserActivity
from app.models.user import UserProfile
from app.schemas.auth import UserLogin, UserRegister
from app.schemas.user import UserProfileUpdate
from app.core.templating import render_template
from app.services.auth_service import auth_service
from app.services.feedback_service import feedback_service
from app.services.translation_service import load_translations
from app.services.user_service import user_service

router = APIRouter(tags=["Authentication"])


def _render_auth_page(request: Request, mode: str = "login", error: str | None = None, title: str = "User Login"):
    templates = request.app.state.templates
    lang = request.cookies.get("lang", "en")
    return render_template(
        templates,
        request,
        "auth.html",
        {
            "request": request,
            "mode": mode,
            "title": title,
            "button": "Create Account" if mode == "signup" else "Login",
            "error": error,
            "lang": lang,
            "t": load_translations(lang),
        },
    )


@router.get("/change-language/{lang}")
def change_language(lang: str):
    """Switch language preference and store in cookie."""
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=31536000)
    return response


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return _render_auth_page(request, mode="signup", title="Create Account")


@router.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    data = UserRegister(name=name, email=email, phone=phone, password=password)
    user, err = auth_service.register_user(db, data)

    if err:
        return _render_auth_page(request, mode="signup", error=err, title="Create Account")

    request.session["user_id"] = user.id
    feedback_service.log_activity(
        db,
        action="signup",
        user_id=user.id,
        details="User created account",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse("/profile", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return _render_auth_page(request, mode="login", title="User Login")


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    data = UserLogin(email=email, password=password)
    user = auth_service.authenticate_user(db, data)

    if not user:
        return _render_auth_page(
            request,
            mode="login",
            error="Invalid email or password",
            title="User Login",
        )

    request.session["user_id"] = user.id
    feedback_service.log_activity(
        db,
        action="login",
        user_id=user.id,
        details="User logged in",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    response = RedirectResponse("/", status_code=303)
    if user.preferred_language:
        response.set_cookie(key="lang", value=user.preferred_language, max_age=31536000)
    return response


@router.get("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id:
        feedback_service.log_activity(
            db,
            action="logout",
            user_id=user_id,
            details="User logged out",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == user.id)
        .order_by(UserActivity.created_at.desc())
        .limit(10)
        .all()
    )

    templates = request.app.state.templates
    lang = request.cookies.get("lang", "en")
    return render_template(
        templates,
        request,
        "profile.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "activities": activities,
            "lang": lang,
            "t": load_translations(lang),
        },
    )


@router.post("/profile")
def update_profile(
    request: Request,
    name: str = Form(...),
    phone: str = Form(""),
    birth_date: str = Form(""),
    birth_time: str = Form(""),
    birth_city: str = Form(""),
    zodiac_sign: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    data = UserProfileUpdate(
        name=name,
        phone=phone,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_city=birth_city,
        zodiac_sign=zodiac_sign,
        notes=notes,
    )
    user_service.update_profile(db, user.id, data)

    feedback_service.log_activity(
        db,
        action="profile_update",
        user_id=user.id,
        details="User updated profile",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse("/", status_code=303)
