import { Link } from "react-router-dom";
import { Cover } from "../components/Cover";
import { Starfield } from "../components/Starfield";
import { useSite, useTitle } from "../site";

export function Home() {
  const site = useSite();
  useTitle();
  const [lead, ...rest] = site.featured;
  const lane = site.posts.flatMap((post) => post.tags);
  const marquee = [...lane, ...lane];

  return (
    <>
      <section className="hero">
        <Starfield weather="calm" />
        <div className="hero-copy">
          <p className="eyebrow">
            {site.eyebrow}
            <span>LOG {String(site.posts.length).padStart(2, "0")}</span>
          </p>
          <h1>
            <span>不要再</span>
            <span>熬夜了</span>
          </h1>
          <p className="deck">{site.deck}</p>
          <div className="actions">
            <Link className="btn" to="/essays">
              进入航线
            </Link>
            <Link className="btn btn-ghost" to="/lab">
              打开实验室
            </Link>
          </div>
        </div>
        <svg className="flight" viewBox="0 0 640 180" aria-hidden="true">
          <path id="lane" d="M8 130C70 130 90 40 170 48S300 150 390 86 560 20 632 64" />
          <circle className="flight-dot" r="4">
            <animateMotion dur="16s" repeatCount="indefinite">
              <mpath href="#lane" />
            </animateMotion>
          </circle>
        </svg>
      </section>

      <section className="status">
        <p>
          <span>正在写</span>
          {site.now.writing}
        </p>
        <p>
          <span>正在读</span>
          {site.now.reading}
        </p>
        <p>
          <span>时区</span>
          {site.now.zone}
        </p>
      </section>

      <section className="block">
        <div className="section-head">
          <h2>精选</h2>
          <Link to="/essays">全部文章</Link>
        </div>
        {lead && (
          <div className="feature-grid">
            <Link className="feature-main card" to={`/essays/${lead.slug}`}>
              <Cover name={lead.cover} label="01" />
              <div>
                <p className="meta">
                  {lead.date} · {lead.minutes} 分钟
                </p>
                <h3>{lead.title}</h3>
                <p>{lead.summary}</p>
              </div>
            </Link>
            <div className="feature-side">
              {rest.map((post, index) => (
                <Link className="card side-card" to={`/essays/${post.slug}`} key={post.slug}>
                  <p className="meta">0{index + 2}</p>
                  <h3>{post.title}</h3>
                  <p>{post.summary}</p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>

      <div className="marquee" aria-hidden="true">
        <div className="marquee-track">
          {marquee.map((tag, index) => (
            <span key={`${tag}-${index}`}>{tag}</span>
          ))}
        </div>
      </div>

      <section className="block">
        <div className="section-head">
          <h2>能点开的作品</h2>
          <Link to="/works">作品集</Link>
        </div>
        <div className="work-grid">
          {site.works.map((work) => (
            <Link className="card work-card" to={`/works/${work.slug}`} key={work.slug}>
              <Cover name={work.cover} label={work.year} />
              <p className="meta">{work.role}</p>
              <h3>{work.title}</h3>
              <p>{work.summary}</p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
