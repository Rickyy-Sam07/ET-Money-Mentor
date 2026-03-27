import { FormEvent, useState } from "react";
import { adviseLifeEvent } from "../lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

const EVENT_TYPES = [
    { value: "bonus", label: "💰 Bonus", icon: "💰" },
    { value: "inheritance", label: "🏛️ Inheritance", icon: "🏛️" },
    { value: "marriage", label: "💍 Marriage", icon: "💍" },
    { value: "new_baby", label: "👶 New Baby", icon: "👶" },
];

function formatInr(v: number) {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);
}

export function LifeEventPage() {
    const [eventType, setEventType] = useState("bonus");
    const [amount, setAmount] = useState("500000");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const data = await adviseLifeEvent({
                event_type: eventType,
                amount: Number(amount),
            });
            setResult(data);
        } catch {
            setError("Failed to get advice. Is the backend running?");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="card">
            <h2>🎉 Life Event Financial Advisor</h2>
            <p className="muted">Select a life event to get personalised financial advice.</p>
            <p className="disclaimer">⚠️ This is for educational purposes only. Consult a SEBI-registered advisor.</p>

            <form className="form-grid" onSubmit={handleSubmit}>
                <label>
                    Event Type
                    <select value={eventType} onChange={(e) => setEventType(e.target.value)}>
                        {EVENT_TYPES.map((t) => (
                            <option key={t.value} value={t.value}>{t.label}</option>
                        ))}
                    </select>
                </label>
                <label>
                    Amount (₹)
                    <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
                </label>
                <button type="submit" disabled={loading}>
                    {loading ? "Analyzing..." : "Get Advice"}
                </button>
            </form>

            {error && <p className="error-text">{error}</p>}

            {result && (
                <div className="life-event-results">
                    <div className="insight-panel">
                        <h3>{result.title}</h3>

                        {result.ai_advice && (
                            <div className="ai-panel">
                                <h4>🤖 AI Advice</h4>
                                <p>{result.ai_advice}</p>
                            </div>
                        )}

                        <h4>Priority Steps</h4>
                        <ol className="priority-list">
                            {(result.priority_steps as string[]).map((step: string, i: number) => (
                                <li key={i}>{step}</li>
                            ))}
                        </ol>

                        <h4>Suggested Allocation</h4>
                        <div className="allocation-bars">
                            {(result.allocations as any[]).map((a: any) => (
                                <div key={a.category} className="alloc-row">
                                    <div className="alloc-label">
                                        <span>{a.category}</span>
                                        <span className="muted">{formatInr(a.amount)} ({a.percentage}%)</span>
                                    </div>
                                    <div className="bar-track">
                                        <div className="bar-fill bar-fill-new" style={{ width: `${a.percentage}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>

                        {result.tax_note && (
                            <div className="tax-note">
                                <h4>📋 Tax Implications</h4>
                                <p>{result.tax_note}</p>
                            </div>
                        )}

                        {result.goal_impact?.length > 0 && (
                            <div className="goal-impact">
                                <h4>🎯 Goal Impact</h4>
                                {(result.goal_impact as string[]).map((gi: string, i: number) => (
                                    <p key={i}>{gi}</p>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </section>
    );
}
