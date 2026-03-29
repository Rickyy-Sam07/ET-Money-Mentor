import { FormEvent, useState } from "react";
import { optimizeCouple } from "../lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

function formatInr(v: number) {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);
}

export function CouplePlannerPage() {
    const [p1, setP1] = useState({ income: 1500000, expenses: 40000, rent: 20000, nps_contribution: 0, investments: [] as any[] });
    const [p2, setP2] = useState({ income: 1000000, expenses: 30000, rent: 0, nps_contribution: 0, investments: [] as any[] });
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const data = await optimizeCouple(p1, p2);
            setResult(data);
        } catch {
            setError("Failed to optimize. Is the backend running?");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="card">
            <h2>💑 Couple's Money Planner</h2>
            <p className="muted">Enter both partners' details for joint financial optimization.</p>
            <p className="disclaimer">⚠️ This is for educational purposes only. Consult a SEBI-registered advisor.</p>

            <form className="couple-form" onSubmit={handleSubmit}>
                <div className="couple-columns">
                    <div className="partner-col">
                        <h3>Partner 1</h3>
                        <label>Annual Income (₹)<input type="number" value={p1.income} onChange={(e) => setP1({ ...p1, income: Number(e.target.value) })} /></label>
                        <label>Monthly Expenses (₹)<input type="number" value={p1.expenses} onChange={(e) => setP1({ ...p1, expenses: Number(e.target.value) })} /></label>
                        <label>Monthly Rent (₹)<input type="number" value={p1.rent} onChange={(e) => setP1({ ...p1, rent: Number(e.target.value) })} /></label>
                        <label>NPS Contribution (₹/yr)<input type="number" value={p1.nps_contribution} onChange={(e) => setP1({ ...p1, nps_contribution: Number(e.target.value) })} /></label>
                    </div>
                    <div className="partner-col">
                        <h3>Partner 2</h3>
                        <label>Annual Income (₹)<input type="number" value={p2.income} onChange={(e) => setP2({ ...p2, income: Number(e.target.value) })} /></label>
                        <label>Monthly Expenses (₹)<input type="number" value={p2.expenses} onChange={(e) => setP2({ ...p2, expenses: Number(e.target.value) })} /></label>
                        <label>Monthly Rent (₹)<input type="number" value={p2.rent} onChange={(e) => setP2({ ...p2, rent: Number(e.target.value) })} /></label>
                        <label>NPS Contribution (₹/yr)<input type="number" value={p2.nps_contribution} onChange={(e) => setP2({ ...p2, nps_contribution: Number(e.target.value) })} /></label>
                    </div>
                </div>
                <button type="submit" disabled={loading} className="full-width" style={{ marginTop: 12 }}>
                    {loading ? "Optimizing..." : "🔍 Optimize Joint Plan"}
                </button>
            </form>

            {error && <p className="error-text">{error}</p>}

            {result && (
                <div className="couple-results">
                    {/* AI Plan */}
                    {result.ai_plan && (
                        <div className="ai-panel">
                            <h3>🤖 AI Joint Plan Summary</h3>
                            <p>{result.ai_plan}</p>
                        </div>
                    )}

                    {/* HRA */}
                    <div className="insight-panel">
                        <h3>🏠 HRA Optimization</h3>
                        <p>{result.hra_optimization.suggestion}</p>
                        <p><strong>Tax Saved:</strong> {formatInr(result.hra_optimization.tax_saved)}</p>
                    </div>

                    {/* NPS */}
                    <div className="insight-panel">
                        <h3>🏛️ NPS Matching</h3>
                        {(result.nps_matching.suggestions as string[]).map((s: string, i: number) => (
                            <p key={i}>{s}</p>
                        ))}
                        <p><strong>Combined Tax Saved:</strong> {formatInr(result.nps_matching.combined_tax_saved)}</p>
                    </div>

                    {/* SIP Splits */}
                    <div className="insight-panel">
                        <h3>📊 SIP Allocation by Goal</h3>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Goal</th>
                                    <th>Partner 1</th>
                                    <th>Partner 2</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(result.sip_splits as any[]).map((s: any) => (
                                    <tr key={s.goal}>
                                        <td>{s.goal}</td>
                                        <td>{formatInr(s.partner1_sip)}/mo</td>
                                        <td>{formatInr(s.partner2_sip)}/mo</td>
                                        <td><strong>{formatInr(s.total_sip)}/mo</strong></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Insurance */}
                    <div className="insight-panel">
                        <h3>🛡️ Insurance</h3>
                        <p><strong>Term Life:</strong> {result.insurance.term_life_cover}</p>
                        <p><strong>Health:</strong> {result.insurance.health_cover}</p>
                        <p className="muted">{result.insurance.suggestion}</p>
                    </div>

                    {/* Net Worth Projection */}
                    <div className="insight-panel">
                        <h3>📈 Combined Net Worth Projection</h3>
                        <div className="projection-bars">
                            {(result.net_worth_projection as any[]).map((p: any) => (
                                <div key={p.year} className="proj-row">
                                    <span>Year {p.year}</span>
                                    <div className="bar-track" style={{ flex: 1 }}>
                                        <div
                                            className="bar-fill bar-fill-new"
                                            style={{
                                                width: `${Math.min((p.net_worth / (result.net_worth_projection as any[]).slice(-1)[0].net_worth) * 100, 100)}%`,
                                            }}
                                        />
                                    </div>
                                    <span className="muted">{formatInr(p.net_worth)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}
