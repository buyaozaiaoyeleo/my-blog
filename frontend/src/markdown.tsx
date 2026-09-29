import type { ReactNode } from "react";

function inline(text: string, keyPrefix: string): ReactNode[] {
  const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;
  const nodes: ReactNode[] = [];
  let last = 0;
  let match: RegExpExecArray | null;
  let index = 0;
  while ((match = pattern.exec(text))) {
    if (match.index > last) {
      nodes.push(text.slice(last, match.index));
    }
    const token = match[0];
    const key = `${keyPrefix}-${index++}`;
    if (token.startsWith("**")) {
      nodes.push(<strong key={key}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("[")) {
      const parsed = /\[([^\]]+)\]\(([^)]+)\)/.exec(token);
      const label = parsed?.[1] ?? token;
      const href = parsed?.[2] ?? "#";
      const safe = /^(https?:|mailto:|\/)/.test(href);
      nodes.push(
        safe ? (
          <a key={key} href={href}>
            {label}
          </a>
        ) : (
          <span key={key}>{label}</span>
        ),
      );
    } else {
      nodes.push(<em key={key}>{token.slice(1, -1)}</em>);
    }
    last = match.index + token.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

function paragraph(text: string, key: string) {
  const lines = text.split("\n");
  return (
    <p key={key}>
      {lines.map((line, index) => (
        <span key={`${key}-l${index}`}>
          {index > 0 && <br />}
          {inline(line, `${key}-i${index}`)}
        </span>
      ))}
    </p>
  );
}

export function renderMarkdown(source: string): ReactNode[] {
  const normalized = source.replace(/\r\n/g, "\n").trim();
  if (!normalized) return [];
  const chunks = normalized.split(/```/);
  const blocks: ReactNode[] = [];
  chunks.forEach((chunk, chunkIndex) => {
    if (chunkIndex % 2 === 1) {
      const code = chunk.replace(/^\w+\n/, "");
      blocks.push(
        <pre key={`code-${chunkIndex}`}>
          <code>{code.replace(/\n$/, "")}</code>
        </pre>,
      );
      return;
    }
    const parts = chunk.split(/\n{2,}/);
    parts.forEach((part, partIndex) => {
      const text = part.trim();
      if (!text) return;
      const key = `b-${chunkIndex}-${partIndex}`;
      const lines = text.split("\n");
      if (lines.every((line) => line.trim() === "---")) {
        blocks.push(<hr key={key} />);
        return;
      }
      if (lines.every((line) => /^>\s?/.test(line))) {
        const quote = lines.map((line) => line.replace(/^>\s?/, "")).join("\n");
        blocks.push(<blockquote key={key}>{inline(quote, key)}</blockquote>);
        return;
      }
      if (lines.every((line) => /^-\s+/.test(line))) {
        blocks.push(
          <ul key={key}>
            {lines.map((line, lineIndex) => (
              <li key={`${key}-${lineIndex}`}>{inline(line.replace(/^-+\s+/, ""), `${key}-${lineIndex}`)}</li>
            ))}
          </ul>,
        );
        return;
      }
      const heading = /^(#{1,3})\s+(.*)$/.exec(lines[0]);
      if (heading && lines.length === 1) {
        const level = heading[1].length;
        const content = inline(heading[2], key);
        if (level === 1) blocks.push(<h2 key={key}>{content}</h2>);
        else if (level === 2) blocks.push(<h3 key={key}>{content}</h3>);
        else blocks.push(<h4 key={key}>{content}</h4>);
        return;
      }
      blocks.push(paragraph(text, key));
    });
  });
  return blocks;
}

export function splitStory(body: string): { lede: string; sections: { title: string; body: string }[] } {
  const chunks = body.split(/^## /m);
  const lede = chunks[0]?.trim() ?? "";
  const sections = chunks.slice(1).map((chunk) => {
    const [titleLine, ...rest] = chunk.split("\n");
    return { title: titleLine.trim(), body: rest.join("\n").trim() };
  });
  return { lede, sections };
}
