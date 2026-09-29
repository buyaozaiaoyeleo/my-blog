import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPost } from "../api";
import { Cover } from "../components/Cover";
import { renderMarkdown, splitStory } from "../markdown";
import { useSite, useTitle } from "../site";
import type { PostFull } from "../types";

export function Essay() {
  const { slug = "" } = useParams();
  const site = useSite();
  const [post, setPost] = useState<PostFull | null>(null);
  const [error, setError] = useState<string | null>(null);
  useTitle(post?.title);

  useEffect(() => {
    let cancelled = false;
    setPost(null);
    setError(null);
    fetchPost(slug)
      .then((next) => {
        if (!cancelled) setPost(next);
      })
      .catch((reason: Error) => {
        if (!cancelled) setError(reason.message === "missing" ? "missing" : "fail");
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (error === "missing") {
    return (
      <section className="boot">
        <h1>这篇文章不在船上</h1>
        <Link className="btn" to="/essays">
          回到航线
        </Link>
      </section>
    );
  }
  if (error) {
    return (
      <section className="boot">
        <h1>文章没有打开</h1>
        <p>档案这一跳失败了。</p>
      </section>
    );
  }
  if (!post) {
    return (
      <section className="boot">
        <h1>翻开档案</h1>
      </section>
    );
  }

  const ordered = site.posts;
  const index = ordered.findIndex((item) => item.slug === post.slug);
  const next = ordered[index + 1] ?? ordered[0];
  const related = ordered.filter((item) => item.slug !== post.slug && item.tags.some((tag) => post.tags.includes(tag))).slice(0, 2);
  const story = post.kind === "story" ? splitStory(post.body) : null;

  return (
    <article className="article">
      <p className="eyebrow">{post.tags.join(" / ")}</p>
      <h1>{post.title}</h1>
      <p className="meta">
        {post.date} · {post.minutes} 分钟 · {post.kind === "story" ? "滚动叙事" : "笔记"}
      </p>
      <p className="deck">{post.summary}</p>
      <Cover name={post.cover} label={post.date.slice(0, 4)} />
      {story ? (
        <>
          {story.lede && <div className="prose lede">{renderMarkdown(story.lede)}</div>}
          {story.sections.map((section, sectionIndex) => (
            <section className="beat" key={section.title}>
              <div className="beat-index">{String(sectionIndex + 1).padStart(2, "0")}</div>
              <h2>{section.title}</h2>
              <div className="prose">{renderMarkdown(section.body)}</div>
            </section>
          ))}
        </>
      ) : (
        <div className="prose">{renderMarkdown(post.body)}</div>
      )}
      {related.length > 0 && (
        <aside className="related">
          <h2>相邻的航线</h2>
          {related.map((item) => (
            <Link key={item.slug} to={`/essays/${item.slug}`}>
              {item.title}
            </Link>
          ))}
        </aside>
      )}
      {next && next.slug !== post.slug && (
        <Link className="next-link" to={`/essays/${next.slug}`}>
          <span>下一篇</span>
          {next.title}
        </Link>
      )}
    </article>
  );
}
