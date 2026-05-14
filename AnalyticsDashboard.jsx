import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie } from "recharts";

const API_BASE = "https://ai-agent-toolkit-vzj1.onrender.com";

const COLORS = {
  bg: "#0A0A0F",
  surface: "#111118",
  card: "#16161F",
  border: "#1E1E2E",
  accent: "#6C63FF",
  accentSoft: "#6C63FF22",
  green: "#00D48A",
  greenSoft: "#00D48A22",
  orange: "#FF8C42",
  orangeSoft: "#FF8C4222",
  red: "#FF4D6A",
  redSoft: "#FF4D6A22",
  text: "#E8E8F0",
  muted: "#6B6B7E",
  white: "#FFFFFF",
};

const PLAN_COLORS = { starter: "#6C63FF", pro: "#00D48A", enterprise: "#FF8C42" };

function useAnalytics(apiKey) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!apiKey) return;
    setLoading(true);
    Promise.all([
      fetch(`${API_BASE}/api/v1/analytics/dashboard`, { headers: { "X-API-Key": apiKey } }).then(r => r.json()),
      fetch(`${API_BASE}/api/v1/analytics/leads`, { headers: { "X-API-Key": apiKey } }).then(r => r.json()),
      fetch(`${API_BASE}/api/v1/social/stats`, { headers: { "X-API-Key": apiKey } }).then(r => r.json()),
    ])
      .then(([dashboard, leads, social]) => {
        setData({ dashboard, leads, social });
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [apiKey]);

  return { data, loading, error };
}

function MetricCard({ label, value, sub, color, icon }) {
  return (
    <div style={{
      background: COLORS.card,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 16,
      padding: "24px",
      display: "flex",
      flexDirection: "column",
      gap: 8,
      position: "relative",
      overflow: "hidden",
    }}>
      <div style={{
        position: "absolute", top: 0, right: 0, width: 80, height: 80,
        background: `radial-gradient(circle at top right, ${color}22, transparent 70%)`,
        borderRadius: "0 16px 0 0",
      }} />
      <div style={{ fontSize: 22 }}>{icon}</div>
      <div style={{ fontSize: 32, fontWeight: 800, color: COLORS.white, letterSpacing: "-1px" }}>{value}</div>
      <div style={{ fontSize: 13, color: COLORS.muted, fontWeight: 500 }}>{label}</div>
      {sub && <div style={{ fontSize: 12, color, fontWeight: 600 }}>{sub}</div>}
    </div>
  );
}

function SectionTitle({ children }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
      <div style={{ width: 3, height: 18, background: COLORS.accent, borderRadius: 2 }} />
      <span style={{ fontSize: 14, fontWeight: 700, color: COLORS.text, letterSpacing: "0.05em", textTransform: "uppercase" }}>
        {children}
      </span>
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: COLORS.surface, border: `1px solid ${COLORS.border}`,
      borderRadius: 8, padding: "10px 14px", fontSize: 13
    }}>
      <div style={{ color: COLORS.muted, marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 600 }}>
          {p.name}: {p.value}
        </div>
      ))}
    </div>
  );
};

function LoginScreen({ onLogin }) {
  const [key, setKey] = useState("");
  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, display: "flex",
      alignItems: "center", justifyContent: "center", fontFamily: "'DM Sans', sans-serif"
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />
      <div style={{
        background: COLORS.card, border: `1px solid ${COLORS.border}`,
        borderRadius: 20, padding: 48, width: 380, textAlign: "center"
      }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>⚡</div>
        <div style={{ fontSize: 24, fontWeight: 800, color: COLORS.white, marginBottom: 4 }}>NowCustom</div>
        <div style={{ fontSize: 13, color: COLORS.muted, marginBottom: 32 }}>Analytics Dashboard</div>
        <input
          type="password"
          placeholder="Enter your API key..."
          value={key}
          onChange={e => setKey(e.target.value)}
          onKeyDown={e => e.key === "Enter" && key && onLogin(key)}
          style={{
            width: "100%", padding: "12px 16px", background: COLORS.surface,
            border: `1px solid ${COLORS.border}`, borderRadius: 10, color: COLORS.text,
            fontSize: 14, fontFamily: "inherit", boxSizing: "border-box", outline: "none",
            marginBottom: 12
          }}
        />
        <button
          onClick={() => key && onLogin(key)}
          style={{
            width: "100%", padding: "12px 16px", background: COLORS.accent,
            border: "none", borderRadius: 10, color: COLORS.white, fontSize: 14,
            fontWeight: 700, cursor: "pointer", fontFamily: "inherit"
          }}
        >
          Access Dashboard →
        </button>
      </div>
    </div>
  );
}

