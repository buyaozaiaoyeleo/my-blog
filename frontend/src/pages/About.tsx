import { useSite, useTitle } from "../site";

export function About() {
  const site = useSite();
  useTitle("关于");
  return (
    <section className="block about">
      <p className="eyebrow">About</p>
      <h1>{site.name}</h1>
      <p className="deck narrow">{site.about.lede}</p>
      <div className="prose about-copy">
        {site.about.paragraphs.map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </div>
      <ol className="timeline">
        {site.about.timeline.map((item) => (
          <li key={item.year}>
            <span>{item.year}</span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.text}</p>
            </div>
          </li>
        ))}
      </ol>
      <ul className="tool-row">
        {site.about.tools.map((tool) => (
          <li key={tool}>{tool}</li>
        ))}
      </ul>
    </section>
  );
}
