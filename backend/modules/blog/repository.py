"""Blog database repository."""

from typing import Optional
from sqlalchemy.orm import Session
from .models import BlogPost
from .schemas import BlogPostCreate


class BlogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str) -> Optional[BlogPost]:
        if str(slug).isdigit():
            post = self.db.query(BlogPost).filter(BlogPost.id == int(slug)).first()
            if post:
                return post
        return self.db.query(BlogPost).filter(BlogPost.slug == slug).first()

    def list_posts(self, lang: str = "en", limit: int = 20, offset: int = 0) -> list[BlogPost]:
        posts = (
            self.db.query(BlogPost)
            .filter(BlogPost.language == lang)
            .order_by(BlogPost.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        if not posts and lang != "en":
            posts = (
                self.db.query(BlogPost)
                .order_by(BlogPost.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        return posts

    def create_post(self, data: BlogPostCreate) -> BlogPost:
        post = BlogPost(
            title=data.title,
            slug=data.slug,
            content=data.content,
            summary=data.summary,
            language=data.language,
            tags=data.tags,
            author=data.author,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Optional[BlogPost]:
        return self.db.query(BlogPost).filter(BlogPost.id == post_id).first()

    def list_all_posts(self, limit: int = 100, offset: int = 0) -> list[BlogPost]:
        return (
            self.db.query(BlogPost)
            .order_by(BlogPost.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_post(self, post_id: int, data: BlogPostCreate) -> Optional[BlogPost]:
        post = self.get_by_id(post_id)
        if not post:
            return None
        post.title = data.title
        if data.slug:
            post.slug = data.slug
        post.content = data.content
        post.summary = data.summary
        post.language = data.language
        if data.tags is not None:
            post.tags = data.tags
        if data.author:
            post.author = data.author
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post_id: int) -> bool:
        post = self.get_by_id(post_id)
        if not post:
            return False
        self.db.delete(post)
        self.db.commit()
        return True

