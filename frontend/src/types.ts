export type Post = {
  slug: string;
  title: string;
  date: string;
  tags: string[];
  minutes: number;
  featured: boolean;
  cover: string;
  summary: string;
  kind: "essay" | "story" | string;
};

export type PostFull = Post & { body: string };

export type Work = {
  slug: string;
  title: string;
  year: string;
  role: string;
  cover: string;
  href: string;
  summary: string;
  points: string[];
  result: string;
};

export type TimelineItem = {
  year: string;
  title: string;
  text: string;
};

export type Site = {
  name: string;
  mark: string;
  eyebrow: string;
  deck: string;
  now: { writing: string; reading: string; zone: string };
  about: {
    lede: string;
    paragraphs: string[];
    timeline: TimelineItem[];
    tools: string[];
  };
  posts: Post[];
  featured: Post[];
  works: Work[];
};

export type Source = { slug: string; title: string };

export type ChatResult = {
  reply: string;
  sources: Source[];
  trace: string[];
  mode: string;
  mode_label: string;
};
