import { FormEvent, useState } from "react";
import { analyzeTax } from "../lib/api";

function formatInr(value: number) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
}

export function TaxPage() {
  const [salary, setSalary] = useState("1200000");
  const [ded80c, setDed80c] = useState("60000");
  const [ded80d, setDed80d] = useState("12000");
  const [regime, setRegime] = useState<"old" | "new">("new");
  const [result, setResult] = useState<any>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const data = await analyzeTax(
      {
        gross_salary: Number(salary),
        deductions_80c: Number(ded80c),
        deductions_80d: Number(ded80d),
      },
      regime
    );
    setResult(data);
  }

  return (
    <section className="card">
      <h2>Tax Wizard</h2>
      <form className="form-grid" onSubmit={submit}>
        <label>
          Gross salary
          <input value={salary} onChange={(e) => setSalary(e.target.value)} />
        </label>
        <label>
          Used 80C
          <input value={ded80c} onChange={(e) => setDed80c(e.target.value)} />
        </label>
        <label>
          Used 80D
          <input value={ded80d} onChange={(e) => setDed80d(e.target.value)} />
        </label>
        <label>
          Regime preference
          <select value={regime} onChange={(e) => setRegime(e.target.value as "old" | "new")}>
            <option value="old">Old</option>
            <option value="new">New</option>
          </select>
        </label>
        <button type="submit">Analyze tax</button>
      </form>

      {result ? (
        <section className="insight-panel">
          <h3>Regime Comparison</h3>
          <div className="metric-grid">
            <div className="metric-card">
              <span>Old Regime Tax</span>
              <strong>{formatInr(result.regime_comparison.old)}</strong>
            </div>
            <div className="metric-card">
              <span>New Regime Tax</span>
              <strong>{formatInr(result.regime_comparison.new)}</strong>
            </div>
            <div className="metric-card">
              <span>Recommended</span>
              <strong>{String(result.regime_comparison.recommended).toUpperCase()}</strong>
            </div>
          </div>
          <div className="bar-group">
            <div className="bar-row">
              <label>Old</label>
              <div className="bar-track">
                <div
                  className="bar-fill bar-fill-old"
                  style={{
                    width: `${Math.min((result.regime_comparison.old / Math.max(result.regime_comparison.old, result.regime_comparison.new, 1)) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
            <div className="bar-row">
              <label>New</label>
              <div className="bar-track">
                <div
                  className="bar-fill bar-fill-new"
                  style={{
                    width: `${Math.min((result.regime_comparison.new / Math.max(result.regime_comparison.old, result.regime_comparison.new, 1)) * 100, 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>

          <h3>Suggested Instruments</h3>
          <div className="suggestion-grid">
            {result.suggestions.map((item: { instrument: string; risk: string; liquidity: string; estimated_tax_saving: number }) => (
              <article key={item.instrument} className="suggestion-card">
                <h4>{item.instrument}</h4>
                <p>Risk: {item.risk}</p>
                <p>Liquidity: {item.liquidity}</p>
                <p>Estimated tax saving: {formatInr(item.estimated_tax_saving)}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <pre className="output-box">{result ? JSON.stringify(result, null, 2) : "No analysis yet."}</pre>
    </section>
  );
}
