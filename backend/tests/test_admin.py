from pathlib import Path

from fastapi.testclient import TestClient

from app.content import POSTS_DIR, reload_posts
from app.main import app
from app.site_data import DEFAULT_SITE, SITE, SITE_PATH

client = TestClient(app)


def _auth_headers():
    login = client.post("/api/admin/login", json={"username": "changxy", "password": "changxy"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['token']}"}


def test_admin_login_rejects_bad_password():
    response = client.post("/api/admin/login", json={"username": "changxy", "password": "nope"})
    assert response.status_code == 401


def test_admin_can_update_site_and_public_reads_it():
    headers = _auth_headers()
    payload = {
        **DEFAULT_SITE,
        "deck": "管理舱改过的甲板说明。",
        "now": {**DEFAULT_SITE["now"], "writing": "后台测试近况"},
    }
    saved = client.put("/api/admin/site", json=payload, headers=headers)
    assert saved.status_code == 200
    assert saved.json()["deck"] == "管理舱改过的甲板说明。"

    public = client.get("/api/site")
    assert public.status_code == 200
    assert public.json()["deck"] == "管理舱改过的甲板说明。"
    assert public.json()["now"]["writing"] == "后台测试近况"

    # restore defaults for other tests
    SITE.clear()
    SITE.update(DEFAULT_SITE)
    if SITE_PATH.exists():
        SITE_PATH.unlink()


def test_admin_can_create_edit_delete_post():
    headers = _auth_headers()
    slug = "admin-temp-signal"
    path = POSTS_DIR / f"{slug}.md"
    if path.exists():
        path.unlink()
        reload_posts()

    created = client.post(
        "/api/admin/posts",
        headers=headers,
        json={
            "slug": slug,
            "title": "临时信号",
            "date": "2099-01-01",
            "tags": ["测试"],
            "minutes": 2,
            "featured": False,
            "cover": "ice",
            "summary": "只给后台测试用。",
            "kind": "essay",
            "body": "这是一篇会被删掉的测试文章。",
        },
    )
    assert created.status_code == 200
    assert created.json()["slug"] == slug

    listed = client.get("/api/site")
    assert any(post["slug"] == slug for post in listed.json()["posts"])

    updated = client.put(
        f"/api/admin/posts/{slug}",
        headers=headers,
        json={
            "slug": slug,
            "title": "临时信号（改）",
            "date": "2099-01-02",
            "tags": ["测试", "后台"],
            "minutes": 3,
            "featured": True,
            "cover": "amber",
            "summary": "改过摘要。",
            "kind": "essay",
            "body": "正文也改了。",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "临时信号（改）"

    detail = client.get(f"/api/posts/{slug}")
    assert detail.status_code == 200
    assert "正文也改了" in detail.json()["body"]

    deleted = client.delete(f"/api/admin/posts/{slug}", headers=headers)
    assert deleted.status_code == 200
    assert client.get(f"/api/posts/{slug}").status_code == 404
    assert not Path(path).exists()


def test_admin_routes_require_token():
    assert client.get("/api/admin/posts").status_code == 401
    assert client.get("/api/admin/site").status_code == 401
