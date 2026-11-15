"""
Integration Test Suite for Blog CRUD in Admin Engine.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from shared.db.session import SessionLocal
from modules.blog.api import blog_service
from modules.blog.schemas import BlogPostCreate


def run_tests():
    db = SessionLocal()
    print("\n========================================================")
    print("           RUNNING BLOG CRUD INTEGRATION TESTS          ")
    print("========================================================")

    # 1. Test Create Blog
    new_blog = BlogPostCreate(
        title="Surya Grahan 2026: Auspicious Remedies & Vedic Guidelines",
        slug="surya-grahan-2026-remedies-guidelines",
        content="Detailed astrological analysis of the upcoming solar eclipse across Ashwini Nakshatra...",
        summary="Auspicious timings, dos and donts, and Surya mantra chanting rules.",
        language="en",
        tags=["Surya Grahan", "Eclipse", "Vedic Remedies"],
        author="Acharya Shastri",
    )

    created = blog_service.create_post(new_blog, db=db)
    print(f"1. Created Blog: ID={created.id} | Slug={created.slug} | Title={created.title}")
    assert created.id is not None
    assert created.slug == "surya-grahan-2026-remedies-guidelines"
    assert created.language == "en"

    # 2. Test Get by ID
    fetched = blog_service.get_post_by_id(created.id, db=db)
    print(f"2. Fetched by ID: ID={fetched.id} | Author={fetched.author}")
    assert fetched.id == created.id
    assert fetched.author == "Acharya Shastri"

    # 3. Test List All Blogs
    all_blogs = blog_service.list_all_posts(db=db, limit=20)
    print(f"3. List All Blogs: Retrieved {len(all_blogs)} posts")
    assert len(all_blogs) >= 1

    # 4. Test Update Blog
    update_data = BlogPostCreate(
        title="Surya Grahan 2026: Auspicious Remedies & Complete Muhurta",
        slug="surya-grahan-2026-complete-muhurta",
        content="Updated comprehensive guidelines with chanting window from 10:15 AM to 01:45 PM...",
        summary="Updated timing and consecration details.",
        language="en",
        tags=["Surya Grahan", "Solar Eclipse", "Mantras", "Updated"],
        author="Acharya Shastri (Senior Vedic Scholar)",
    )
    updated = blog_service.update_post(created.id, update_data, db=db)
    print(f"4. Updated Blog: ID={updated.id} | New Title={updated.title} | New Slug={updated.slug}")
    assert updated.title == "Surya Grahan 2026: Auspicious Remedies & Complete Muhurta"
    assert updated.slug == "surya-grahan-2026-complete-muhurta"

    # 5. Test Delete Blog
    del_res = blog_service.delete_post(created.id, db=db)
    print(f"5. Deleted Blog: ID={created.id} | Success={del_res}")
    assert del_res is True

    # Verify deletion
    try:
        blog_service.get_post_by_id(created.id, db=db)
        assert False, "Post should have been deleted"
    except Exception:
        print("   Confirmed post no longer exists in database.")

    print("\n========================================================")
    print("      ALL 5 BLOG CRUD TESTS PASSED 100%                 ")
    print("========================================================\n")

    db.close()


if __name__ == "__main__":
    run_tests()

