// [DEV1] DashboardPage.tsx — shared dashboard. Dev2: add your widgets inside the card below the insight panels.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ensureSession, getProfile } from "../lib/api";

export function DashboardPage() {
  const [sessionId, setSessionId] = useState<string>("");
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    async function load() {
      const sid = await ensureSession();
      setSessionId(sid);
      const user = await getProfile();
      setProfile(user.profile);
    }

    void load();
  }, []);

  const safeProfile = profile || {};
  const fields = [
    { label: "Age", value: safeProfile.age },
    { label: "Monthly Income", value: safeProfile.income ? `INR ${Number(safeProfile.income).toLocaleString("en-IN")}` : null },
    { label: "Monthly Expenses", value: safeProfile.expenses ? `INR ${Number(safeProfile.expenses).toLocaleString("en-IN")}` : null },
    { label: "Risk Profile", value: safeProfile.risk_profile },
  ];

  const filledCount = fields.filter((item) => item.value !== null && item.value !== undefined && item.value !== "").length;
  const completionPercent = Math.round((filledCount / fields.length) * 100);
  const goalsCount = Array.isArray(safeProfile.goals) ? safeProfile.goals.length : 0;
  const investmentsCount = Array.isArray(safeProfile.investments) ? safeProfile.investments.length : 0;

  return (
    <section className="card">
      <h2>Dashboard</h2>
      <p className="muted">
        Disclaimer: This information is for educational purposes only. Consult a SEBI-registered advisor before investment decisions.
      </p>

      <div className="dashboard-meta">
        <p><strong>Session:</strong> {sessionId || "Loading..."}</p>
        <p><strong>Profile Completion:</strong> {completionPercent}%</p>
      </div>

      <div className="progress-shell" role="progressbar" aria-valuenow={completionPercent} aria-valuemin={0} aria-valuemax={100}>
        <div className="progress-fill" style={{ width: `${completionPercent}%` }} />
      </div>

      <div className="dashboard-grid">
        <article className="metric-card">
          <span>Goals Tracked</span>
          <strong>{goalsCount}</strong>
        </article>
        <article className="metric-card">
          <span>Investments Tracked</span>
          <strong>{investmentsCount}</strong>
        </article>
        <article className="metric-card">
          <span>Money Health Score</span>
          <strong>{safeProfile.health_score?.overall ?? "—"}/100</strong>
        </article>
        <article className="metric-card">
          <span>Next Best Step</span>
          <strong>{completionPercent < 100 ? "Complete profile via onboarding" : "Run Tax and Portfolio"}</strong>
        </article>
      </div>

      <div className="dashboard-row-layout">
        <section className="insight-panel flex-1">
          <h3>Your Financial Profile</h3>
          <div className="dashboard-profile-grid">
            {fields.map((item) => (
              <div key={item.label} className="metric-card">
                <span>{item.label}</span>
                <strong>{item.value ?? "Not set"}</strong>
              </div>
            ))}
          </div>
        </section>

        {safeProfile.health_score && (
          <section className="insight-panel flex-1">
            <h3>Money Health Dimensions</h3>
            <div className="radar-grid">
              {Object.entries(safeProfile.health_score as Record<string, number>)
                .filter(([k]) => k !== "overall")
                .map(([k, v]) => (
                  <div key={k} className="radar-item">
                    <div className="radar-label">{k.replace(/_/g, " ")}</div>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{
                          width: `${v}%`,
                          background: v >= 70 ? "#1d7b5b" : v >= 40 ? "#d4a017" : "#d94040",
                        }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          </section>
        )}
      </div>

      <section className="insight-panel">
        <h3>Quick Actions</h3>
        <div className="dashboard-actions">
          <Link className="action-link" to="/onboarding">🚀 Start Onboarding</Link>
          <Link className="action-link" to="/voice">🎙️ Voice Mentor</Link>
          <Link className="action-link" to="/upload">📄 Upload Documents</Link>
          <Link className="action-link" to="/tax">⚖️ Tax Wizard</Link>
          <Link className="action-link" to="/portfolio">📊 Portfolio X-Ray</Link>
          <Link className="action-link" to="/news">🔔 News & Warnings</Link>
          <Link className="action-link" to="/life-event">🌟 Life Events</Link>
          <Link className="action-link" to="/couple">👫 Couple Planner</Link>
          <Link className="action-link" to="/whatif">🧪 What-If Sim</Link>
          <Link className="action-link" to="/emergency">🆘 Emergency Help</Link>
          <Link className="action-link" to="/recommendations">🎯 Smart Recommendations</Link>
          <Link className="action-link" to="/report">📈 Final Report</Link>
        </div>
      </section>
    </section>
  );
}
