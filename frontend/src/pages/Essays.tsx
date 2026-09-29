import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useSite, useTitle } from "../site";

export function Essays() {
  const site = useSite();
  useTitle("文章");
  const tags = useMemo(() => ["全部", ...Array.from(new Set(site.posts.flatMap((post) => post.tags)))], [site.posts]);
  const [active, setActive] = useState("全部");
  const posts = site.posts.filter((post) => active === "全部" || post.tags.includes(active));

  return (
    <section className="block archive">
      <p className="eyebrow">Archive</p>
      <h1>航线</h1>
      <p className="deck narrow">八篇已经写完的笔记。精选留在首页，这里按时间全部摊开。</p>
      <div className="tag-row">
        {tags.map((tag) => (
          <button key={tag} className={tag === active ? "chip on" : "chip"} onClick={() => setActive(tag)} type="button">
            {tag}
          </button>
        ))}
      </div>
      <ol className="essay-list">
        {posts.map((post, index) => (
          <li key={post.slug}>
            <Link to={`/essays/${post.slug}`}>
              <span className="index">{String(index + 1).padStart(2, "0")}</span>
              <span>
                <strong>{post.title}</strong>
                <em>{post.summary}</em>
              </span>
              <span className="meta">
                {post.date}
                <br />
                {post.minutes} 分钟
              </span>
            </Link>
          </li>
        ))}
      </ol>
      {posts.length === 0 && <p>这个标签下还没有文章。</p>}
    </section>
  );
}
