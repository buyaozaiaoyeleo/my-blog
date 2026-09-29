from fastapi.testclient import TestClient

from app.archive import search_archive
from app.graph import build_graph, run_agent
from app.main import app


def test_search_finds_highlight_essay():
    hits = search_archive("颜色为什么只留一种高光", limit=3)
    assert hits
    assert hits[0]["slug"] == "one-highlight"


def test_graph_has_agent_and_tools():
    graph = build_graph().get_graph()
    assert "agent" in graph.nodes
    assert "tools" in graph.nodes


def test_archivist_quotes_homepage_reason():
    result = run_agent("首页为什么不是文章列表？")
    assert "夜航仪" in result["reply"]
    assert result["sources"]
    assert result["sources"][0]["slug"] == "night-instruments"
    assert any(step.startswith("规划") for step in result["trace"])
    assert any(step.startswith("检索") for step in result["trace"])
    assert result["mode"] == "archive"


def test_archivist_lists_works():
    result = run_agent("有哪些作品？")
    assert "星图" in result["reply"]
    assert "档案员" in result["reply"]


def test_archivist_greeting_mentions_current_writing():
    result = run_agent("你好")
    assert "档案员" in result["reply"]
    assert "夜航仪的状态栏" in result["reply"]


def test_site_lists_eight_posts_and_serves_body():
    client = TestClient(app)
    site = client.get("/api/site")
    assert site.status_code == 200
    assert len(site.json()["posts"]) == 8
    post = client.get("/api/posts/one-highlight")
    assert post.status_code == 200
    assert "琥珀色" in post.json()["body"]
    missing = client.get("/api/posts/not-a-real-slug")
    assert missing.status_code == 404
