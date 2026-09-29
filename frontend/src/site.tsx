import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { fetchSite } from "./api";
import type { Site } from "./types";

type SiteState = {
  site: Site | null;
  error: string | null;
};

const SiteContext = createContext<SiteState | null>(null);

export function SiteProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SiteState>({ site: null, error: null });

  useEffect(() => {
    let cancelled = false;
    fetchSite()
      .then((site) => {
        if (!cancelled) setState({ site, error: null });
      })
      .catch(() => {
        if (!cancelled) setState({ site: null, error: "仪表没有连上档案。先把接口开在 8000 端口。" });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return <SiteContext.Provider value={state}>{children}</SiteContext.Provider>;
}

export function useSiteState() {
  const value = useContext(SiteContext);
  if (!value) throw new Error("站点还没有装上");
  return value;
}

export function useSite() {
  const { site } = useSiteState();
  if (!site) throw new Error("站点还在校准");
  return site;
}

export function useTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} · 不要再熬夜了` : "不要再熬夜了";
  }, [title]);
}
