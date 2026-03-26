import { FormEvent, useState } from "react";
import { processVoice } from "../lib/api";

type ChatItem = { role: "user" | "agent"; text: string };

type SpeechRecognitionCtor = new () => {
  lang: string;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
};

declare global {
  interface Window {
    webkitSpeechRecognition?: SpeechRecognitionCtor;
    SpeechRecognition?: SpeechRecognitionCtor;
  }
}

export function VoicePage() {
  const [mode, setMode] = useState<"agent" | "ask">("agent");
  const [language, setLanguage] = useState("en");
  const [text, setText] = useState("");
  const [chat, setChat] = useState<ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) {
      return;
    }

    const userText = text;
    setText("");
    setChat((prev) => [...prev, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const data = await processVoice({ text: userText, language, mode });
      setChat((prev) => [...prev, { role: "agent", text: data.response }]);
    } finally {
      setLoading(false);
    }
  }

  function startMicCapture() {
    setVoiceError("");
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setVoiceError("Speech recognition is not available in this browser. Use text fallback.");
      return;
    }

    const recognition = new Recognition();
    recognition.lang = language;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    setListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript ?? "";
      setText(transcript);
    };
    recognition.onerror = (event) => {
      setVoiceError(`Mic error: ${event.error}`);
    };
    recognition.onend = () => {
      setListening(false);
    };
    recognition.start();
  }

  return (
    <section className="card">
      <h2>Voice Agent</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Mode
          <select value={mode} onChange={(e) => setMode(e.target.value as "agent" | "ask")}>
            <option value="agent">Agent</option>
            <option value="ask">Ask</option>
          </select>
        </label>

        <label>
          Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
            <option value="bn">Bengali</option>
          </select>
        </label>

        <label className="full-width">
          Text input (voice fallback)
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type what user said..." />
        </label>

        <button type="button" onClick={startMicCapture} disabled={listening || loading}>
          {listening ? "Listening..." : "Use Mic"}
        </button>
        <button type="submit" disabled={loading}>{loading ? "Processing..." : "Send"}</button>
      </form>
      {voiceError ? <p className="error-text">{voiceError}</p> : null}

      <div className="chat-box">
        {chat.map((line, idx) => (
          <div key={idx} className={line.role === "agent" ? "bubble bubble-agent" : "bubble bubble-user"}>
            <strong>{line.role === "agent" ? "Mentor" : "User"}:</strong> {line.text}
          </div>
        ))}
      </div>
    </section>
  );
}
