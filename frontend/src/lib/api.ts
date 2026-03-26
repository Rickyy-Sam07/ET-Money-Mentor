import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
});

export type SessionData = { session_id: string };

export async function ensureSession(): Promise<string> {
  const existing = localStorage.getItem("session_id");
  if (existing) {
    return existing;
  }
  const { data } = await api.post<SessionData>("/api/session/start");
  localStorage.setItem("session_id", data.session_id);
  return data.session_id;
}

export async function getProfile() {
  const sessionId = await ensureSession();
  const { data } = await api.get("/api/user", { params: { session_id: sessionId } });
  return data;
}

export async function processVoice(payload: {
  text: string;
  language?: string;
  mode: "agent" | "ask";
}) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/voice/process", {
    session_id: sessionId,
    text: payload.text,
    language: payload.language,
    mode: payload.mode,
  });
  return data;
}

export async function uploadDocument(file: File) {
  const sessionId = await ensureSession();
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/api/upload", formData, {
    params: { session_id: sessionId },
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function analyzeTax(form16Data: Record<string, unknown>, regimePreference: "old" | "new") {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/tax/analyze", {
    session_id: sessionId,
    form16_data: form16Data,
    regime_preference: regimePreference,
  });
  return data;
}

export async function analyzePortfolio(holdings: Array<Record<string, unknown>>) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/portfolio/analyze", {
    session_id: sessionId,
    holdings,
  });
  return data;
}

export async function getNews() {
  const sessionId = await ensureSession();
  const { data } = await api.get("/api/news/query", {
    params: { session_id: sessionId },
  });
  return data;
}
