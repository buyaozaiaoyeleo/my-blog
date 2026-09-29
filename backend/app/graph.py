"""档案员：一条固定的 LangGraph。

规划节点决定调用哪些 LangChain 工具，工具节点去翻档案，
再回到规划节点成稿。有模型钥匙时由模型组织语言；没有时直接引用原文。
图的形状两种情况下相同。
"""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app import archive

SYSTEM = """你是「不要再熬夜了」这艘博客的档案员。
只根据工具返回的内容回答，用简体中文，语气像夜里的编辑：短句、具体、有判断。
回答博客、作品、关于、近况之前，必须先调用工具。不要编造船上没有的文章、经历或链接。
如果档案对不上，就说没有，并提一两篇真正存在的标题。
不要自称人工智能，不要写“作为语言模型”。引用时写出文章标题。"""

_GREETING = re.compile(
    r"^(你好|嗨|hi|hello|hey|在吗|晚上好|早安|午安|早上好|你好呀)[!！。.~\s]*$",
    re.I,
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    sources: list
    steps: int
    mode: str


@tool
def search_posts(query: str, limit: int = 3) -> str:
    """按自然语言在博客档案中检索文章，返回标题、摘要和最相关的摘录。"""

    hits = archive.search_archive(query, limit)
    return json.dumps({"hits": hits}, ensure_ascii=False)


@tool
def read_post(slug: str) -> str:
    """按 slug 或标题阅读一篇文章的全文。"""

    return json.dumps(archive.read_archive(slug), ensure_ascii=False)


@tool
def list_posts() -> str:
    """列出全部文章的标题、日期和摘要，以及站点此刻正在写什么。"""

    return json.dumps(archive.list_archive(), ensure_ascii=False)


@tool
def list_works() -> str:
    """列出作品集：标题、角色、摘要和结果。"""

    return json.dumps(archive.list_works(), ensure_ascii=False)


@tool
def read_about() -> str:
    """阅读关于页、船的简介、时间线和此刻状态。"""

    return json.dumps(archive.read_about(), ensure_ascii=False)


TOOL_LIST = [search_posts, read_post, list_posts, list_works, read_about]
TOOL_MAP = {item.name: item for item in TOOL_LIST}

_llm = None
_llm_broken = False
_llm_ready = False


def get_llm():
    global _llm, _llm_broken, _llm_ready
    if _llm_broken:
        return None
    if _llm_ready:
        return _llm
    key = os.getenv("OPENAI_API_KEY", "").strip()
    _llm_ready = True
    if not key:
        _llm = None
        return None
    from langchain_openai import ChatOpenAI

    kwargs = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.4,
        "api_key": key,
    }
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    if base_url:
        kwargs["base_url"] = base_url
    _llm = ChatOpenAI(**kwargs)
    return _llm


def last_human(messages) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _call(name: str, args: dict) -> dict:
    return {
        "name": name,
        "args": args,
        "id": f"call_{uuid.uuid4().hex[:10]}",
        "type": "tool_call",
    }


def heuristic_plan(question: str) -> AIMessage:
    text = question.strip()
    calls = []
    if _GREETING.match(text):
        calls.append(_call("read_about", {}))
    else:
        catalog_cues = ("有哪些文章", "文章目录", "写过什么", "最近在写", "最近写", "在写什么", "全部文章")
        if any(word in text for word in catalog_cues):
            calls.append(_call("list_posts", {}))
        if any(word in text for word in ("作品", "案例", "项目")):
            calls.append(_call("list_works", {}))
        if any(word in text for word in ("关于", "你是谁", "这艘", "简介", "时间线", "什么技术", "技术栈")):
            calls.append(_call("read_about", {}))
        for post in archive.POSTS:
            if post.title in text or post.slug in text:
                calls.append(_call("read_post", {"slug": post.slug}))
        if not calls:
            calls.append(_call("search_posts", {"query": text[:500], "limit": 3}))
    return AIMessage(content="", tool_calls=calls)


