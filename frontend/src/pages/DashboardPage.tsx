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
          <span>Next Best Step</span>
          <strong>{completionPercent < 100 ? "Complete profile via voice" : "Run Tax and Portfolio"}</strong>
        </article>
      </div>

      <section className="insight-panel">
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

      <section className="insight-panel">
        <h3>Quick Actions</h3>
        <div className="dashboard-actions">
          <Link className="action-link" to="/voice">Complete Profile with Voice</Link>
          <Link className="action-link" to="/upload">Upload Form 16 / Statement</Link>
          <Link className="action-link" to="/tax">Run Tax Wizard</Link>
          <Link className="action-link" to="/portfolio">Run Portfolio X-Ray</Link>
          <Link className="action-link" to="/news">Check Market Warnings</Link>
          <Link className="action-link" to="/report">Generate Report</Link>
        </div>
      </section>
    </section>
  );
}
