import { useEffect, useState } from "react";
import { getRecommendations } from "../lib/api";
import { useFinancialStore } from "../lib/useStore";

/* eslint-disable @typescript-eslint/no-explicit-any */

function formatInr(v: number) {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);
}

export function RecommendationsPage() {
    const { profile } = useFinancialStore();
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function load() {
            try {
                // If profile exists in store, we could even show local recs first
                const data = await getRecommendations();
                setResult(data);
            } catch {
                setError("Failed to load recommendations. Is the backend running?");
            } finally {
                setLoading(false);
            }
        }
        void load();
    }, [profile]);

    if (loading) return <section className="card"><h2>Loading recommendations...</h2></section>;
    if (error) return <section className="card"><h2>Recommendations</h2><p className="error-text">{error}</p></section>;
    if (!result) return null;

    return (
        <section className="card">
            <h2>🎯 Personalised Recommendations</h2>
            <p className="muted">
                Profile: <strong>{(result.segment as string).replace(/_/g, " ")}</strong> | Risk: <strong>{result.risk_profile}</strong>
            </p>
            <p className="disclaimer">⚠️ This is for educational purposes only. Consult a SEBI-registered advisor.</p>

            {/* AI Explanation */}
            {result.ai_explanation && (
                <div className="ai-panel">
                    <h3>🤖 AI Insight</h3>
                    <p>{result.ai_explanation}</p>
                </div>
            )}

            {/* Asset Allocation */}
            <div className="insight-panel">
                <h3>📊 Recommended Asset Allocation</h3>
                <div className="allocation-bars">
                    {Object.entries(result.asset_allocation as Record<string, number>).map(([k, v]) => (
                        <div key={k} className="alloc-row">
                            <div className="alloc-label">
                                <span>{k.charAt(0).toUpperCase() + k.slice(1)}</span>
                                <span className="muted">{v}%</span>
                            </div>
                            <div className="bar-track">
                                <div
                                    className="bar-fill"
                                    style={{
                                        width: `${v}%`,
                                        background: k === "equity" ? "#1d7b5b" : k === "debt" ? "#0e6ba8" : k === "gold" ? "#d4a017" : "#7b8794",
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Top Funds */}
            <div className="insight-panel">
                <h3>🏆 Top Recommended Funds</h3>
                <div className="suggestion-grid">
                    {(result.recommended_funds as any[]).map((f: any) => (
                        <article key={f.name} className="suggestion-card rec-card">
                            <h4>{f.name}</h4>
                            <p><strong>Category:</strong> {f.category}</p>
                            <p><strong>3Y Return:</strong> {f.return_3y}%</p>
                            <p><strong>Expense Ratio:</strong> {f.expense}%</p>
                            <p className="muted">Risk: {f.risk}</p>
                        </article>
                    ))}
                </div>
            </div>

            {/* Insurance */}
            <div className="insight-panel">
                <h3>🛡️ Insurance Recommendations</h3>
                <div className="suggestion-grid">
                    {(result.insurance as any[]).map((ins: any) => (
                        <article key={ins.type} className="suggestion-card">
                            <h4>{ins.type}</h4>
                            <p>{ins.recommendation}</p>
                            <p className="muted">Est. Premium: {ins.estimated_premium}</p>
                        </article>
                    ))}
                </div>
            </div>

            {/* Tax Saving */}
            <div className="insight-panel">
                <h3>💰 Tax-Saving Opportunities</h3>
                {(result.tax_saving as any[]).map((t: any) => (
                    <div key={t.section} className="tax-rec-item">
                        <strong>Section {t.section}</strong>
                        <span className="muted"> — Gap: {formatInr(t.gap)}</span>
                        <p>{t.suggestion}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}
