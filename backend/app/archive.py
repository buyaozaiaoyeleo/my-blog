"""不依赖向量模型的中文档案检索。给 LangGraph 的工具用。"""

from __future__ import annotations

import re

from app.content import POSTS, Post
from app.site_data import SITE

_LATIN = re.compile(r"[a-z0-9]{2,}")
_HAN = re.compile(r"[\u4e00-\u9fff]")
_SENTENCE = re.compile(r"[^。！？\n]+[。！？]?")


def tokens(text: str) -> set[str]:
    lowered = text.lower()
    found = set(_LATIN.findall(lowered))
    chars = _HAN.findall(lowered)
    found.update(a + b for a, b in zip(chars, chars[1:]))
    found.update(chars)
    return {token for token in found if token.strip()}


def _score(query: str, post: Post) -> int:
    query_tokens = tokens(query)
    if not query_tokens:
        return 0
    title = tokens(post.title)
    summary = tokens(post.summary)
    body = tokens(post.body + " " + " ".join(post.tags))
    score = 4 * len(query_tokens & title) + 2 * len(query_tokens & summary) + len(query_tokens & body)
    compact = re.sub(r"\s+", "", query)
    if compact and compact in (post.title + post.summary + post.body):
        score += 8
    return score


def best_excerpt(query: str, body: str, limit: int = 120) -> str:
    pieces = []
    for raw in _SENTENCE.findall(body):
        sentence = raw.strip().lstrip("#").strip()
        if len(sentence) < 8 or sentence.startswith("```"):
            continue
        pieces.append(sentence)
    if not pieces:
        pieces = [body.strip()]
    query_tokens = tokens(query)
    pieces.sort(key=lambda sentence: len(query_tokens & tokens(sentence)), reverse=True)
    picked = pieces[0]
    if len(picked) > limit:
        return picked[: limit - 1] + "…"
    return picked


def search_archive(query: str, limit: int = 3) -> list[dict]:
    limit = max(1, min(int(limit), 5))
    ranked = [( _score(query, post), post) for post in POSTS]
    ranked = [item for item in ranked if item[0] > 0]
    ranked.sort(key=lambda item: (item[0], item[1].date), reverse=True)
    hits = []
    for score, post in ranked[:limit]:
        hits.append(
            {
                "slug": post.slug,
                "title": post.title,
                "date": post.date,
                "summary": post.summary,
                "excerpt": best_excerpt(query, post.body),
                "score": score,
            }
        )
    return hits


def list_archive() -> dict:
    return {
        "now": SITE["now"],
        "posts": [
            {
                "slug": post.slug,
                "title": post.title,
                "date": post.date,
                "summary": post.summary,
                "tags": post.tags,
            }
            for post in POSTS
        ],
    }


def read_archive(slug: str) -> dict:
    post = next((item for item in POSTS if item.slug == slug), None)
    if post is None:
        titled = next((item for item in POSTS if item.title == slug), None)
        post = titled
    if post is None:
        return {"error": f"档案里没有「{slug}」。"}
    return {
        "post": {
            "slug": post.slug,
            "title": post.title,
            "date": post.date,
            "summary": post.summary,
            "tags": post.tags,
            "body": post.body,
        }
    }


def list_works() -> dict:
    return {
        "works": [
            {
                "slug": work["slug"],
                "title": work["title"],
                "year": work["year"],
                "role": work["role"],
                "summary": work["summary"],
                "result": work["result"],
            }
            for work in SITE["works"]
        ]
    }


def read_about() -> dict:
    about = SITE["about"]
    return {
        "about": {
            "name": SITE["name"],
            "deck": SITE["deck"],
            "lede": about["lede"],
            "paragraphs": about["paragraphs"],
            "timeline": about["timeline"],
            "tools": about["tools"],
        },
        "now": SITE["now"],
    }
