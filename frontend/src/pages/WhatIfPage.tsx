import { FormEvent, useState } from "react";
import { simulateWhatIf } from "../lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

function formatInr(v: number) {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);
}

export function WhatIfPage() {
    const [scenario, setScenario] = useState("I receive a bonus");
    const [amount, setAmount] = useState("100000");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const data = await simulateWhatIf(scenario, Number(amount));
            setResult(data);
        } catch {
            setError("Simulation failed. Is the backend running?");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="card">
            <h2>🔮 What-if Simulation</h2>
            <p className="muted">Explore how a financial event could change your future.</p>
            <p className="disclaimer">⚠️ This is for educational purposes only. Consult a SEBI-registered advisor.</p>

            <form className="form-grid" onSubmit={handleSubmit}>
                <label className="full-width">
                    Scenario
                    <input
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        placeholder="e.g., I receive a ₹1,00,000 bonus"
                    />
                </label>
                <label>
                    Amount (₹)
                    <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                    {loading ? "Simulating..." : "🚀 Run Simulation"}
                </button>
            </form>

            {error && <p className="error-text">{error}</p>}

            {result && (
                <div className="whatif-results">
                    {/* Base */}
                    <div className="insight-panel">
                        <h3>📊 Baseline (without this event)</h3>
                        <div className="metric-grid">
                            <div className="metric-card"><span>5-Year Projection</span><strong>{formatInr(result.base_projection.year_5)}</strong></div>
                            <div className="metric-card"><span>10-Year Projection</span><strong>{formatInr(result.base_projection.year_10)}</strong></div>
                        </div>
                    </div>

                    {/* Scenarios */}
                    <div className="scenario-cards">
                        {(result.scenarios as any[]).map((s: any) => (
                            <div key={s.name} className="scenario-card">
                                <h3>{s.name}</h3>
                                <p>{s.description}</p>
                                <div className="metric-grid" style={{ marginTop: 10 }}>
                                    <div className="metric-card">
                                        <span>5-Year Value</span>
                                        <strong>{formatInr(s.projected_5y)}</strong>
                                        <span className="gain">+{formatInr(s.gain_over_base_5y)}</span>
                                    </div>
                                    <div className="metric-card">
                                        <span>10-Year Value</span>
                                        <strong>{formatInr(s.projected_10y)}</strong>
                                        <span className="gain">+{formatInr(s.gain_over_base_10y)}</span>
                                    </div>
                                </div>
                                <p className="muted" style={{ marginTop: 8 }}>Risk: {s.risk}</p>
                            </div>
                        ))}
                    </div>

                    <div className="insight-panel" style={{ marginTop: 14 }}>
                        <h4>💡 Recommendation</h4>
                        <p>{result.recommendation}</p>
                    </div>
                </div>
            )}
        </section>
    );
}
