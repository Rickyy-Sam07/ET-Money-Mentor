import { FormEvent, useState } from "react";
import { submitOnboarding } from "../lib/api";

const INVESTMENT_TYPES = ["Mutual Funds", "Stocks", "PPF", "NPS", "FD", "Gold", "ELSS", "EPF", "LIC", "Real Estate"];
const GOAL_TYPES = ["Retirement", "Child Education", "House", "Car", "Travel", "Emergency Fund", "Wealth Building"];

/* eslint-disable @typescript-eslint/no-explicit-any */

export function OnboardingPage() {
    const [step, setStep] = useState(1);

    // Step 1: Personal
    const [age, setAge] = useState("30");
    const [income, setIncome] = useState("1200000");
    const [expenses, setExpenses] = useState("35000");
    const [riskProfile, setRiskProfile] = useState("moderate");

    // Step 2: Financial
    const [emergencyFund, setEmergencyFund] = useState("100000");
    const [healthInsurance, setHealthInsurance] = useState("500000");
    const [lifeInsurance, setLifeInsurance] = useState("5000000");
    const [debtEmi, setDebtEmi] = useState("0");

    // Step 3: Investments
    const [investments, setInvestments] = useState([{ type: "Mutual Funds", amount: 200000 }]);

    // Step 4: Goals
    const [goals, setGoals] = useState([{ type: "Retirement", target: 50000000, years: 25 }]);

    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    function addInvestment() {
        setInvestments([...investments, { type: "Stocks", amount: 50000 }]);
    }

    function removeInvestment(i: number) {
        setInvestments(investments.filter((_, idx) => idx !== i));
    }

    function addGoal() {
        setGoals([...goals, { type: "House", target: 5000000, years: 10 }]);
    }

    function removeGoal(i: number) {
        setGoals(goals.filter((_, idx) => idx !== i));
    }

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const data = await submitOnboarding({
                age: Number(age),
                income: Number(income),
                expenses: Number(expenses),
                investments: investments.map((inv) => ({ type: inv.type, amount: inv.amount })),
                goals: goals.map((g) => ({ type: g.type, target: g.target, years: g.years })),
                risk_profile: riskProfile,
                emergency_fund: Number(emergencyFund),
                health_insurance: Number(healthInsurance),
                life_insurance: Number(lifeInsurance),
                debt_emi: Number(debtEmi),
            });
            setResult(data);
            setStep(5);
        } catch {
            setError("Failed to submit onboarding. Is the backend running?");
        } finally {
            setLoading(false);
        }
    }

    const progress = Math.min((step / 4) * 100, 100);

    return (
        <section className="card">
            <h2>🚀 Onboarding – FIRE Path Planner</h2>
            <p className="muted">
                Complete this 4-step form to get your Money Health Score and personalized FIRE roadmap.
            </p>
            <p className="disclaimer">
                ⚠️ This is for educational purposes only. Consult a SEBI-registered advisor.
            </p>

            {/* Progress bar */}
            <div className="progress-bar-track">
                <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="muted" style={{ textAlign: "center", marginTop: 4 }}>
                {step <= 4 ? `Step ${step} of 4` : "Complete ✅"}
            </p>

            {step <= 4 && (
                <form className="form-grid" onSubmit={handleSubmit}>
                    {step === 1 && (
                        <>
                            <h3 className="full-width">👤 Personal Details</h3>
                            <label>Age<input type="number" value={age} onChange={(e) => setAge(e.target.value)} /></label>
                            <label>Annual Income (₹)<input type="number" value={income} onChange={(e) => setIncome(e.target.value)} /></label>
                            <label>Monthly Expenses (₹)<input type="number" value={expenses} onChange={(e) => setExpenses(e.target.value)} /></label>
                            <label>
                                Risk Profile
                                <select value={riskProfile} onChange={(e) => setRiskProfile(e.target.value)}>
                                    <option value="conservative">Conservative</option>
                                    <option value="moderate">Moderate</option>
                                    <option value="aggressive">Aggressive</option>
                                </select>
                            </label>
                            <button type="button" className="full-width" onClick={() => setStep(2)}>Next →</button>
                        </>
                    )}

                    {step === 2 && (
                        <>
                            <h3 className="full-width">🛡️ Financial Safety Net</h3>
                            <label>Emergency Fund (₹)<input type="number" value={emergencyFund} onChange={(e) => setEmergencyFund(e.target.value)} /></label>
                            <label>Health Insurance Cover (₹)<input type="number" value={healthInsurance} onChange={(e) => setHealthInsurance(e.target.value)} /></label>
                            <label>Life Insurance Cover (₹)<input type="number" value={lifeInsurance} onChange={(e) => setLifeInsurance(e.target.value)} /></label>
                            <label>Monthly Debt EMI (₹)<input type="number" value={debtEmi} onChange={(e) => setDebtEmi(e.target.value)} /></label>
                            <div className="full-width step-nav">
                                <button type="button" onClick={() => setStep(1)}>← Back</button>
                                <button type="button" onClick={() => setStep(3)}>Next →</button>
                            </div>
                        </>
                    )}

                    {step === 3 && (
                        <>
                            <h3 className="full-width">💰 Existing Investments</h3>
                            {investments.map((inv, i) => (
                                <div key={i} className="full-width inline-row">
                                    <select value={inv.type} onChange={(e) => {
                                        const n = [...investments];
                                        n[i] = { ...n[i], type: e.target.value };
                                        setInvestments(n);
                                    }}>
                                        {INVESTMENT_TYPES.map((t) => <option key={t}>{t}</option>)}
                                    </select>
                                    <input type="number" placeholder="Amount" value={inv.amount} onChange={(e) => {
                                        const n = [...investments];
                                        n[i] = { ...n[i], amount: Number(e.target.value) };
                                        setInvestments(n);
                                    }} />
                                    <button type="button" className="btn-sm btn-danger" onClick={() => removeInvestment(i)}>✕</button>
                                </div>
                            ))}
                            <button type="button" className="full-width btn-outline" onClick={addInvestment}>+ Add Investment</button>
                            <div className="full-width step-nav">
                                <button type="button" onClick={() => setStep(2)}>← Back</button>
                                <button type="button" onClick={() => setStep(4)}>Next →</button>
                            </div>
                        </>
                    )}

                    {step === 4 && (
                        <>
                            <h3 className="full-width">🎯 Financial Goals</h3>
                            {goals.map((g, i) => (
                                <div key={i} className="full-width inline-row">
                                    <select value={g.type} onChange={(e) => {
                                        const n = [...goals];
                                        n[i] = { ...n[i], type: e.target.value };
                                        setGoals(n);
                                    }}>
                                        {GOAL_TYPES.map((t) => <option key={t}>{t}</option>)}
                                    </select>
                                    <input type="number" placeholder="Target ₹" value={g.target} onChange={(e) => {
                                        const n = [...goals];
                                        n[i] = { ...n[i], target: Number(e.target.value) };
                                        setGoals(n);
                                    }} />
                                    <input type="number" placeholder="Years" value={g.years} onChange={(e) => {
                                        const n = [...goals];
                                        n[i] = { ...n[i], years: Number(e.target.value) };
                                        setGoals(n);
                                    }} />
                                    <button type="button" className="btn-sm btn-danger" onClick={() => removeGoal(i)}>✕</button>
                                </div>
                            ))}
                            <button type="button" className="full-width btn-outline" onClick={addGoal}>+ Add Goal</button>
                            <div className="full-width step-nav">
                                <button type="button" onClick={() => setStep(3)}>← Back</button>
                                <button type="submit" disabled={loading}>
                                    {loading ? "Analyzing..." : "🔍 Analyze My Finances"}
                                </button>
                            </div>
                        </>
                    )}
                </form>
            )}

            {error && <p className="error-text">{error}</p>}

            {/* Results */}
            {result && step === 5 && (
                <div className="onboarding-results">
                    {/* Money Health Score */}
                    <div className="insight-panel">
                        <h3>💪 Money Health Score: {result.health_score.overall}/100</h3>
                        <div className="radar-grid">
                            {Object.entries(result.health_score as Record<string, number>)
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
                                        <span className="muted">{v}/100</span>
                                    </div>
                                ))}
                        </div>
                    </div>

                    {/* FIRE Roadmap */}
                    <div className="insight-panel">
                        <h3>🗺️ 12-Month FIRE Roadmap</h3>
                        <div className="roadmap-timeline">
                            {(result.roadmap as any[]).map((item: any) => (
                                <div key={item.month} className="roadmap-month">
                                    <div className="roadmap-month-header">
                                        <strong>Month {item.month}</strong>
                                        <span className="muted">SIP: ₹{item.sip_amount?.toLocaleString("en-IN")}</span>
                                    </div>
                                    <ul>
                                        {(item.actions as string[]).map((action: string, j: number) => (
                                            <li key={j}>{action}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        className="full-width"
                        style={{ marginTop: 16, padding: "12px", background: "#0e6ba8", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontSize: "1rem" }}
                        onClick={() => { setStep(1); setResult(null); }}
                    >
                        ↻ Start Over
                    </button>
                </div>
            )}
        </section>
    );
}
