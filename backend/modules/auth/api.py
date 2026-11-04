"""Auth module API routers & AuthService public interface."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta

from shared.db.session import get_db
from shared.config.settings import settings
from shared.i18n.translation import load_translations

from modules.auth.engine import auth_engine
from modules.auth.models import User, UserProfile, AdminUser, UserActivity
from modules.auth.schemas import UserLogin, UserRegister, UserProfileUpdate

auth_router = APIRouter(tags=["Authentication"])
router = auth_router
admin_router = APIRouter(tags=["Admin"])



class AuthService:
    def register_user(self, db: Session, data: UserRegister) -> tuple[User | None, str | None]:
        return auth_engine.register_user(db, data)

    def authenticate_user(self, db: Session, data: UserLogin) -> User | None:
        return auth_engine.authenticate_user(db, data)

    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        return auth_engine.get_user_by_id(db, user_id)

    def update_profile(self, db: Session, user_id: int, data: UserProfileUpdate) -> UserProfile | None:
        return auth_engine.update_profile(db, user_id, data)

    def get_user_profile(self, db: Session, user_id: int) -> UserProfile | None:
        return auth_engine.get_user_profile(db, user_id)


def _render_auth_page(request: Request, mode: str = "login", error: str | None = None, title: str = "User Login"):
    templates = request.app.state.templates
    lang = request.cookies.get("lang", "en")
    return templates.TemplateResponse(
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


@auth_router.get("/change-language/{lang}")
def change_language(lang: str):
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=31536000)
    return response


@auth_router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return _render_auth_page(request, mode="signup", title="Create Account")


@auth_router.post("/signup")
def signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    data = UserRegister(name=name, email=email, phone=phone, password=password)
    user, err = auth_engine.register_user(db, data)

    if err:
        return _render_auth_page(request, mode="signup", error=err, title="Create Account")

    request.session["user_id"] = user.id
    auth_engine.log_activity(
        db,
        action="signup",
        user_id=user.id,
        details="User created account",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse("/profile", status_code=303)


@auth_router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return _render_auth_page(request, mode="login", title="User Login")


@auth_router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    data = UserLogin(email=email, password=password)
    user = auth_engine.authenticate_user(db, data)

    if not user:
        return _render_auth_page(
            request,
            mode="login",
            error="Invalid email or password",
            title="User Login",
        )

    request.session["user_id"] = user.id
    auth_engine.log_activity(
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


@auth_router.get("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id:
        auth_engine.log_activity(
            db,
            action="logout",
            user_id=user_id,
            details="User logged out",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@auth_router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    user = auth_engine.get_user_by_id(db, user_id)
    if not user:
        return RedirectResponse("/login", status_code=303)

    profile = auth_engine.get_user_profile(db, user.id)
    activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == user.id)
        .order_by(UserActivity.created_at.desc())
        .limit(10)
        .all()
    )

    templates = request.app.state.templates
    lang = request.cookies.get("lang", "en")
    return templates.TemplateResponse(
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


@auth_router.post("/profile")
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
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    user = auth_engine.get_user_by_id(db, user_id)
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
    auth_engine.update_profile(db, user.id, data)

    auth_engine.log_activity(
        db,
        action="profile_update",
        user_id=user.id,
        details="User updated profile",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse("/", status_code=303)


@admin_router.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin and auth_engine.verify_password(password, admin.password_hash):
        request.session["admin"] = "true"
        return RedirectResponse("/admin/blogs", status_code=303)
    templates = request.app.state.templates
    return templates.TemplateResponse("admin-login.html", {"request": request, "error": "Invalid administrator credentials"}, status_code=200)


@auth_router.post("/api/auth/signup", status_code=201)
def api_signup(request: Request, data: UserRegister, db: Session = Depends(get_db)):
    """JSON API endpoint for user registration."""
    user, err = auth_engine.register_user(db, data)
    if err:
        raise HTTPException(status_code=400, detail=err)
    request.session["user_id"] = user.id
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": user.name}}


@auth_router.post("/api/auth/login")
def api_login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """JSON API endpoint for user login."""
    user = auth_engine.authenticate_user(db, data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    request.session["user_id"] = user.id
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": user.name}}


@auth_router.post("/api/auth/logout")
def api_logout(request: Request):
    """JSON API endpoint for user logout."""
    request.session.clear()
    return {"status": "ok", "message": "Logged out successfully"}


