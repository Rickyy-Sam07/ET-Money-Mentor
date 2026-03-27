import { useState } from "react";
import { respondEmergency } from "../lib/api";

/* eslint-disable @typescript-eslint/no-explicit-any */

const CRISIS_TYPES = [
    { value: "job_loss", label: "💼 Job Loss", color: "#d94040" },
    { value: "medical", label: "🏥 Medical Emergency", color: "#d4a017" },
    { value: "debt_crisis", label: "💳 Debt Crisis", color: "#c5550a" },
    { value: "market_crash", label: "📉 Market Crash", color: "#5b5ea6" },
];

export function EmergencyPage() {
    const [messages, setMessages] = useState<Array<{ role: "user" | "bot"; text: string; data?: any }>>([
        { role: "bot", text: "I'm here to help you during tough times. Select a crisis type and describe your situation." },
    ]);
    const [crisisType, setCrisisType] = useState("job_loss");
    const [details, setDetails] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleSend() {
        if (!crisisType) return;
        const userMsg = details || `I'm facing a ${crisisType.replace(/_/g, " ")} situation.`;
        setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
        setLoading(true);

        try {
            const data = await respondEmergency(crisisType, details);
            setMessages((prev) => [
                ...prev,
                {
                    role: "bot",
                    text: data.empathy_message,
                    data,
                },
            ]);
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "bot", text: "Sorry, I couldn't connect to the server. Please try again." },
            ]);
        } finally {
            setLoading(false);
            setDetails("");
        }
    }

    return (
        <section className="card emergency-card">
            <h2>🆘 Emergency Financial Chatbot</h2>
            <p className="muted">Get calm, actionable advice during a financial crisis.</p>
            <p className="disclaimer">⚠️ This is for educational purposes only. For medical/legal issues, consult professionals.</p>

            <div className="chat-container">
                <div className="chat-box">
                    {messages.map((msg, i) => (
                        <div key={i} className={msg.role === "user" ? "bubble bubble-user" : "bubble bubble-agent emergency-bubble"}>
                            <p>{msg.text}</p>
                            {msg.data && (
                                <div className="emergency-response">
                                    <p className="personal-note">{msg.data.personalised_note}</p>
                                    <h4>{msg.data.title}</h4>
                                    <div className="action-steps">
                                        {(msg.data.action_steps as any[]).map((step: any, j: number) => (
                                            <div key={j} className={`action-step priority-${step.priority}`}>
                                                <div className="step-header">
                                                    <strong>{step.action}</strong>
                                                    <span className="priority-badge">{step.priority.replace(/_/g, " ")}</span>
                                                </div>
                                                <p>{step.detail}</p>
                                                {step.link && (
                                                    <a href={step.link} target="_blank" rel="noopener noreferrer" className="resource-link">
                                                        🔗 Resource Link
                                                    </a>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                    {loading && <div className="bubble bubble-agent"><p>Thinking...</p></div>}
                </div>

                <div className="emergency-input">
                    <select
                        value={crisisType}
                        onChange={(e) => setCrisisType(e.target.value)}
                        className="crisis-select"
                    >
                        {CRISIS_TYPES.map((c) => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                        ))}
                    </select>
                    <input
                        value={details}
                        onChange={(e) => setDetails(e.target.value)}
                        placeholder="Describe your situation (optional)..."
                        onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }}
                    />
                    <button onClick={handleSend} disabled={loading}>
                        {loading ? "..." : "Send"}
                    </button>
                </div>
            </div>
        </section>
    );
}
