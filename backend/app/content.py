"""从 Markdown 档案装载文章，并提供给站点接口与检索工具共用。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.site_data import SITE

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "content" / "posts"

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


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


def load_posts() -> list[Post]:
    posts: list[Post] = []
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


POSTS = load_posts()
POSTS_BY_SLUG = {post.slug: post for post in POSTS}


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
    return {
        "name": SITE["name"],
        "mark": SITE["mark"],
        "eyebrow": SITE["eyebrow"],
        "deck": SITE["deck"],
        "now": SITE["now"],
        "about": SITE["about"],
        "posts": [post.public() for post in POSTS],
        "featured": [post.public() for post in featured_posts()],
        "works": SITE["works"],
    }