def _loads(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
    return data if isinstance(data, dict) else {"raw": data}


def _tool_payloads(messages) -> list[dict]:
    payloads = []
    seen_human = False
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            seen_human = True
            break
        if isinstance(message, ToolMessage):
            payloads.append(_loads(message.content if isinstance(message.content, str) else str(message.content)))
    if not seen_human:
        payloads = [
            _loads(message.content if isinstance(message.content, str) else str(message.content))
            for message in messages
            if isinstance(message, ToolMessage)
        ]
    payloads.reverse()
    return payloads


def _has_tool_result(messages) -> bool:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return False
        if isinstance(message, ToolMessage):
            return True
    return False


def _bold(title: str) -> str:
    return f"**{title}**"


def compose_from_tools(messages) -> str:
    question = last_human(messages).strip()
    payloads = _tool_payloads(messages)
    if _GREETING.match(question):
        now = {}
        for payload in payloads:
            if payload.get("now"):
                now = payload["now"]
        writing = now.get("writing") or "一篇还没起名的笔记"
        return (
            "夜里好。我是这艘博客的档案员，沿着 LangGraph 在文章和作品之间走。\n\n"
            f"这一阵正在写的是「{writing}」。你可以直接问某篇在讲什么，也可以问有哪些作品。"
        )

    blocks: list[str] = []
    for payload in payloads:
        if "error" in payload and len(payload) == 1:
            blocks.append(str(payload["error"]))
            continue
        if "posts" in payload:
            now = payload.get("now") or {}
            lines = []
            if now.get("writing"):
                lines.append(f"此刻正在写的是「{now['writing']}」。正在读的是「{now.get('reading', '')}」。")
            lines.append("档案里的航线：")
            for index, post in enumerate(payload["posts"], start=1):
                lines.append(f"{index}. {_bold(post['title'])}（{post['date']}）\n{post['summary']}")
            blocks.append("\n\n".join(lines))
        if "works" in payload:
            lines = ["船上目前这些作品能点开："]
            for work in payload["works"]:
                lines.append(
                    f"{_bold(work['title'])} · {work['role']}\n{work['summary']}\n结果：{work['result']}"
                )
            blocks.append("\n\n".join(lines))
        if "about" in payload:
            about = payload["about"]
            timeline = "\n".join(
                f"- {item['year']} {item['title']}：{item['text']}" for item in about.get("timeline", [])
            )
            tools = "、".join(about.get("tools") or [])
            paragraphs = "\n\n".join(about.get("paragraphs") or [])
            blocks.append(
                f"{_bold(about['name'])}\n{about['lede']}\n\n{paragraphs}\n\n时间线：\n{timeline}\n\n工具：{tools}"
            )
        if "post" in payload:
            post = payload["post"]
            excerpt = archive.best_excerpt(question or post["title"], post["body"], limit=180)
            blocks.append(f"{_bold(post['title'])}\n{post['summary']}\n\n摘录：{excerpt}")
        if "hits" in payload:
            hits = payload["hits"]
            if not hits:
                blocks.append(
                    "这艘船上没有直接写到这件事。可以换一个档案里真有的词，比如高光、留白、星图、夜航仪。"
                )
            else:
                lines = ["我按你的问题翻到这些段落："]
                for hit in hits:
                    lines.append(f"{_bold(hit['title'])}\n{hit['summary']}\n摘录：{hit['excerpt']}")
                lines.append("想看全文，点下面的篇名。")
                blocks.append("\n\n".join(lines))
    if not blocks:
        return "档案这一跳是空的。换个问法，比如「首页为什么不是文章列表」。"
    return "\n\n".join(blocks)


def _sources_from(payload: dict) -> list[dict]:
    found = []
    for hit in payload.get("hits") or []:
        if hit.get("slug") and hit.get("title"):
            found.append({"slug": hit["slug"], "title": hit["title"]})
    post = payload.get("post")
    if isinstance(post, dict) and post.get("slug"):
        found.append({"slug": post["slug"], "title": post["title"]})
    for post in payload.get("posts") or []:
        if post.get("slug") and post.get("title"):
            found.append({"slug": post["slug"], "title": post["title"]})
    return found


def _dedupe(sources: list[dict]) -> list[dict]:
    seen = set()
    ordered = []
    for source in sources:
        if source["slug"] in seen:
            continue
        seen.add(source["slug"])
        ordered.append(source)
    return ordered


def agent(state: AgentState) -> dict:
    global _llm_broken
    messages = state["messages"]
    steps = int(state.get("steps") or 0) + 1
    mode = state.get("mode") or "archive"
    if steps > 6:
        return {
            "messages": [AIMessage(content=compose_from_tools(messages))],
            "steps": steps,
            "mode": mode,
        }

    llm = get_llm()
    if llm is None:
        if _has_tool_result(messages):
            return {
                "messages": [AIMessage(content=compose_from_tools(messages))],
                "steps": steps,
                "mode": "archive",
            }
        return {"messages": [heuristic_plan(last_human(messages))], "steps": steps, "mode": "archive"}

    try:
        response = llm.bind_tools(TOOL_LIST).invoke(messages)
    except Exception:
        _llm_broken = True
        if _has_tool_result(messages):
            text = compose_from_tools(messages) + "\n\n（模型没有连上，上面这段改由档案直接拼出。）"
            return {"messages": [AIMessage(content=text)], "steps": steps, "mode": "archive"}
        return {"messages": [heuristic_plan(last_human(messages))], "steps": steps, "mode": "archive"}

    if not getattr(response, "tool_calls", None) and not str(response.content or "").strip():
        response = AIMessage(content=compose_from_tools(messages))
    elif not getattr(response, "tool_calls", None) and not _has_tool_result(messages):
        # 没有翻档案就成稿时，改走检索，避免模型凭空回答。
        return {"messages": [heuristic_plan(last_human(messages))], "steps": steps, "mode": "model"}
    return {"messages": [response], "steps": steps, "mode": "model"}


def run_tools(state: AgentState) -> dict:
    last = state["messages"][-1]
    sources = list(state.get("sources") or [])
    messages = []
    for call in getattr(last, "tool_calls", None) or []:
        name = call.get("name")
        args = call.get("args") or {}
        tool_fn = TOOL_MAP.get(name)
        if tool_fn is None:
            payload = {"error": f"没有这个工具：{name}"}
        else:
            try:
                raw = tool_fn.invoke(args)
                payload = _loads(raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False))
            except Exception as exc:  # 工具参数不合法时把错误交还给图，而不是让请求失败。
                payload = {"error": str(exc)}
        sources.extend(_sources_from(payload))
        messages.append(
            ToolMessage(content=json.dumps(payload, ensure_ascii=False), tool_call_id=call.get("id", "call_unknown"))
        )
    return {"messages": messages, "sources": _dedupe(sources)}


