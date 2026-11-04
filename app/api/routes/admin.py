"""Admin portal dashboard, blog management, user telemetry, and activity routes."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db, require_admin
from app.core.config import settings
from app.core.security import verify_password
from app.core.templating import render_template
from app.models.activity import UserActivity
from app.models.admin import AdminUser
from app.models.blog import Blog
from app.models.feedback import Feedback
from app.models.user import User, UserProfile
from app.schemas.blog import BlogCreate, BlogUpdate
from app.services.blog_service import blog_service
from app.services.translation_service import load_translations

router = APIRouter(tags=["Admin"])


def _render_admin(request: Request, template_name: str, context: dict | None = None):
    templates = request.app.state.templates
    lang = request.cookies.get("lang", "en")
    base_ctx = {
        "request": request,
        "lang": lang,
        "t": load_translations(lang),
    }
    if context:
        base_ctx.update(context)
    return render_template(templates, request, template_name, base_ctx)


# ── Admin Web Routes ───────────────────────────────────────────────

@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return RedirectResponse("/admin/blogs", status_code=303)


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return _render_admin(request, "admin-login.html")


@router.post("/admin/login")
def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = (
        db.query(AdminUser)
        .filter(AdminUser.username == username.strip(), AdminUser.is_active == True)
        .first()
    )
    if admin and verify_password(password, admin.password_hash):
        request.session["admin"] = "true"
        request.session["admin_id"] = admin.id
        return RedirectResponse("/admin/blogs", status_code=303)
    return _render_admin(request, "admin-login.html", {"error": "Invalid administrator credentials"})


@router.get("/admin/logout")
def admin_logout(request: Request):
    request.session.pop("admin", None)
    return RedirectResponse("/", status_code=303)


@router.get("/admin/blogs", response_class=HTMLResponse)
def admin_blogs_page(request: Request):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)
    return _render_admin(request, "admin-blog.html")


@router.get("/admin/activity", response_class=HTMLResponse)
def admin_activity_page(request: Request, db: Session = Depends(get_db)):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)

    activities = (
        db.query(UserActivity)
        .options(joinedload(UserActivity.user))
        .order_by(UserActivity.created_at.desc())
        .limit(100)
        .all()
    )
    since = datetime.utcnow() - timedelta(days=7)

    return _render_admin(
        request,
        "admin-activity.html",
        {
            "activities": activities,
            "total_users": db.query(User).count(),
            "total_activities": db.query(UserActivity).count(),
            "recent_signups": db.query(User).filter(User.created_at >= since).count(),
        },
    )


@router.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request, db: Session = Depends(get_db)):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)

    users = (
        db.query(User)
        .options(joinedload(User.profile))
        .order_by(User.created_at.desc())
        .all()
    )
    return _render_admin(
        request,
        "admin-users.html",
        {
            "users": users,
            "total_users": db.query(User).count(),
            "total_profiles": db.query(UserProfile).count(),
            "total_activities": db.query(UserActivity).count(),
        },
    )


@router.get("/admin/feedback", response_class=HTMLResponse)
def admin_feedback_page(request: Request, db: Session = Depends(get_db)):
    if request.session.get("admin") != "true":
        return RedirectResponse("/admin/login", status_code=303)

    items = (
        db.query(Feedback)
        .options(joinedload(Feedback.user))
        .order_by(Feedback.created_at.desc())
        .limit(200)
        .all()
    )
    return _render_admin(
        request,
        "admin-feedback.html",
        {
            "feedback_items": items,
            "total_feedback": db.query(Feedback).count(),
            "kundali_feedback": db.query(Feedback).filter(Feedback.module == "kundali").count(),
            "prediction_feedback": db.query(Feedback).filter(Feedback.module == "prediction").count(),
        },
    )


# ── Admin API Endpoints ────────────────────────────────────────────

@router.get("/api/admin/blogs")
def admin_get_all_blogs(request: Request, db: Session = Depends(get_db)):
    require_admin(request)
    return blog_service.get_all_blogs(db)


@router.post("/api/admin/blogs")
@router.post("/api/admin/blogs.html")
def admin_create_blog(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    language: str = Form("en"),
    db: Session = Depends(get_db),
):
    require_admin(request)
    data = BlogCreate(title=title, content=content)
    blog_service.create_blog(db, data, language=language)
    return RedirectResponse(url="/admin/blogs", status_code=303)


@router.post("/api/admin/blogs/update/{blog_id}")
def admin_update_blog(
    request: Request,
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    require_admin(request)
    data = BlogUpdate(title=title, content=content)
    blog = blog_service.update_blog(db, blog_id, data)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return RedirectResponse(url="/admin/blogs", status_code=303)


@router.post("/api/admin/blogs/delete/{blog_id}")
def admin_delete_blog(
    request: Request,
    blog_id: int,
    db: Session = Depends(get_db),
):
    require_admin(request)
    success = blog_service.delete_blog(db, blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return RedirectResponse(url="/admin/blogs", status_code=303)
