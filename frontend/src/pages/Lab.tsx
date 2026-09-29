import { useState } from "react";
import { Link } from "react-router-dom";
import { askArchive } from "../api";
import { Starfield, type Weather } from "../components/Starfield";
import { renderMarkdown } from "../markdown";
import { useTitle } from "../site";
import type { Source } from "../types";

type Msg = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  trace?: string[];
  modeLabel?: string;
};

const SUGGESTIONS = ["你好", "首页为什么不是文章列表？", "高光色为什么只有一种？", "有哪些作品？"];
const WEATHERS: { id: Weather; label: string }[] = [
  { id: "calm", label: "静海" },
  { id: "storm", label: "风暴" },
  { id: "aurora", label: "极光" },
];

export function Lab() {
  useTitle("实验室");
  const [weather, setWeather] = useState<Weather>("calm");
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content: "夜里好。我是档案员。问航线、颜色、作品，或者直接说你好。",
      modeLabel: "LangGraph · 待命",
    },
  ]);

  async function send(text: string) {
    const question = text.trim();
    if (!question || pending) return;
    const history = messages
      .filter((item) => item.modeLabel !== "LangGraph · 待命")
      .map((item) => ({ role: item.role, content: item.content }));
    setMessages((current) => [...current, { role: "user", content: question }]);
    setDraft("");
    setPending(true);
    try {
      const result = await askArchive(question, history);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: result.reply,
          sources: result.sources,
          trace: result.trace,
          modeLabel: result.mode_label,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        { role: "assistant", content: "这一跳没有返回。档案接口可能还没开。", modeLabel: "失败" },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="block">
      <p className="eyebrow">Lab</p>
      <h1>星图与档案员</h1>
      <p className="deck narrow">
        左边的粒子认鼠标。右边的代理沿着 LangGraph 走：先规划工具，再检索档案，最后成稿。没有模型钥匙时，句子直接从文章里摘。
      </p>
      <div className="lab">
        <div className="stage">
          <Starfield weather={weather} interactive />
          <div className="stage-ui">
            <p>天气</p>
            <div className="tag-row">
              {WEATHERS.map((item) => (
                <button
                  key={item.id}
                  className={item.id === weather ? "chip on" : "chip"}
                  onClick={() => setWeather(item.id)}
                  type="button"
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="chat" id="ask">
          <div className="thread" aria-live="polite">
            {messages.map((message, index) => (
              <article className={`bubble ${message.role}`} key={`${message.role}-${index}`}>
                {message.modeLabel && <p className="meta">{message.modeLabel}</p>}
                <div className="prose tight">{renderMarkdown(message.content)}</div>
                {message.trace && message.trace.length > 0 && (
                  <ol className="trace">
                    {message.trace.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                )}
                {message.sources && message.sources.length > 0 && (
                  <div className="tag-row">
                    {message.sources.slice(0, 4).map((source) => (
                      <Link key={source.slug} className="chip" to={`/essays/${source.slug}`}>
                        {source.title}
                      </Link>
                    ))}
                  </div>
                )}
              </article>
            ))}
            {pending && <p className="meta pending">正在翻档案…</p>}
          </div>
          <div className="tag-row suggest">
            {SUGGESTIONS.map((item) => (
              <button key={item} className="chip" type="button" onClick={() => send(item)}>
                {item}
              </button>
            ))}
          </div>
          <form
            className="composer"
            onSubmit={(event) => {
              event.preventDefault();
              void send(draft);
            }}
          >
            <label className="sr" htmlFor="ask-box">
              问档案员
            </label>
            <textarea
              id="ask-box"
              value={draft}
              placeholder="问一篇文章、一件作品，或这艘船是什么"
              rows={3}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void send(draft);
                }
              }}
            />
            <button className="btn" type="submit" disabled={pending || !draft.trim()}>
              发送
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