def route(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "end"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", run_tools)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", route, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


GRAPH = build_graph()


def _trace(new_messages) -> list[str]:
    trace: list[str] = []
    index = 0
    while index < len(new_messages):
        message = new_messages[index]
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            names = "、".join(call["name"] for call in message.tool_calls)
            trace.append(f"规划 · {names}")
        elif isinstance(message, ToolMessage):
            count = 0
            while index < len(new_messages) and isinstance(new_messages[index], ToolMessage):
                count += 1
                index += 1
            trace.append(f"检索 · {count} 次返回")
            continue
        elif isinstance(message, AIMessage) and str(message.content or "").strip():
            trace.append("成稿")
        index += 1
    return trace


def run_agent(question: str, history: list[dict] | None = None) -> dict:
    messages = [SystemMessage(content=SYSTEM)]
    for turn in history or []:
        content = str(turn.get("content") or "").strip()
        if not content:
            continue
        if turn.get("role") == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    messages.append(HumanMessage(content=question.strip()))
    prior = len(messages)
    result = GRAPH.invoke(
        {"messages": messages, "sources": [], "steps": 0, "mode": "archive"},
        config={"recursion_limit": 12},
    )
    reply = ""
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and str(message.content or "").strip() and not message.tool_calls:
            reply = str(message.content).strip()
            break
    if not reply:
        reply = compose_from_tools(result["messages"])
    mode = result.get("mode") or "archive"
    return {
        "reply": reply,
        "sources": result.get("sources") or [],
        "trace": _trace(result["messages"][prior:]),
        "mode": mode,
        "mode_label": "LangGraph · 模型成稿" if mode == "model" else "LangGraph · 档案直引",
    }
