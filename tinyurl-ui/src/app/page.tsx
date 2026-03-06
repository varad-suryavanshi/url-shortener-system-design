"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "../../lib/api";

type LoginResp = { access_token: string; token_type: string };

type UrlItem = {
  _id: string;
  original_url: string;
  short_code: string;
  created_at: string;
  click_count: number;
  last_clicked_at?: string | null;
  user_id?: string;
};

export default function Home() {
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("pass1234");
  const [token, setToken] = useState<string | null>(null);

  const [originalUrl, setOriginalUrl] = useState("https://nyu.edu");
  const [custom, setCustom] = useState("varad123");

  const [myUrls, setMyUrls] = useState<UrlItem[]>([]);
  const [topUrls, setTopUrls] = useState<UrlItem[]>([]);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    const t = localStorage.getItem("token");
    setToken(t);
  }, []);

  const loggedIn = useMemo(() => Boolean(token), [token]);

  async function register() {
    setStatus("Registering...");
    try {
      await api.post("/auth/register", { email, password });
      setStatus("Registered ✅ Now login.");
    } catch (e: any) {
      setStatus(e?.response?.data?.detail ? `Error: ${e.response.data.detail}` : "Register failed");
    }
  }

  async function login() {
    setStatus("Logging in...");
    try {
      const res = await api.post<LoginResp>("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      setToken(res.data.access_token);
      setStatus("Logged in ✅");
    } catch (e: any) {
      setStatus(e?.response?.data?.detail ? `Error: ${e.response.data.detail}` : "Login failed");
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setMyUrls([]);
    setTopUrls([]);
    setStatus("Logged out");
  }

  async function createUrl() {
    setStatus("Creating short URL...");
    try {
      const q = custom?.trim() ? `?custom=${encodeURIComponent(custom.trim())}` : "";
      const res = await api.post(`/me/shorten${q}`, { original_url: originalUrl });
      setStatus(`Created ✅ ${res.data.short_url}`);
      await refresh();
    } catch (e: any) {
      setStatus(e?.response?.data?.detail ? `Error: ${e.response.data.detail}` : "Create failed");
    }
  }

  async function refresh() {
    if (!loggedIn) return;
    setStatus("Refreshing...");
    try {
      const [urlsRes, topRes] = await Promise.all([
        api.get<{ items: UrlItem[] }>("/me/urls"),
        api.get<{ items: UrlItem[] }>("/me/top?limit=10"),
      ]);
      setMyUrls(urlsRes.data.items);
      setTopUrls(topRes.data.items);
      setStatus("Up to date ✅");
    } catch (e: any) {
      setStatus(e?.response?.data?.detail ? `Error: ${e.response.data.detail}` : "Refresh failed");
    }
  }

  useEffect(() => {
    if (loggedIn) refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loggedIn]);

  return (
    <main style={{ maxWidth: 900, margin: "40px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1 style={{ fontSize: 28, marginBottom: 8 }}>TinyURL Clone UI</h1>
      <p style={{ marginTop: 0, opacity: 0.75 }}>Backend: FastAPI + MongoDB + JWT</p>

      <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12, marginBottom: 16 }}>
        <h2 style={{ fontSize: 18, marginTop: 0 }}>Auth</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email"
            style={{ padding: 10, width: 260 }}
          />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="password"
            type="password"
            style={{ padding: 10, width: 260 }}
          />
          <button onClick={register} style={{ padding: "10px 14px" }}>Register</button>
          <button onClick={login} style={{ padding: "10px 14px" }}>Login</button>
          <button onClick={logout} style={{ padding: "10px 14px" }} disabled={!loggedIn}>Logout</button>
          <button onClick={refresh} style={{ padding: "10px 14px" }} disabled={!loggedIn}>Refresh</button>
        </div>
        <div style={{ marginTop: 10, fontSize: 14 }}>
          <strong>Status:</strong> {status}
        </div>
      </div>

      <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12, marginBottom: 16 }}>
        <h2 style={{ fontSize: 18, marginTop: 0 }}>Create URL (authenticated)</h2>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            value={originalUrl}
            onChange={(e) => setOriginalUrl(e.target.value)}
            placeholder="https://example.com"
            style={{ padding: 10, width: 420 }}
            disabled={!loggedIn}
          />
          <input
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
            placeholder="custom code (optional)"
            style={{ padding: 10, width: 220 }}
            disabled={!loggedIn}
          />
          <button onClick={createUrl} style={{ padding: "10px 14px" }} disabled={!loggedIn}>
            Shorten
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <section style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
          <h2 style={{ fontSize: 18, marginTop: 0 }}>My URLs</h2>
          <UrlTable items={myUrls} />
        </section>

        <section style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
          <h2 style={{ fontSize: 18, marginTop: 0 }}>Top URLs</h2>
          <UrlTable items={topUrls} />
        </section>
      </div>
    </main>
  );
}

function UrlTable({ items }: { items: UrlItem[] }) {
  if (!items.length) return <p style={{ opacity: 0.7 }}>No items yet.</p>;

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
      <thead>
        <tr style={{ textAlign: "left" }}>
          <th style={{ borderBottom: "1px solid #eee", padding: "8px 6px" }}>Code</th>
          <th style={{ borderBottom: "1px solid #eee", padding: "8px 6px" }}>Clicks</th>
          <th style={{ borderBottom: "1px solid #eee", padding: "8px 6px" }}>Last</th>
        </tr>
      </thead>
      <tbody>
        {items.map((u) => (
          <tr key={u._id}>
            <td style={{ borderBottom: "1px solid #f3f3f3", padding: "8px 6px" }}>
              <a href={`http://127.0.0.1:8000/r/${u.short_code}`} target="_blank" rel="noreferrer">
                {u.short_code}
              </a>
              <div style={{ opacity: 0.7, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 360 }}>
                {u.original_url}
              </div>
            </td>
            <td style={{ borderBottom: "1px solid #f3f3f3", padding: "8px 6px" }}>{u.click_count}</td>
            <td style={{ borderBottom: "1px solid #f3f3f3", padding: "8px 6px" }}>
              {u.last_clicked_at ? new Date(u.last_clicked_at).toLocaleString() : "—"}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}