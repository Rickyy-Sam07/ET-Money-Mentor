import { FormEvent, useState } from "react";
import { analyzePortfolio } from "../lib/api";

const starter = [
  { name: "Nifty Index Fund", units: 200, nav: 41.2, expense_ratio: 0.25 },
  { name: "Flexi Cap Fund", units: 150, nav: 62.8, expense_ratio: 1.1 },
];

export function PortfolioPage() {
  const [rawJson, setRawJson] = useState(JSON.stringify(starter, null, 2));
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const holdings = JSON.parse(rawJson);
      const data = await analyzePortfolio(holdings);
      setResult(data);
    } catch {
      setError("Invalid holdings JSON. Please correct the structure and retry.");
    }
  }

  return (
    <section className="card">
      <h2>Portfolio X-Ray</h2>
      <form onSubmit={submit} className="form-grid">
        <label className="full-width">
          Holdings JSON
          <textarea rows={10} value={rawJson} onChange={(e) => setRawJson(e.target.value)} />
        </label>
        <button type="submit">Run X-Ray</button>
      </form>
      {error ? <p className="error-text">{error}</p> : null}

      {result ? (
        <section className="insight-panel">
          <h3>Portfolio Metrics</h3>
          <div className="metric-grid">
            <div className="metric-card">
              <span>Total Value</span>
              <strong>{new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(result.metrics.total_value)}</strong>
            </div>
            <div className="metric-card">
              <span>XIRR</span>
              <strong>{result.metrics.xirr}%</strong>
            </div>
            <div className="metric-card">
              <span>Overlap</span>
              <strong>{result.metrics.overlap_percent}%</strong>
            </div>
            <div className="metric-card">
              <span>Expense Ratio Drag</span>
              <strong>{result.metrics.expense_ratio_drag}%</strong>
            </div>
          </div>
          <div className="bar-group">
            <div className="bar-row">
              <label>Portfolio Return</label>
              <div className="bar-track">
                <div className="bar-fill bar-fill-new" style={{ width: `${Math.min(result.metrics.xirr * 5, 100)}%` }} />
              </div>
            </div>
            <div className="bar-row">
              <label>Benchmark Return</label>
              <div className="bar-track">
                <div className="bar-fill bar-fill-old" style={{ width: `${Math.min(result.metrics.benchmark.benchmark_return_estimate * 5, 100)}%` }} />
              </div>
            </div>
          </div>
        </section>
      ) : null}

      <pre className="output-box">{result ? JSON.stringify(result, null, 2) : "No analysis yet."}</pre>
    </section>
  );
}
