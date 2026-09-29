import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useSiteState } from "../site";

function formatClock() {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "Asia/Shanghai",
  }).format(new Date());
}

export function Shell() {
  const { site, error } = useSiteState();
  const location = useLocation();
  const [clock, setClock] = useState(formatClock);

  useEffect(() => {
    const id = window.setInterval(() => setClock(formatClock()), 30000);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  useEffect(() => {
    const onScroll = () => {
      const root = document.documentElement;
      const max = root.scrollHeight - root.clientHeight;
      const progress = max > 0 ? root.scrollTop / max : 0;
      root.style.setProperty("--progress", String(progress));
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [location.pathname]);

  useEffect(() => {
    const onMove = (event: PointerEvent) => {
      document.documentElement.style.setProperty("--mx", `${event.clientX}px`);
      document.documentElement.style.setProperty("--my", `${event.clientY}px`);
    };
    window.addEventListener("pointermove", onMove);
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  return (
    <div className="shell">
      <div className="progress" />
      <div className="glow" />
      <div className="grain" />
      <header className="nav">
        <NavLink to="/" className="brand" end>
          <i />
          夜航
        </NavLink>
        <nav>
          <NavLink to="/essays">文章</NavLink>
          <NavLink to="/works">作品</NavLink>
          <NavLink to="/about">关于</NavLink>
          <NavLink to="/lab">实验室</NavLink>
        </nav>
        <span className="clock">{clock}</span>
      </header>
      <main className="page">
        {error && (
          <section className="boot">
            <p className="eyebrow">Night Passage</p>
            <h1>仪表离线</h1>
            <p>{error}</p>
          </section>
        )}
        {!error && !site && (
          <section className="boot">
            <p className="eyebrow">Night Passage</p>
            <h1>校准仪表</h1>
            <p>正在把航线从档案里取出来。</p>
          </section>
        )}
        {site && <Outlet />}
      </main>
      <footer className="colophon">
        <span>不要再熬夜了</span>
        <span>React · LangGraph · LangChain</span>
        <a href="/feed.xml">RSS</a>
      </footer>
    </div>
  );
}
