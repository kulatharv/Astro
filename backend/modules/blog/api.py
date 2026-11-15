"""Blog Router and Public Service Interface."""

import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.db import get_db
from shared.errors import NotFoundError
from .schemas import BlogPostCreate, BlogPostResponse
from .engine import BlogEngine

router = APIRouter(prefix="/api/blogs", tags=["blogs"])


class BlogService:
    def get_post(self, slug: str, db: Session) -> BlogPostResponse:
        engine = BlogEngine(db)
        return engine.get_post(slug)

    def get_post_by_id(self, post_id: int, db: Session) -> BlogPostResponse:
        engine = BlogEngine(db)
        return engine.get_post_by_id(post_id)

    def list_posts(self, lang: str, db: Session, limit: int = 20) -> list[BlogPostResponse]:
        engine = BlogEngine(db)
        return engine.list_posts(lang=lang, limit=limit)

    def list_all_posts(self, db: Session, limit: int = 100, offset: int = 0) -> list[BlogPostResponse]:
        engine = BlogEngine(db)
        return engine.list_all_posts(limit=limit, offset=offset)

    def create_post(self, req: BlogPostCreate, db: Session) -> BlogPostResponse:
        if not req.slug:
            clean_slug = re.sub(r"[^\w]+", "-", req.title.lower()).strip("-")
            req.slug = clean_slug or f"blog-{int(datetime.utcnow().timestamp())}"
        engine = BlogEngine(db)
        return engine.create_post(req)

    def update_post(self, post_id: int, req: BlogPostCreate, db: Session) -> BlogPostResponse:
        if not req.slug:
            clean_slug = re.sub(r"[^\w]+", "-", req.title.lower()).strip("-")
            req.slug = clean_slug
        engine = BlogEngine(db)
        return engine.update_post(post_id, req)

    def delete_post(self, post_id: int, db: Session) -> bool:
        engine = BlogEngine(db)
        return engine.delete_post(post_id)

    def get_blog_by_id(self, db: Session, blog_id: int):
        from .models import BlogPost
        return db.query(BlogPost).filter(BlogPost.id == blog_id).first()

    def delete_blog(self, db: Session, blog_id: int):
        from .models import BlogPost
        post = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
        if post:
            db.delete(post)
            db.commit()
            return True
        return False

    def get_all_blogs(self, db: Session, lang: str = "en"):
        engine = BlogEngine(db)
        return [self.get_blog_by_id(db, p.id) for p in engine.list_posts(lang=lang)]


blog_service = BlogService()


@router.get("", response_model=list[BlogPostResponse])
def list_blogs(lang: str = "en", limit: int = 20, db: Session = Depends(get_db)):
    if lang == "all":
        return blog_service.list_all_posts(db=db, limit=limit)
    return blog_service.list_posts(lang=lang, db=db, limit=limit)


@router.get("/all", response_model=list[BlogPostResponse])
def list_all_blogs_admin(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return blog_service.list_all_posts(db=db, limit=limit, offset=offset)


@router.get("/id/{post_id}", response_model=BlogPostResponse)
def get_blog_by_numeric_id(post_id: int, db: Session = Depends(get_db)):
    try:
        return blog_service.get_post_by_id(post_id=post_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{slug}", response_model=BlogPostResponse)
def get_blog(slug: str, db: Session = Depends(get_db)):
    try:
        return blog_service.get_post(slug=slug, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_blog(req: BlogPostCreate, db: Session = Depends(get_db)):
    return blog_service.create_post(req, db=db)


@router.put("/{post_id}", response_model=BlogPostResponse)
def update_blog(post_id: int, req: BlogPostCreate, db: Session = Depends(get_db)):
    try:
        return blog_service.update_post(post_id=post_id, req=req, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{post_id}")
def delete_blog(post_id: int, db: Session = Depends(get_db)):
    try:
        blog_service.delete_post(post_id=post_id, db=db)
        return {"status": "success", "message": f"Blog post {post_id} deleted successfully."}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

