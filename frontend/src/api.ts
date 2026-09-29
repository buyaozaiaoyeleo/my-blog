import type { ChatResult, PostFull, Site } from "./types";

export async function fetchSite(): Promise<Site> {
  const response = await fetch("/api/site");
  if (!response.ok) throw new Error("站点没有应答");
  return response.json();
}

export async function fetchPost(slug: string): Promise<PostFull> {
  const response = await fetch(`/api/posts/${slug}`);
  if (response.status === 404) throw new Error("missing");
  if (!response.ok) throw new Error("文章没有打开");
  return response.json();
}

export async function askArchive(
  message: string,
  history: { role: string; content: string }[],
): Promise<ChatResult> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!response.ok) throw new Error("档案员没有应答");
  return response.json();
}
