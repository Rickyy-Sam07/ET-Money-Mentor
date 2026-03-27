import { FormEvent, useEffect, useState } from "react";
import { analyzePortfolio } from "../lib/api";
import {
  loadPortfolioInput,
  loadPortfolioResult,
  savePortfolioInput,
  savePortfolioResult,
} from "../lib/voiceState";

const starter = [
  {
    name: "Nifty Index Fund",
    units: 200,
    nav: 41.2,
    expense_ratio: 0.25,
    invested_amount: 8000,
    buy_date: "2024-01-01",
  },
  {
    name: "Flexi Cap Fund",
    units: 150,
    nav: 62.8,
    expense_ratio: 1.1,
    invested_amount: 9000,
    buy_date: "2024-02-01",
  },
];

type HoldingRow = {
  name: string;
  units: number;
  nav: number;
  expense_ratio: number;
  invested_amount: number;
  buy_date: string;
};

const EMPTY_ROW: HoldingRow = {
  name: "",
  units: 0,
  nav: 0,
  expense_ratio: 0,
  invested_amount: 0,
  buy_date: "",
};

function normalizeHolding(input: any): HoldingRow {
  return {
    name: String(input?.name ?? ""),
    units: Number(input?.units ?? 0),
    nav: Number(input?.nav ?? 0),
    expense_ratio: Number(input?.expense_ratio ?? 0),
    invested_amount: Number(input?.invested_amount ?? 0),
    buy_date: String(input?.buy_date ?? ""),
  };
}

