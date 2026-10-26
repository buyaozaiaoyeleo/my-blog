"""博客接口：站点、文章、RSS，以及 LangGraph 档案员。"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.admin import router as admin_router
from app.content import POSTS_BY_SLUG, site_payload
from app.graph import GRAPH, run_agent
from app.site_data import SITE

app = FastAPI(title=SITE["name"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router)

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


class Turn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[Turn] = Field(default_factory=list, max_length=12)


@app.get("/api/health")
def health():
    nodes = list(GRAPH.get_graph().nodes)
    return {"ok": True, "graph": nodes}


@app.get("/api/site")
def site():
    return site_payload()


@app.get("/api/posts/{slug}")
def post(slug: str):
    found = POSTS_BY_SLUG.get(slug)
    if found is None:
        raise HTTPException(status_code=404, detail="没有这篇文章")
    return found.public(with_body=True)


@app.post("/api/chat")
def chat(body: ChatRequest):
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="问题是空的")
    history = [{"role": turn.role, "content": turn.content} for turn in body.history][-8:]
    return run_agent(message, history)


@app.get("/feed.xml")
def feed():
    payload = site_payload()
    items = []
    for post_item in payload["posts"]:
        items.append(
            "<item>"
            f"<title>{escape(post_item['title'])}</title>"
            f"<link>/essays/{escape(post_item['slug'])}</link>"
            f"<description>{escape(post_item['summary'])}</description>"
            f"<pubDate>{escape(post_item['date'])}</pubDate>"
            "</item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        f"<title>{escape(SITE['name'])}</title>"
        f"<description>{escape(SITE['deck'])}</description>"
        + "".join(items)
        + "</channel></rss>"
    )
    return Response(content=xml, media_type="application/xml")


def _mount_frontend():
    if not DIST.exists():
        return
    assets = DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")


_mount_frontend()
