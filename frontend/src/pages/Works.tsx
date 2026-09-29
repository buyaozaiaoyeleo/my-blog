import { Link } from "react-router-dom";
import { Cover } from "../components/Cover";
import { useSite, useTitle } from "../site";

export function Works() {
  const site = useSite();
  useTitle("作品");
  return (
    <section className="block">
      <p className="eyebrow">Works</p>
      <h1>能点开的四件</h1>
      <p className="deck narrow">每件都有问题、做法和一句结果。海报不上船。</p>
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
  );
}