export function PortfolioPage() {
  const [holdings, setHoldings] = useState<HoldingRow[]>(starter);
  const [rawJson, setRawJson] = useState(JSON.stringify(starter, null, 2));
  const [showAdvancedEditor, setShowAdvancedEditor] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const cachedInput = loadPortfolioInput<any[]>();
    if (cachedInput) {
      setHoldings(cachedInput.map(normalizeHolding));
      setRawJson(JSON.stringify(cachedInput, null, 2));
    }
    const cachedResult = loadPortfolioResult();
    if (cachedResult) {
      setResult(cachedResult);
    }
  }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const payload = holdings.map((row) => ({
        name: row.name,
        units: Number(row.units),
        nav: Number(row.nav),
        expense_ratio: Number(row.expense_ratio),
        invested_amount: Number(row.invested_amount),
        buy_date: row.buy_date,
      }));

      if (payload.some((row) => !row.name.trim())) {
        setError("Each holding must have a fund name.");
        return;
      }

      const data = await analyzePortfolio(payload);
      setRawJson(JSON.stringify(payload, null, 2));
      savePortfolioInput(payload);
      savePortfolioResult(data);
      setResult(data);
    } catch {
      setError("Unable to run X-Ray. Please check holdings and retry.");
    }
  }

  function updateHolding(index: number, key: keyof HoldingRow, value: string) {
    setHoldings((prev) =>
      prev.map((row, idx) => {
        if (idx !== index) return row;
        if (key === "name" || key === "buy_date") {
          return { ...row, [key]: value };
        }
        return { ...row, [key]: Number(value || 0) };
      })
    );
  }

  function addHoldingRow() {
    setHoldings((prev) => [...prev, { ...EMPTY_ROW }]);
  }

  function removeHoldingRow(index: number) {
    setHoldings((prev) => prev.filter((_, idx) => idx !== index));
  }

  function applyAdvancedJson() {
    setError("");
    try {
      const parsed = JSON.parse(rawJson);
      if (!Array.isArray(parsed)) {
        setError("Holdings JSON must be an array.");
        return;
      }
      setHoldings(parsed.map(normalizeHolding));
      setShowAdvancedEditor(false);
    } catch {
      setError("Invalid JSON format. Please fix and try again.");
    }
  }

  const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });

  function overlapLabel(value: number) {
    if (value >= 50) return "High";
    if (value >= 25) return "Moderate";
    return "Low";
  }

  function returnNarrative(portfolioReturn: number, benchmarkReturn: number) {
    const diff = portfolioReturn - benchmarkReturn;
    if (diff >= 1) {
      return `Portfolio is outperforming benchmark by ${diff.toFixed(2)}%.`;
    }
    if (diff <= -1) {
      return `Portfolio is trailing benchmark by ${Math.abs(diff).toFixed(2)}%.`;
    }
    return "Portfolio is broadly in line with benchmark.";
  }

  return (
    <section className="card">
      <h2>Portfolio X-Ray</h2>
      <p className="muted">Analyze returns, overlap, expense drag, and rebalancing opportunities in one view.</p>
      <form onSubmit={submit} className="form-grid">
        <label className="full-width">
          Holdings
          <div className="table-wrap">
            <table className="portfolio-input-table">
              <thead>
                <tr>
                  <th>Fund Name</th>
                  <th>Units</th>
                  <th>NAV</th>
                  <th>Expense %</th>
                  <th>Invested Amt</th>
                  <th>Buy Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((row, idx) => (
                  <tr key={`${idx}-${row.name || "holding"}`}>
                    <td>
                      <input value={row.name} onChange={(e) => updateHolding(idx, "name", e.target.value)} placeholder="Fund name" />
                    </td>
                    <td>
                      <input type="number" value={row.units} onChange={(e) => updateHolding(idx, "units", e.target.value)} />
                    </td>
                    <td>
                      <input type="number" value={row.nav} onChange={(e) => updateHolding(idx, "nav", e.target.value)} />
                    </td>
                    <td>
                      <input type="number" step="0.01" value={row.expense_ratio} onChange={(e) => updateHolding(idx, "expense_ratio", e.target.value)} />
                    </td>
                    <td>
                      <input type="number" value={row.invested_amount} onChange={(e) => updateHolding(idx, "invested_amount", e.target.value)} />
                    </td>
                    <td>
                      <input type="date" value={row.buy_date} onChange={(e) => updateHolding(idx, "buy_date", e.target.value)} />
                    </td>
                    <td>
                      <button type="button" className="secondary-btn" onClick={() => removeHoldingRow(idx)} disabled={holdings.length <= 1}>
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </label>
        <button type="button" className="secondary-btn" onClick={addHoldingRow}>Add Fund</button>
        <button
          type="button"
          className="secondary-btn"
          onClick={() => {
            setRawJson(JSON.stringify(holdings, null, 2));
            setShowAdvancedEditor((v) => !v);
          }}
        >
          {showAdvancedEditor ? "Hide JSON Editor" : "Advanced JSON Editor"}
        </button>
        <button type="submit">Run X-Ray</button>
      </form>

      {showAdvancedEditor ? (
        <section className="insight-panel">
          <h3>Advanced Holdings JSON</h3>
          <textarea rows={10} value={rawJson} onChange={(e) => setRawJson(e.target.value)} />
          <div className="portfolio-advanced-actions">
            <button type="button" onClick={applyAdvancedJson}>Apply JSON</button>
          </div>
        </section>
      ) : null}
      {error ? <p className="error-text">{error}</p> : null}

      {result ? (
        <>
          <section className="insight-panel">
            <h3>Portfolio Metrics</h3>
            <div className="metric-grid">
              <div className="metric-card">
                <span>Total Value</span>
                <strong>{inr.format(result.metrics.total_value)}</strong>
              </div>
              <div className="metric-card">
                <span>Invested Amount</span>
                <strong>{inr.format(result.metrics.invested_amount)}</strong>
              </div>
              <div className="metric-card">
                <span>XIRR</span>
                <strong>{result.metrics.xirr}%</strong>
              </div>
              <div className="metric-card">
                <span>Overlap ({overlapLabel(result.metrics.overlap_percent)})</span>
                <strong>{result.metrics.overlap_percent}%</strong>
              </div>
              <div className="metric-card">
                <span>Expense Ratio Drag</span>
                <strong>{result.metrics.expense_ratio_drag}%</strong>
              </div>
              <div className="metric-card">
                <span>Market Signal</span>
                <strong>{String(result.market_signal?.label || "neutral").toUpperCase()}</strong>
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

            <p className="muted portfolio-callout">
              {returnNarrative(result.metrics.xirr, result.metrics.benchmark.benchmark_return_estimate)}
            </p>
          </section>

          <section className="insight-panel">
            <h3>Reconstructed Holdings</h3>
            <div className="table-wrap">
              <table className="portfolio-table">
                <thead>
                  <tr>
                    <th>Fund</th>
                    <th>Units</th>
                    <th>NAV</th>
                    <th>Value</th>
                    <th>Expense Ratio</th>
                  </tr>
                </thead>
                <tbody>
                  {(result.reconstructed_portfolio || []).map((item: any) => (
                    <tr key={item.name}>
                      <td>{item.name}</td>
                      <td>{item.units}</td>
                      <td>{item.nav}</td>
                      <td>{inr.format(item.value)}</td>
                      <td>{item.expense_ratio}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="insight-panel">
            <h3>Rebalancing Plan</h3>
            <ul className="plan-list">
              {(result.rebalancing_plan || []).map((step: string, idx: number) => (
                <li key={`${idx}-${step}`}>{step}</li>
              ))}
            </ul>
          </section>
        </>
      ) : null}

      <details className="raw-json-panel">
        <summary>{result ? "Show Raw JSON" : "No analysis yet"}</summary>
        {result ? <pre className="output-box">{JSON.stringify(result, null, 2)}</pre> : null}
      </details>
    </section>
  );
}
