import { useEffect, useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import type { PostFull } from "../types";
import {
  deleteAdminPost,
  fetchAdminMe,
  fetchAdminPosts,
  fetchAdminSite,
  logoutAdmin,
  saveAdminPost,
  saveAdminSite,
  type AdminSite,
} from "./api";
import { getAdminToken } from "./auth";

type Tab = "site" | "now" | "about" | "works" | "posts";

const emptyPost = (): PostFull => ({
  slug: "",
  title: "",
  date: new Date().toISOString().slice(0, 10),
  tags: [],
  minutes: 5,
  featured: false,
  cover: "amber",
  summary: "",
  kind: "essay",
  body: "",
});

export function AdminDesk() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [tab, setTab] = useState<Tab>("site");
  const [site, setSite] = useState<AdminSite | null>(null);
  const [posts, setPosts] = useState<PostFull[]>([]);
  const [draft, setDraft] = useState<PostFull | null>(null);
  const [editingSlug, setEditingSlug] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    document.title = "管理舱 · 不要再熬夜了";
    const token = getAdminToken();
    if (!token) {
      setReady(true);
      setAuthed(false);
      return;
    }
    Promise.all([fetchAdminMe(), fetchAdminSite(), fetchAdminPosts()])
      .then(([me, siteData, postData]) => {
        if (!me) {
          setAuthed(false);
          return;
        }
        setAuthed(true);
        setSite(siteData);
        setPosts(postData);
      })
      .catch(() => setAuthed(false))
      .finally(() => setReady(true));
  }, []);

  function flash(ok: string) {
    setMessage(ok);
    setError(null);
  }

  function fail(err: unknown) {
    setError(err instanceof Error ? err.message : "操作失败");
    setMessage(null);
  }

  async function persistSite(next: AdminSite) {
    setBusy(true);
    try {
      const saved = await saveAdminSite(next);
      setSite(saved);
      flash("站点内容已写入。前台刷新即可看见。");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onSaveSite(event: FormEvent) {
    event.preventDefault();
    if (!site) return;
    await persistSite(site);
  }

  async function onSavePost(event: FormEvent) {
    event.preventDefault();
    if (!draft) return;
    setBusy(true);
    try {
      const saved = await saveAdminPost(draft, editingSlug ?? undefined);
      const next = await fetchAdminPosts();
      setPosts(next);
      setDraft(null);
      setEditingSlug(null);
      flash(`文章「${saved.title}」已保存。`);
      setTab("posts");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function onDeletePost(slug: string) {
    if (!window.confirm(`确定删除「${slug}」？`)) return;
    setBusy(true);
    try {
      await deleteAdminPost(slug);
      setPosts(await fetchAdminPosts());
      if (editingSlug === slug) {
        setDraft(null);
        setEditingSlug(null);
      }
      flash("文章已删除。");
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    logoutAdmin();
    navigate("/admin", { replace: true });
  }

  if (!ready) {
    return (
      <div className="admin-shell">
        <main className="admin-login">
          <p className="eyebrow">Admin Hatch</p>
          <h1>校准管理舱</h1>
        </main>
      </div>
    );
  }

  if (!authed || !site) {
    return <Navigate to="/admin" replace />;
  }

  return (
    <div className="admin-shell">
      <div className="admin-glow" />
      <header className="admin-nav">
        <div>
          <p className="eyebrow">Admin Desk</p>
          <strong>管理舱 · {site.mark}</strong>
        </div>
        <div className="admin-nav-actions">
          <Link className="btn-ghost" to="/">
            看前台
          </Link>
          <button className="btn-ghost" type="button" onClick={logout}>
            退出
          </button>
        </div>
      </header>

      <nav className="admin-tabs">
        {(
          [
            ["site", "船名与主张"],
            ["now", "近况"],
            ["about", "关于"],
            ["works", "作品"],
            ["posts", "文章"],
          ] as [Tab, string][]
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "chip on" : "chip"}
            onClick={() => {
              setTab(id);
              setDraft(null);
              setEditingSlug(null);
            }}
          >
            {label}
          </button>
        ))}
      </nav>

      {(message || error) && (
        <p className={error ? "admin-error" : "admin-ok"}>{error || message}</p>
      )}

      <main className="admin-panel">
        {tab === "site" && (
          <form className="admin-form" onSubmit={onSaveSite}>
            <label>
              <span>站点名</span>
              <input
                value={site.name}
                onChange={(event) => setSite({ ...site, name: event.target.value })}
              />
            </label>
            <label>
              <span>船徽</span>
              <input
                value={site.mark}
                onChange={(event) => setSite({ ...site, mark: event.target.value })}
              />
            </label>
            <label>
              <span>眉题</span>
              <input
                value={site.eyebrow}
                onChange={(event) => setSite({ ...site, eyebrow: event.target.value })}
              />
            </label>
            <label>
              <span>主张 / 甲板说明</span>
              <textarea
                rows={4}
                value={site.deck}
                onChange={(event) => setSite({ ...site, deck: event.target.value })}
              />
            </label>
            <button className="btn" type="submit" disabled={busy}>
              保存船名
            </button>
          </form>
        )}

        {tab === "now" && (
          <form className="admin-form" onSubmit={onSaveSite}>
            <label>
              <span>正在写</span>
              <input
                value={site.now.writing}
                onChange={(event) =>
                  setSite({ ...site, now: { ...site.now, writing: event.target.value } })
                }
              />
            </label>
            <label>
              <span>正在读</span>
              <input
                value={site.now.reading}
                onChange={(event) =>
                  setSite({ ...site, now: { ...site.now, reading: event.target.value } })
                }
              />
            </label>
            <label>
              <span>时区</span>
              <input
                value={site.now.zone}
                onChange={(event) =>
                  setSite({ ...site, now: { ...site.now, zone: event.target.value } })
                }
              />
            </label>
            <button className="btn" type="submit" disabled={busy}>
              保存近况
            </button>
          </form>
        )}

        {tab === "about" && (
          <form className="admin-form" onSubmit={onSaveSite}>
            <label>
              <span>导语</span>
              <textarea
                rows={3}
                value={site.about.lede}
                onChange={(event) =>
                  setSite({
                    ...site,
                    about: { ...site.about, lede: event.target.value },
                  })
                }
              />
            </label>
            <label>
              <span>段落（每行一段）</span>
              <textarea
                rows={8}
                value={site.about.paragraphs.join("\n\n")}
                onChange={(event) =>
                  setSite({
                    ...site,
                    about: {
                      ...site.about,
                      paragraphs: event.target.value
                        .split(/\n\s*\n/)
                        .map((item) => item.trim())
                        .filter(Boolean),
                    },
                  })
                }
              />
            </label>
            <label>
              <span>工具栈（逗号分隔）</span>
              <input
                value={site.about.tools.join(", ")}
                onChange={(event) =>
                  setSite({
                    ...site,
                    about: {
                      ...site.about,
                      tools: event.target.value
                        .split(/[,，]/)
                        .map((item) => item.trim())
                        .filter(Boolean),
                    },
                  })
                }
              />
            </label>
            <label>
              <span>时间线（JSON）</span>
              <textarea
                rows={10}
                value={JSON.stringify(site.about.timeline, null, 2)}
                onChange={(event) => {
                  try {
                    const timeline = JSON.parse(event.target.value);
                    setSite({
                      ...site,
                      about: { ...site.about, timeline },
                    });
                    setError(null);
                  } catch {
                    setError("时间线 JSON 暂时不合法，改完再保存。");
                  }
                }}
              />
            </label>
            <button className="btn" type="submit" disabled={busy}>
              保存关于
            </button>
          </form>
        )}

        {tab === "works" && (
          <form className="admin-form" onSubmit={onSaveSite}>
            <label>
              <span>作品列表（JSON）</span>
              <textarea
                rows={18}
                value={JSON.stringify(site.works, null, 2)}
                onChange={(event) => {
                  try {
                    const works = JSON.parse(event.target.value);
                    setSite({ ...site, works });
                    setError(null);
                  } catch {
                    setError("作品 JSON 暂时不合法，改完再保存。");
                  }
                }}
              />
            </label>
            <button className="btn" type="submit" disabled={busy}>
              保存作品
            </button>
          </form>
        )}

        {tab === "posts" && !draft && (
          <section className="admin-posts">
            <div className="admin-posts-head">
              <h2>文章档案</h2>
              <button
                className="btn"
                type="button"
                onClick={() => {
                  setEditingSlug(null);
                  setDraft({ ...emptyPost(), tags: [] });
                }}
              >
                新建文章
              </button>
            </div>
            <ul className="admin-post-list">
              {posts.map((post) => (
                <li key={post.slug}>
                  <div>
                    <strong>{post.title}</strong>
                    <span>
                      {post.date} · {post.slug}
                      {post.featured ? " · 精选" : ""}
                    </span>
                  </div>
                  <div className="admin-row-actions">
                    <button
                      className="btn-ghost"
                      type="button"
                      onClick={() => {
                        setEditingSlug(post.slug);
                        setDraft({ ...post });
                      }}
                    >
                      编辑
                    </button>
                    <button
                      className="btn-ghost"
                      type="button"
                      onClick={() => onDeletePost(post.slug)}
                      disabled={busy}
                    >
                      删除
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}

        {tab === "posts" && draft && (
          <form className="admin-form" onSubmit={onSavePost}>
            <div className="admin-posts-head">
              <h2>{editingSlug ? "编辑文章" : "新建文章"}</h2>
              <button
                className="btn-ghost"
                type="button"
                onClick={() => {
                  setDraft(null);
                  setEditingSlug(null);
                }}
              >
                返回列表
              </button>
            </div>
            <label>
              <span>标题</span>
              <input
                value={draft.title}
                onChange={(event) => setDraft({ ...draft, title: event.target.value })}
                required
              />
            </label>
            <label>
              <span>slug</span>
              <input
                value={draft.slug}
                onChange={(event) => setDraft({ ...draft, slug: event.target.value })}
                required
              />
            </label>
            <div className="admin-grid-2">
              <label>
                <span>日期</span>
                <input
                  value={draft.date}
                  onChange={(event) => setDraft({ ...draft, date: event.target.value })}
                  required
                />
              </label>
              <label>
                <span>阅读分钟</span>
                <input
                  type="number"
                  min={1}
                  value={draft.minutes}
                  onChange={(event) =>
                    setDraft({ ...draft, minutes: Number(event.target.value) || 5 })
                  }
                />
              </label>
            </div>
            <div className="admin-grid-2">
              <label>
                <span>封面</span>
                <input
                  value={draft.cover}
                  onChange={(event) => setDraft({ ...draft, cover: event.target.value })}
                />
              </label>
              <label>
                <span>类型</span>
                <input
                  value={draft.kind}
                  onChange={(event) => setDraft({ ...draft, kind: event.target.value })}
                />
              </label>
            </div>
            <label>
              <span>标签（逗号分隔）</span>
              <input
                value={draft.tags.join(", ")}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    tags: event.target.value
                      .split(/[,，]/)
                      .map((item) => item.trim())
                      .filter(Boolean),
                  })
                }
              />
            </label>
            <label className="admin-check">
              <input
                type="checkbox"
                checked={draft.featured}
                onChange={(event) => setDraft({ ...draft, featured: event.target.checked })}
              />
              <span>精选到首页</span>
            </label>
            <label>
              <span>摘要</span>
              <textarea
                rows={3}
                value={draft.summary}
                onChange={(event) => setDraft({ ...draft, summary: event.target.value })}
              />
            </label>
            <label>
              <span>正文 Markdown</span>
              <textarea
                rows={16}
                value={draft.body}
                onChange={(event) => setDraft({ ...draft, body: event.target.value })}
              />
            </label>
            <button className="btn" type="submit" disabled={busy}>
              {busy ? "写入中…" : "保存文章"}
            </button>
          </form>
        )}
      </main>
    </div>
  );
}
