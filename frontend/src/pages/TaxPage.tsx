// [DEV1] TaxPage.tsx — tax wizard. Dev2: do not modify.
import { FormEvent, useEffect, useState } from "react";
import { analyzeTax } from "../lib/api";
import { loadTaxInput, loadTaxResult, saveTaxInput, saveTaxResult } from "../lib/voiceState";

function formatInr(value: number) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
}

export function TaxPage() {
  const [salary, setSalary] = useState("1200000");
  const [ded80c, setDed80c] = useState("60000");
  const [ded80d, setDed80d] = useState("12000");
  const [regime, setRegime] = useState<"old" | "new">("new");
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const cachedInput = loadTaxInput();
    if (cachedInput) {
      setSalary(String(cachedInput.gross_salary));
      setDed80c(String(cachedInput.deductions_80c));
      setDed80d(String(cachedInput.deductions_80d));
      setRegime(cachedInput.regime_preference);
    }
    const cachedResult = loadTaxResult();
    if (cachedResult) {
      setResult(cachedResult);
    }
  }, []);

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
    saveTaxInput({
      gross_salary: Number(salary),
      deductions_80c: Number(ded80c),
      deductions_80d: Number(ded80d),
      regime_preference: regime,
    });
    saveTaxResult(data);
    setResult(data);
  }

  function utilization(used: number, max: number) {
    return Math.min(Math.round((used / Math.max(max, 1)) * 100), 100);
  }

  function taxDelta(oldTax: number, newTax: number) {
    const diff = Math.abs(oldTax - newTax);
    if (diff < 1) {
      return "Both regimes are almost equal for current inputs.";
    }
    return oldTax > newTax
      ? `New regime saves ${formatInr(diff)} compared to old regime.`
      : `Old regime saves ${formatInr(diff)} compared to new regime.`;
  }

  return (
    <section className="card">
      <h2>Tax Wizard</h2>
      <p className="muted">Estimate tax, compare regimes, and identify unused deduction capacity instantly.</p>
      <form className="form-grid" onSubmit={submit}>
        <label>
          Gross salary
          <input value={salary} onChange={(e) => setSalary(e.target.value)} placeholder="e.g. 1200000" />
        </label>
        <label>
          Used 80C
          <input value={ded80c} onChange={(e) => setDed80c(e.target.value)} placeholder="Max 150000" />
        </label>
        <label>
          Used 80D
          <input value={ded80d} onChange={(e) => setDed80d(e.target.value)} placeholder="Max 25000" />
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
        <>
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
                <strong className="regime-chip">{String(result.regime_comparison.recommended).toUpperCase()}</strong>
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

            <p className="muted tax-highlight">
              {taxDelta(result.regime_comparison.old, result.regime_comparison.new)}
            </p>
          </section>

          <section className="insight-panel">
            <h3>Deduction Utilization</h3>
            <div className="tax-deduction-grid">
              <div className="metric-card">
                <span>80C Used</span>
                <strong>{formatInr(result.deductions.used_80c)}</strong>
                <p className="muted">Missing: {formatInr(result.deductions.missed_80c)} | Utilization: {utilization(result.deductions.used_80c, 150000)}%</p>
              </div>
              <div className="metric-card">
                <span>80D Used</span>
                <strong>{formatInr(result.deductions.used_80d)}</strong>
                <p className="muted">Missing: {formatInr(result.deductions.missed_80d)} | Utilization: {utilization(result.deductions.used_80d, 25000)}%</p>
              </div>
            </div>
          </section>

          <section className="insight-panel">
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
        </>
      ) : null}

      <details className="raw-json-panel">
        <summary>{result ? "Show Raw JSON" : "No analysis yet"}</summary>
        {result ? <pre className="output-box">{JSON.stringify(result, null, 2)}</pre> : null}
      </details>
    </section>
  );
}
