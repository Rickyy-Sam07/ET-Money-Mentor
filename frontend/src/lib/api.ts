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

// ── Dev2 API functions ──────────────────────────────────────

export async function submitOnboarding(payload: {
  age: number;
  income: number;
  expenses: number;
  investments: Array<Record<string, unknown>>;
  goals: Array<Record<string, unknown>>;
  risk_profile: string;
  emergency_fund: number;
  health_insurance: number;
  life_insurance: number;
  debt_emi: number;
}) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/onboarding/submit", {
    session_id: sessionId,
    ...payload,
  });
  return data;
}

export async function adviseLifeEvent(payload: {
  event_type: string;
  amount: number;
  timing?: string;
}) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/life-event/advise", {
    session_id: sessionId,
    ...payload,
  });
  return data;
}

export async function optimizeCouple(partner1: Record<string, unknown>, partner2: Record<string, unknown>) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/couple/optimize", {
    session_id: sessionId,
    partner1,
    partner2,
  });
  return data;
}

export async function simulateWhatIf(scenario: string, amount: number) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/whatif/simulate", {
    session_id: sessionId,
    scenario,
    amount,
  });
  return data;
}

export async function respondEmergency(crisis_type: string, details: string) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/emergency/respond", {
    session_id: sessionId,
    crisis_type,
    details,
  });
  return data;
}

export async function getRecommendations() {
  const sessionId = await ensureSession();
  const { data } = await api.get("/api/recommendations", {
    params: { session_id: sessionId },
  });
  return data;
}

export async function updateProfile(payload: {
  age?: number;
  income?: number;
  expenses?: number;
  investments?: Array<Record<string, unknown>>;
  goals?: Array<Record<string, unknown>>;
  risk_profile?: string;
}) {
  const sessionId = await ensureSession();
  const { data } = await api.post("/api/user/update", {
    session_id: sessionId,
    ...payload,
  });
  return data;
}
