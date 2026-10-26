"""从 Markdown 档案装载文章，并提供给站点接口与检索工具共用。

管理员可增删改文章；改完后原地刷新内存列表，前台立刻读到新内容。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.site_data import get_site

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: str
    tags: list[str]
    minutes: int
    featured: bool
    cover: str
    summary: str
    kind: str
    body: str

    def public(self, with_body: bool = False) -> dict:
        data = {
            "slug": self.slug,
            "title": self.title,
            "date": self.date,
            "tags": self.tags,
            "minutes": self.minutes,
            "featured": self.featured,
            "cover": self.cover,
            "summary": self.summary,
            "kind": self.kind,
        }
        if with_body:
            data["body"] = self.body
        return data


def _parse_value(raw: str):
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"').strip("'") for part in inner.split(",") if part.strip()]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value.strip('"').strip("'")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = _FRONTMATTER.match(text.strip() + "\n")
    if not match:
        raise ValueError("文章缺少 frontmatter")
    meta: dict = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        meta[key.strip()] = _parse_value(raw)
    return meta, match.group(2).strip()


def _format_tags(tags: list[str]) -> str:
    if not tags:
        return "[]"
    inner = ", ".join(f'"{tag}"' for tag in tags)
    return f"[{inner}]"


def render_post_markdown(post: Post) -> str:
    featured = "true" if post.featured else "false"
    return (
        "---\n"
        f'title: "{post.title}"\n'
        f"slug: {post.slug}\n"
        f"date: {post.date}\n"
        f"tags: {_format_tags(post.tags)}\n"
        f"minutes: {post.minutes}\n"
        f"featured: {featured}\n"
        f"cover: {post.cover}\n"
        f'summary: "{post.summary}"\n'
        f"kind: {post.kind}\n"
        "---\n\n"
        f"{post.body.rstrip()}\n"
    )


def post_from_payload(data: dict, *, require_slug: bool = True) -> Post:
    slug = str(data.get("slug") or "").strip()
    if require_slug and not slug:
        raise ValueError("slug 不能为空")
    if slug and not _SLUG_RE.fullmatch(slug):
        raise ValueError("slug 只能用小写字母、数字和连字符")
    title = str(data.get("title") or "").strip()
    if not title:
        raise ValueError("标题不能为空")
    date = str(data.get("date") or "").strip()
    if not date:
        raise ValueError("日期不能为空")
    tags = data.get("tags") or []
    if not isinstance(tags, list):
        raise ValueError("标签必须是列表")
    return Post(
        slug=slug,
        title=title,
        date=date,
        tags=[str(tag).strip() for tag in tags if str(tag).strip()],
        minutes=int(data.get("minutes") or 5),
        featured=bool(data.get("featured") or False),
        cover=str(data.get("cover") or "amber"),
        summary=str(data.get("summary") or "").strip(),
        kind=str(data.get("kind") or "essay"),
        body=str(data.get("body") or "").strip(),
    )


def load_posts() -> list[Post]:
    posts: list[Post] = []
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        slug = str(meta.get("slug") or path.stem)
        posts.append(
            Post(
                slug=slug,
                title=str(meta["title"]),
                date=str(meta["date"]),
                tags=list(meta.get("tags") or []),
                minutes=int(meta.get("minutes") or 5),
                featured=bool(meta.get("featured") or False),
                cover=str(meta.get("cover") or "amber"),
                summary=str(meta.get("summary") or ""),
                kind=str(meta.get("kind") or "essay"),
                body=body,
            )
        )
    slugs = [post.slug for post in posts]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("文章 slug 重复")
    posts.sort(key=lambda post: post.date, reverse=True)
    return posts


POSTS: list[Post] = []
POSTS_BY_SLUG: dict[str, Post] = {}


def reload_posts() -> list[Post]:
    loaded = load_posts()
    POSTS.clear()
    POSTS.extend(loaded)
    POSTS_BY_SLUG.clear()
    POSTS_BY_SLUG.update({post.slug: post for post in POSTS})
    return POSTS


reload_posts()


def featured_posts() -> list[Post]:
    chosen = [post for post in POSTS if post.featured]
    if len(chosen) >= 3:
        return chosen[:3]
    seen = {post.slug for post in chosen}
    for post in POSTS:
        if post.slug not in seen:
            chosen.append(post)
        if len(chosen) == 3:
            break
    return chosen


def site_payload() -> dict:
    site = get_site()
    return {
        "name": site["name"],
        "mark": site["mark"],
        "eyebrow": site["eyebrow"],
        "deck": site["deck"],
        "now": site["now"],
        "about": site["about"],
        "posts": [post.public() for post in POSTS],
        "featured": [post.public() for post in featured_posts()],
        "works": site["works"],
    }


def _post_path(slug: str) -> Path:
    return POSTS_DIR / f"{slug}.md"


def save_post(post: Post, *, previous_slug: str | None = None) -> Post:
    path = _post_path(post.slug)
    if previous_slug is None:
        if path.exists() or post.slug in POSTS_BY_SLUG:
            raise ValueError("slug 已存在")
    elif previous_slug != post.slug:
        if path.exists() or post.slug in POSTS_BY_SLUG:
            raise ValueError("slug 已存在")
        old = _post_path(previous_slug)
        if old.exists():
            old.unlink()
    path.write_text(render_post_markdown(post), encoding="utf-8")
    reload_posts()
    return POSTS_BY_SLUG[post.slug]


def delete_post(slug: str) -> None:
    path = _post_path(slug)
    if not path.exists() and slug not in POSTS_BY_SLUG:
        raise KeyError(slug)
    if path.exists():
        path.unlink()
    reload_posts()
