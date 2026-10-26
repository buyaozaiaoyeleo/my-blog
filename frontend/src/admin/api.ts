import type { PostFull, Site } from "../types";
import { adminFetch, clearAdminToken, setAdminToken } from "./auth";

export type AdminSite = Omit<Site, "posts" | "featured">;

export async function loginAdmin(username: string, password: string) {
  const response = await fetch("/api/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || "登录失败");
  }
  const data = (await response.json()) as { token: string; username: string };
  setAdminToken(data.token);
  return data;
}

export async function fetchAdminMe() {
  const response = await adminFetch("/api/admin/me");
  if (!response.ok) return null;
  return (await response.json()) as { username: string };
}

export async function fetchAdminSite(): Promise<AdminSite> {
  const response = await adminFetch("/api/admin/site");
  if (!response.ok) throw new Error("读不到站点配置");
  return response.json();
}

export async function saveAdminSite(site: AdminSite): Promise<AdminSite> {
  const response = await adminFetch("/api/admin/site", {
    method: "PUT",
    body: JSON.stringify(site),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || "保存站点失败");
  }
  return response.json();
}

export async function fetchAdminPosts(): Promise<PostFull[]> {
  const response = await adminFetch("/api/admin/posts");
  if (!response.ok) throw new Error("读不到文章列表");
  return response.json();
}

export async function saveAdminPost(post: PostFull, previousSlug?: string): Promise<PostFull> {
  const path = previousSlug ? `/api/admin/posts/${previousSlug}` : "/api/admin/posts";
  const response = await adminFetch(path, {
    method: previousSlug ? "PUT" : "POST",
    body: JSON.stringify(post),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.detail || "保存文章失败");
  }
  return response.json();
}

export async function deleteAdminPost(slug: string) {
  const response = await adminFetch(`/api/admin/posts/${slug}`, { method: "DELETE" });
  if (!response.ok) throw new Error("删除失败");
}

export function logoutAdmin() {
  clearAdminToken();
}
