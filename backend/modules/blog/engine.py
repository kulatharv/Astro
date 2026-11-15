"""Blog Business Engine."""

from sqlalchemy.orm import Session
from shared.errors import NotFoundError
from .repository import BlogRepository
from .schemas import BlogPostCreate, BlogPostResponse


class BlogEngine:
    def __init__(self, db: Session):
        self.repo = BlogRepository(db)

    def get_post(self, slug: str) -> BlogPostResponse:
        post = self.repo.get_by_slug(slug)
        if not post:
            raise NotFoundError(f"Blog post with slug '{slug}' not found.")
        return BlogPostResponse.model_validate(post)

    def list_posts(self, lang: str = "en", limit: int = 20) -> list[BlogPostResponse]:
        posts = self.repo.list_posts(lang=lang, limit=limit)
        return [BlogPostResponse.model_validate(p) for p in posts]

    def create_post(self, data: BlogPostCreate) -> BlogPostResponse:
        post = self.repo.create_post(data)
        return BlogPostResponse.model_validate(post)

    def get_post_by_id(self, post_id: int) -> BlogPostResponse:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError(f"Blog post with ID {post_id} not found.")
        return BlogPostResponse.model_validate(post)

    def list_all_posts(self, limit: int = 100, offset: int = 0) -> list[BlogPostResponse]:
        posts = self.repo.list_all_posts(limit=limit, offset=offset)
        return [BlogPostResponse.model_validate(p) for p in posts]

    def update_post(self, post_id: int, data: BlogPostCreate) -> BlogPostResponse:
        post = self.repo.update_post(post_id, data)
        if not post:
            raise NotFoundError(f"Blog post with ID {post_id} not found.")
        return BlogPostResponse.model_validate(post)

    def delete_post(self, post_id: int) -> bool:
        success = self.repo.delete_post(post_id)
        if not success:
            raise NotFoundError(f"Blog post with ID {post_id} not found.")
        return True

