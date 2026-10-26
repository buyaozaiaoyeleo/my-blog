"""站点里不随文章变化的那一层：船名、近况、关于、作品。

默认写在代码里；管理员保存后落到 content/site.json，下次启动优先读文件。
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_PATH = ROOT / "content" / "site.json"

DEFAULT_SITE = {
    "name": "不要再熬夜了",
    "mark": "夜航",
    "eyebrow": "Night Passage",
    "deck": "技术、视觉，和夜里的句子。首页是驾驶舱，文章是航线，实验室里有一位会翻档案的代理。",
    "now": {
        "writing": "夜航仪的状态栏",
        "reading": "关于网格与节拍的笔记",
        "zone": "东八区",
    },
    "about": {
        "lede": "白天的东西留在白天。这里只放还愿意被反复打开的界面、句子，和一点点生成艺术。",
        "paragraphs": [
            "「不要再熬夜了」是一艘个人站点，不是简历。名字是态度：夜里可以做事，但每一件都得配得上那盏还亮着的灯。",
            "时间线上的年份，记的是这艘船自己的结构怎么长出来。先有仪表，再有叙事，然后才让一个会翻档案的代理上船。代理用 LangGraph 走路，用 LangChain 拿工具，回答必须带回文章出处。",
            "想合作、想争辩、想问某篇到底在说什么，去实验室直接问。档案员只根据船上的文字回答，不会替你编一段没有写过的生平。",
        ],
        "timeline": [
            {
                "year": "2024",
                "title": "先写船名",
                "text": "把态度写成名字，而不是「欢迎来到我的博客」。人先记住句子，再决定要不要留下。",
            },
            {
                "year": "2025",
                "title": "仪表上船",
                "text": "首页改成驾驶舱：你在哪、下一站是什么、哪盏灯是亮的。目录退到档案里。",
            },
            {
                "year": "2026 春",
                "title": "一屏一件事",
                "text": "滚动叙事收成节拍。每次滚动只增加一个信息，动效跟在句子后面，不跑到句子前面。",
            },
            {
                "year": "2026 秋",
                "title": "档案员上船",
                "text": "LangGraph 固定走规划、检索、成稿。没有模型钥匙时，仍然引用原文；有钥匙时，只改变组织语言的那一步。",
            },
        ],
        "tools": ["React", "TypeScript", "Vite", "LangGraph", "LangChain", "FastAPI"],
    },
    "works": [
        {
            "slug": "instruments",
            "title": "夜航仪",
            "year": "2026",
            "role": "界面 / 编辑",
            "cover": "amber",
            "href": "/",
            "summary": "把博客首页从时间排序的列表，改成一块只回答三个问题的仪表。",
            "points": [
                "主张用船名本身，不写欢迎辞。",
                "首页只留三篇精选，其余进入档案。",
                "状态栏放正在写、正在读、时区，让站点有一个会变的事实。",
            ],
            "result": "打开首页的人先看见态度和下一站，而不是二十个同等大小的标题。",
        },
        {
            "slug": "scroll-score",
            "title": "滚动叙事",
            "year": "2026",
            "role": "写作 / 排版",
            "cover": "tide",
            "href": "/essays/one-screen",
            "summary": "用章节而不是全屏动画来管节拍。大编号是拍点，正文是旋律。",
            "points": [
                "故事型文章按二级标题拆成独立的屏。",
                "每一屏只推进一个判断。",
                "动效限制在出现和淡入，阅读本身不被视差打断。",
            ],
            "result": "两篇航线文章可以一口气读完，也能单独截一屏发给别人。",
        },
        {
            "slug": "star-chart",
            "title": "星图",
            "year": "2026",
            "role": "生成 / 交互",
            "cover": "ice",
            "href": "/lab",
            "summary": "实验室里的星图会认鼠标。静海、风暴、极光是三种天气，不是三张贴图。",
            "points": [
                "粒子离指针近时才连线，远处置于安静。",
                "尊重系统的减少动态设置，必要时星图停住。",
                "绚丽集中在实验室，文章页保持可长时间阅读。",
            ],
            "result": "背景终于能被碰到。碰不到的粒子不再上船。",
        },
        {
            "slug": "archivist",
            "title": "档案员",
            "year": "2026",
            "role": "LangGraph / 检索",
            "cover": "flare",
            "href": "/lab",
            "summary": "一位沿着固定图走路的代理：先决定翻哪份档案，再引用，最后才把话说完整。",
            "points": [
                "工具只有搜索文章、阅读全文、列出目录、列出作品、阅读关于。",
                "图的节点是规划与执行，条件边决定还要不要再翻一次。",
                "出处以篇名形式留在回答下面，可以直接点进文章。",
            ],
            "result": "问「高光色为什么只有一种」，得到的是文章里的理由，不是一段泛泛的设计建议。",
        },
    ],
}


def _load_site() -> dict:
    if SITE_PATH.exists():
        data = json.loads(SITE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            merged = copy.deepcopy(DEFAULT_SITE)
            merged.update(data)
            return merged
    return copy.deepcopy(DEFAULT_SITE)


SITE = _load_site()


def get_site() -> dict:
    return SITE


def replace_site(data: dict) -> dict:
    """用管理员提交的数据整体替换站点配置，并写入磁盘。"""
    required = ("name", "mark", "eyebrow", "deck", "now", "about", "works")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"站点数据缺少字段：{', '.join(missing)}")
    SITE.clear()
    SITE.update(copy.deepcopy(data))
    SITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SITE_PATH.write_text(json.dumps(SITE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return SITE