export default function AnalyticsDashboard() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem("nc_api_key") || "");
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("nc_api_key"));
  const { data, loading, error } = useAnalytics(loggedIn ? apiKey : null);

  const handleLogin = (key) => {
    setApiKey(key);
    localStorage.setItem("nc_api_key", key);
    setLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("nc_api_key");
    setApiKey("");
    setLoggedIn(false);
  };

  if (!loggedIn) return <LoginScreen onLogin={handleLogin} />;

  const dashboard = data?.dashboard;
  const leads = data?.leads;
  const social = data?.social;

  const leadsByState = leads?.por_estado || [];
  const leadsBySource = leads?.por_fuente || [];
  const trendData = dashboard?.tendencia?.leads_por_dia || [];
  const socialStats = dashboard?.social || {};

  const conversionRate = dashboard?.leads?.tasa_conversion || 0;
  const scoreAvg = dashboard?.leads?.score_promedio || 0;

  return (
    <div style={{
      minHeight: "100vh", background: COLORS.bg, fontFamily: "'DM Sans', sans-serif",
      color: COLORS.text, padding: "0"
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{
        padding: "20px 32px", borderBottom: `1px solid ${COLORS.border}`,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: COLORS.surface, position: "sticky", top: 0, zIndex: 10
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 32, height: 32, background: COLORS.accent, borderRadius: 8,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16
          }}>⚡</div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 800, color: COLORS.white }}>NowCustom</div>
            <div style={{ fontSize: 11, color: COLORS.muted }}>Analytics Dashboard</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            padding: "4px 12px", background: COLORS.greenSoft, borderRadius: 20,
            fontSize: 12, color: COLORS.green, fontWeight: 600
          }}>● Live</div>
          <button onClick={handleLogout} style={{
            padding: "8px 16px", background: "transparent", border: `1px solid ${COLORS.border}`,
            borderRadius: 8, color: COLORS.muted, fontSize: 13, cursor: "pointer",
            fontFamily: "inherit"
          }}>Sign out</button>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "32px", maxWidth: 1200, margin: "0 auto" }}>

        {loading && (
          <div style={{ textAlign: "center", padding: 80, color: COLORS.muted }}>
            <div style={{ fontSize: 32, marginBottom: 16 }}>⚡</div>
            Loading analytics...
          </div>
        )}

        {error && (
          <div style={{
            background: COLORS.redSoft, border: `1px solid ${COLORS.red}`,
            borderRadius: 12, padding: 20, color: COLORS.red, marginBottom: 24
          }}>
            ⚠️ API Error: {error}
          </div>
        )}

        {!loading && data && (
          <>
            {/* KPI Row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
              <MetricCard
                label="Total Leads" value={dashboard?.leads?.total ?? 0}
                sub={`+${dashboard?.leads?.nuevos ?? 0} nuevos`}
                color={COLORS.accent} icon="👥"
              />
              <MetricCard
                label="Conversion Rate" value={`${conversionRate}%`}
                sub={`${dashboard?.leads?.convertidos ?? 0} convertidos`}
                color={COLORS.green} icon="🎯"
              />
              <MetricCard
                label="Avg Lead Score" value={scoreAvg}
                sub="de 100 puntos" color={COLORS.orange} icon="⭐"
              />
              <MetricCard
                label="Posts Publicados" value={socialStats?.publicados ?? 0}
                sub={`${socialStats?.programados ?? 0} programados`}
                color={COLORS.accent} icon="📱"
              />
            </div>

            {/* Charts Row */}
            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16, marginBottom: 32 }}>

              {/* Trend chart */}
              <div style={{
                background: COLORS.card, border: `1px solid ${COLORS.border}`,
                borderRadius: 16, padding: 24
              }}>
                <SectionTitle>Leads — Últimos 7 días</SectionTitle>
                {trendData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                      <XAxis dataKey="dia" stroke={COLORS.muted} tick={{ fontSize: 11 }} />
                      <YAxis stroke={COLORS.muted} tick={{ fontSize: 11 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Line
                        type="monotone" dataKey="cantidad" name="Leads"
                        stroke={COLORS.accent} strokeWidth={2.5}
                        dot={{ fill: COLORS.accent, strokeWidth: 0, r: 4 }}
                        activeDot={{ r: 6, fill: COLORS.accent }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{
                    height: 200, display: "flex", alignItems: "center", justifyContent: "center",
                    color: COLORS.muted, fontSize: 13, flexDirection: "column", gap: 8
                  }}>
                    <div style={{ fontSize: 32 }}>📊</div>
                    Sin datos de tendencia aún
                  </div>
                )}
              </div>

              {/* Leads by state */}
              <div style={{
                background: COLORS.card, border: `1px solid ${COLORS.border}`,
                borderRadius: 16, padding: 24
              }}>
                <SectionTitle>Pipeline de Leads</SectionTitle>
                {leadsByState.length > 0 ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {leadsByState.map((item, i) => {
                      const stateColors = {
                        nuevo: COLORS.accent, contactado: COLORS.orange,
                        convertido: COLORS.green, perdido: COLORS.red
                      };
                      const color = stateColors[item.estado] || COLORS.muted;
                      const pct = dashboard?.leads?.total > 0
                        ? Math.round((item.cantidad / dashboard.leads.total) * 100) : 0;
                      return (
                        <div key={i}>
                          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                            <span style={{ fontSize: 12, color: COLORS.text, textTransform: "capitalize" }}>
                              {item.estado}
                            </span>
                            <span style={{ fontSize: 12, color, fontWeight: 700 }}>
                              {item.cantidad} ({pct}%)
                            </span>
                          </div>
                          <div style={{ height: 6, background: COLORS.border, borderRadius: 3 }}>
                            <div style={{
                              height: "100%", width: `${pct}%`, background: color,
                              borderRadius: 3, transition: "width 0.6s ease"
                            }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div style={{
                    height: 150, display: "flex", alignItems: "center", justifyContent: "center",
                    color: COLORS.muted, fontSize: 13, flexDirection: "column", gap: 8
                  }}>
                    <div style={{ fontSize: 32 }}>🎯</div>
                    Sin leads aún
                  </div>
                )}
              </div>
            </div>

            {/* Bottom Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

              {/* Sources */}
              <div style={{
                background: COLORS.card, border: `1px solid ${COLORS.border}`,
                borderRadius: 16, padding: 24
              }}>
                <SectionTitle>Fuentes de Leads</SectionTitle>
                {leadsBySource.length > 0 ? (
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={leadsBySource} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
                      <XAxis type="number" stroke={COLORS.muted} tick={{ fontSize: 11 }} />
                      <YAxis dataKey="fuente" type="category" stroke={COLORS.muted} tick={{ fontSize: 11 }} width={60} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="cantidad" name="Leads" radius={[0, 4, 4, 0]}>
                        {leadsBySource.map((_, i) => (
                          <Cell key={i} fill={[COLORS.accent, COLORS.green, COLORS.orange, COLORS.red][i % 4]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{
                    height: 180, display: "flex", alignItems: "center", justifyContent: "center",
                    color: COLORS.muted, fontSize: 13, flexDirection: "column", gap: 8
                  }}>
                    <div style={{ fontSize: 32 }}>🌐</div>
                    Sin datos de fuentes
                  </div>
                )}
              </div>

              {/* Social + Alerts */}
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

                {/* Social summary */}
                <div style={{
                  background: COLORS.card, border: `1px solid ${COLORS.border}`,
                  borderRadius: 16, padding: 24, flex: 1
                }}>
                  <SectionTitle>Social Media</SectionTitle>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                    {[
                      { label: "Total", value: socialStats?.total ?? 0, color: COLORS.accent },
                      { label: "Publicados", value: socialStats?.publicados ?? 0, color: COLORS.green },
                      { label: "Errores", value: socialStats?.errores ?? 0, color: COLORS.red },
                    ].map((item, i) => (
                      <div key={i} style={{
                        background: COLORS.surface, borderRadius: 10, padding: "12px",
                        textAlign: "center", border: `1px solid ${COLORS.border}`
                      }}>
                        <div style={{ fontSize: 24, fontWeight: 800, color: item.color }}>{item.value}</div>
                        <div style={{ fontSize: 11, color: COLORS.muted, marginTop: 2 }}>{item.label}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Alerts */}
                <div style={{
                  background: COLORS.card, border: `1px solid ${COLORS.border}`,
                  borderRadius: 16, padding: 24, flex: 1
                }}>
                  <SectionTitle>Alertas</SectionTitle>
                  {dashboard?.alertas?.errores_publicacion?.length > 0 ? (
                    dashboard.alertas.errores_publicacion.map((e, i) => (
                      <div key={i} style={{
                        display: "flex", justifyContent: "space-between",
                        padding: "8px 0", borderBottom: `1px solid ${COLORS.border}`
                      }}>
                        <span style={{ fontSize: 13, color: COLORS.text }}>{e.plataforma}</span>
                        <span style={{
                          fontSize: 12, color: COLORS.red, background: COLORS.redSoft,
                          padding: "2px 8px", borderRadius: 20
                        }}>{e.total} errores</span>
                      </div>
                    ))
                  ) : (
                    <div style={{
                      display: "flex", alignItems: "center", gap: 8,
                      color: COLORS.green, fontSize: 13
                    }}>
                      <span>✅</span> Sin alertas activas
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div style={{
              marginTop: 32, textAlign: "center", fontSize: 12, color: COLORS.muted
            }}>
              NowCustom Platform · Datos en tiempo real · {new Date().toLocaleDateString("es", {
                year: "numeric", month: "long", day: "numeric"
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
