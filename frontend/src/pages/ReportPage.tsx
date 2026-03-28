// [DEV1] ReportPage.tsx — unified report view. Dev2: do not modify.
import { useEffect, useState } from "react";
import { loadUnifiedReport } from "../lib/voiceState";

export function ReportPage() {
  const [report, setReport] = useState<any>(null);

  // Read on every mount so navigating here after voice command always picks up fresh data
  useEffect(() => {
    setReport(loadUnifiedReport());
  }, []);

  if (!report) {
    return (
      <section className="card">
        <h2>Unified Report</h2>
        <p className="muted">No report generated yet. Use the voice command "generate report" or run Tax Wizard and Portfolio X-Ray first.</p>
      </section>
    );
  }

  const tax = report.tax_result;
  const portfolio = report.portfolio_result;
  const news = Array.isArray(report.news) ? report.news : [];
  const taxInput = report.tax_input;
  const portfolioInput = Array.isArray(report.portfolio_input) ? report.portfolio_input : [];

  return (
    <section className="card">
      <h2>Unified Report</h2>
      <p className="muted">Generated at: {report.generated_at ? new Date(report.generated_at).toLocaleString() : "—"}</p>

      {/* Health Score Summary (Dev2) */}
      {report.health_score && (
        <div className="insight-panel">
          <h3>Money Health Score: {report.health_score.overall}/100</h3>
          <div className="radar-grid">
            {Object.entries(report.health_score as Record<string, number>)
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
        </div>
      )}

      {/* Tax Summary */}
      <div className="insight-panel">
        <h3>Tax Summary</h3>
        {tax ? (
          <>
            <div className="metric-grid">
              <div className="metric-card">
                <span>Gross Salary</span>
                <strong>₹{Number(taxInput?.gross_salary ?? 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="metric-card">
                <span>Recommended Regime</span>
                <strong>{tax.regime_comparison?.selected ?? "—"}</strong>
              </div>
              <div className="metric-card">
                <span>Old Regime Tax</span>
                <strong>₹{Number(tax.regime_comparison?.old_regime_tax ?? tax.regime_comparison?.old ?? 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="metric-card">
                <span>New Regime Tax</span>
                <strong>₹{Number(tax.regime_comparison?.new_regime_tax ?? tax.regime_comparison?.new ?? 0).toLocaleString("en-IN")}</strong>
              </div>
            </div>
            {tax.deductions && (
              <div style={{ marginTop: 10 }}>
                <strong>Deductions:</strong>
                <ul className="plan-list" style={{ marginTop: 6 }}>
                  {Array.isArray(tax.deductions)
                    ? tax.deductions.map((d: any, i: number) => (
                      <li key={i}>{d.section} — ₹{Number(d.amount ?? 0).toLocaleString("en-IN")}: {d.note}</li>
                    ))
                    : Object.entries(tax.deductions).map(([k, v]) => (
                      <li key={k}>{k.replace(/_/g, " ").toUpperCase()}: ₹{Number(v).toLocaleString("en-IN")}</li>
                    ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="muted">No tax analysis data. Run Tax Wizard first.</p>
        )}
      </div>

      {/* FIRE Roadmap (Dev2) */}
      {report.roadmap && Array.isArray(report.roadmap) && (
        <div className="insight-panel">
          <h3>12-Month FIRE Roadmap</h3>
          <div className="roadmap-timeline">
            {report.roadmap.slice(0, 3).map((item: any) => (
              <div key={item.month} className="roadmap-month">
                <strong>Month {item.month} </strong>
                <span className="muted"> (SIP: ₹{Number(item.sip_amount || 0).toLocaleString("en-IN")})</span>
                <p className="muted" style={{ margin: "4px 0 0" }}>{item.actions?.[0] || "Continue investing."}</p>
              </div>
            ))}
            {report.roadmap.length > 3 && <p className="muted">Plus {report.roadmap.length - 3} more months of actions...</p>}
          </div>
        </div>
      )}

      {/* Portfolio Summary */}
      <div className="insight-panel">
        <h3>Portfolio Summary</h3>
        {portfolio ? (
          <>
            <div className="metric-grid">
              <div className="metric-card">
                <span>XIRR</span>
                <strong>{portfolio.metrics?.xirr ?? "—"}%</strong>
              </div>
              <div className="metric-card">
                <span>Overlap</span>
                <strong>{portfolio.metrics?.overlap_percent ?? "—"}%</strong>
              </div>
              <div className="metric-card">
                <span>Expense Ratio Drag</span>
                <strong>{portfolio.metrics?.expense_ratio_drag ?? "—"}%</strong>
              </div>
              <div className="metric-card">
                <span>Holdings</span>
                <strong>{portfolioInput.length}</strong>
              </div>
            </div>
            {Array.isArray(portfolio.rebalancing_plan) && portfolio.rebalancing_plan.length > 0 && (
              <div style={{ marginTop: 10 }}>
                <strong>Rebalancing Suggestions:</strong>
                <ul className="plan-list" style={{ marginTop: 6 }}>
                  {portfolio.rebalancing_plan.map((p: any, i: number) => (
                    <li key={i}>
                      {typeof p === "string"
                        ? p
                        : `${p.action ?? ""}${p.fund ? `: ${p.fund}` : ""}${p.reason ? ` — ${p.reason}` : ""}`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="muted">No portfolio data. Run Portfolio X-Ray first.</p>
        )}
      </div>

      {/* News Warnings */}
      <div className="insight-panel">
        <h3>Market News & Warnings</h3>
        {news.length > 0 ? (
          <div className="news-list">
            {news.slice(0, 5).map((item: any, i: number) => (
              <div key={i} className={`news-item ${item.is_warning ? "news-warning" : ""}`}>
                <strong>{item.title ?? item.headline ?? "News"}</strong>
                {item.summary && <p style={{ margin: "4px 0 0" }}>{item.summary}</p>}
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">No news data. Refresh news first.</p>
        )}
      </div>

      <details className="raw-json-panel">
        <summary>Raw Report JSON</summary>
        <pre className="output-box">{JSON.stringify(report, null, 2)}</pre>
      </details>
    </section>
  );
}
