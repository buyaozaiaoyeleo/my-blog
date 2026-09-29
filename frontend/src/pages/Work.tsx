import { Link, useParams } from "react-router-dom";
import { Cover } from "../components/Cover";
import { useSite, useTitle } from "../site";

export function Work() {
  const { slug = "" } = useParams();
  const site = useSite();
  const work = site.works.find((item) => item.slug === slug);
  useTitle(work?.title ?? "作品");

  if (!work) {
    return (
      <section className="boot">
        <h1>这件作品不在船上</h1>
        <Link className="btn" to="/works">
          回到作品
        </Link>
      </section>
    );
  }

  return (
    <article className="article">
      <p className="eyebrow">{work.role}</p>
      <h1>{work.title}</h1>
      <p className="meta">{work.year}</p>
      <p className="deck">{work.summary}</p>
      <Cover name={work.cover} label={work.year} />
      <ol className="steps">
        {work.points.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ol>
      <p className="result">
        <span>结果</span>
        {work.result}
      </p>
      <Link className="btn" to={work.href}>
        点开它
      </Link>
    </article>
  );
}
