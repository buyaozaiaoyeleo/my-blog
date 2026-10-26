"""管理员接口：登录、改站点文案、增删改文章。"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import ADMIN_USER, authenticate, require_admin
from app.content import (
    POSTS,
    POSTS_BY_SLUG,
    delete_post,
    post_from_payload,
    save_post,
)
from app.site_data import get_site, replace_site

router = APIRouter(prefix="/api/admin", tags=["admin"])


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class PostBody(BaseModel):
    slug: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    date: str = Field(min_length=1, max_length=32)
    tags: list[str] = Field(default_factory=list)
    minutes: int = Field(default=5, ge=1, le=180)
    featured: bool = False
    cover: str = Field(default="amber", max_length=32)
    summary: str = Field(default="", max_length=2000)
    kind: str = Field(default="essay", max_length=32)
    body: str = Field(default="", max_length=200_000)


@router.post("/login")
def login(body: LoginBody):
    token = authenticate(body.username.strip(), body.password)
    return {"token": token, "username": ADMIN_USER}


@router.get("/me")
def me(username: Annotated[str, Depends(require_admin)]):
    return {"username": username}


@router.get("/site")
def admin_site(_: Annotated[str, Depends(require_admin)]):
    return get_site()


@router.put("/site")
def update_site(payload: dict, _: Annotated[str, Depends(require_admin)]):
    try:
        return replace_site(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/posts")
def admin_posts(_: Annotated[str, Depends(require_admin)]):
    return [post.public(with_body=True) for post in POSTS]


@router.get("/posts/{slug}")
def admin_post(slug: str, _: Annotated[str, Depends(require_admin)]):
    found = POSTS_BY_SLUG.get(slug)
    if found is None:
        raise HTTPException(status_code=404, detail="没有这篇文章")
    return found.public(with_body=True)


@router.post("/posts")
def create_post(body: PostBody, _: Annotated[str, Depends(require_admin)]):
    try:
        post = post_from_payload(body.model_dump())
        saved = save_post(post)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return saved.public(with_body=True)


@router.put("/posts/{slug}")
def update_post(slug: str, body: PostBody, _: Annotated[str, Depends(require_admin)]):
    if slug not in POSTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="没有这篇文章")
    try:
        post = post_from_payload(body.model_dump())
        saved = save_post(post, previous_slug=slug)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return saved.public(with_body=True)


@router.delete("/posts/{slug}")
def remove_post(slug: str, _: Annotated[str, Depends(require_admin)]):
    if slug not in POSTS_BY_SLUG:
        raise HTTPException(status_code=404, detail="没有这篇文章")
    delete_post(slug)
    return {"ok": True, "slug": slug}
