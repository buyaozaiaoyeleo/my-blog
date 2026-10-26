import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fetchAdminMe, loginAdmin } from "./api";
import { DEFAULT_ADMIN, getAdminToken } from "./auth";

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState(DEFAULT_ADMIN.username);
  const [password, setPassword] = useState(DEFAULT_ADMIN.password);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    document.title = "管理舱 · 不要再熬夜了";
    if (!getAdminToken()) return;
    fetchAdminMe().then((me) => {
      if (me) navigate("/admin/desk", { replace: true });
    });
  }, [navigate]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await loginAdmin(username.trim(), password);
      navigate("/admin/desk", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="admin-shell">
      <div className="admin-glow" />
      <main className="admin-login">
        <p className="eyebrow">
          <span>Admin Hatch</span>
          <Link to="/">返回驾驶舱</Link>
        </p>
        <h1>管理舱</h1>
        <p className="deck narrow">
          前台不挂入口。只有知道这条暗道的人才能改界面文案与文章档案。账号已预填，确认后进入。
        </p>
        <form className="admin-form" onSubmit={onSubmit}>
          <label>
            <span>账号</span>
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>
          <label>
            <span>密码</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="admin-error">{error}</p>}
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "开门中…" : "进入管理舱"}
          </button>
        </form>
      </main>
    </div>
  );
}
