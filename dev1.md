We’ll now provide a **detailed step** ‑ **by** ‑ **step plan** for **Dev1** , covering frontend, backend, and AI work across
the 3‑day hackathon. This plan assumes the shared context with Dev2 (common user session, database,
API contracts) and focuses on Dev1’s ve feature areas:

```
. Voice Agent – auto language detection, mode switching (Agent/Ask), conversation log with
subtitles.
. Document Upload – Form 16 and portfolio screenshots (OCR + manual entry).
. Tax Wizard – deductions, regime comparison, investment suggestions.
. Mutual Fund Portfolio X ‑ Ray – XIRR, overlap, expense ratio, rebalancing.
. RAG for Real ‑ time News & Warnings – relevant news retrieval and alerts.
```
# 🗓 Day 1: Foundation & Core Setup

## Morning – Shared Infrastructure & API Contracts

```
Set up project structure
```
```
Create a monorepo or separate folders for frontend and backend.
Initialize Git, create dev1 branch for isolated development.
Agree on database schema with Dev2:
users table: id, session_id, created_at, last_active.
profiles table: user_id, age, income, expenses, investments (JSON), goals (JSON),
risk_prole, etc.
tax_data table: user_id, form16_data (JSON), deductions (JSON), regime_choice,
etc.
portfolio table: user_id, holdings (JSON), xirr, overlap, expense_ratio, benchmark.
API contracts (to be implemented by both):
POST /api/session/start – returns session_id.
GET /api/user – returns current prole.
POST /api/user/update – updates prole (used by both).
GET /api/health – health check.
Use FastAPI for backend, SQLite (dev) / PostgreSQL (prod).
```
```
Frontend foundation
```
```
Choose React with TypeScript (or Vue).
Set up routing (React Router) with pages:
/ – Dashboard (shared with Dev2 later).
/voice – Voice chat page.
```

```
/upload – Document upload.
/tax – Tax Wizard.
/portfolio – Portfolio X‑Ray.
/news – News & warnings.
Create a common NavBar linking to these pages.
Implement shared state management (e.g., Zustand or Context) for user session.
```
## Afternoon – Voice Agent

```
Backend: Voice endpoint
```
```
Create POST /api/voice/process accepting:
audio (base64 or multipart) or text (if user typed).
language (optional, auto‑detected).
mode ("agent" or "ask").
Use Whisper (via OpenAI API or local whisper.cpp) for speech‑to‑text.
Language detection: use langdetect or Whisper’s detected language.
For TTS, use pyttsx3 (oine) or a cloud service (optional).
Intent routing : For "agent" mode, the backend maintains a state machine to guide through
steps (e.g., collect age → income → expenses). For "ask" mode, send to a generic LLM with
system prompt.
Store conversation history in session.
```
```
Frontend: Voice chat page
```
```
Use navigator.mediaDevices.getUserMedia for microphone access.
Record audio as WAV/MP3, send to /voice/process.
Display conversation log with both user and agent messages.
Add a mode toggle (Agent/Ask) and a language selector (optional).
Show subtitles for each turn.
Add a text input fallback.
```
## Evening – Document Upload & OCR

```
Backend: Upload endpoint
```
```
POST /api/upload accepts le (image/PDF).
Use Tesseract.js (if frontend OCR) or Google Vision API / Azure Form Recognizer (backend).
Extract text, then use LLM (e.g., Llama 3) to parse into structured JSON (for Form 16: salary,
deductions, etc.; for portfolio: fund names, units, NAV).
Return structured data to frontend for preview and manual correction.
```

```
Frontend: Upload page
```
```
Drag‑and‑drop area for images/PDFs.
After upload, show extracted elds with editable forms.
Allow manual entry if user prefers not to upload.
Store the nal data in user prole via /api/user/update.
```
# 🗓 Day 2: Core AI Features & Integration

## Morning – Tax Wizard

```
Backend: Tax analysis endpoint
```
```
POST /api/tax/analyze accepts Form 16 data (either from upload or manual).
Compute deductions: parse Form 16 sections (80C, 80D, etc.) and compare with user’s
declared investments. Identify missed deductions.
Compare old vs. new tax regime with user’s numbers.
Generate ranked list of tax‑saving investments (ELSS, PPF, NPS, etc.) with risk/liquidity
indicators.
Use LLM to generate plain‑English explanations with citations (e.g., “Section 80C allows
₹1.5L deduction – you have used only ₹40k”).
Store results in tax_data table.
```
```
Frontend: Tax Wizard page
```
```
Show Form 16 summary (editable).
Display deductions list with checkboxes for missing ones.
Interactive slider to switch between old/new regime, showing tax liability.
Cards for suggested investments: each card shows risk, liquidity, expected return, and a
“Learn more” button.
Allow user to accept suggestions, which updates the nancial roadmap.
```
## Afternoon – Mutual Fund Portfolio X ‑ Ray

```
Backend: Portfolio analysis endpoint
```
```
POST /api/portfolio/analyze accepts portfolio data (from uploaded statement or
manual).
Reconstruct portfolio: fund names, units, NAV, date of investment.
Compute XIRR using numpy.irr or custom function (requires cash ows).
```

```
Overlap analysis : compare fund holdings using pre‑computed overlap matrix (use data from
AMFI or a public dataset).
Expense ratio drag : sum expense ratios × AUM, compare to category average.
Benchmark comparison : compare returns with Nifty 50 TRI or category benchmark.
Rebalancing suggestions : identify overlapping funds, high‑expense funds, and suggest
switches.
Return JSON with all metrics and recommendations.
```
```
Frontend: Portfolio X ‑ Ray page
```
```
Upload area for CAMS/KFintech statements (PDF/txt).
Show portfolio reconstruction in a table (fund name, units, NAV, current value).
Visualizations:
XIRR gauge (poor/good/excellent).
Overlap donut chart (percentage overlap).
Expense ratio drag bar chart.
Benchmark comparison line chart (portfolio vs. benchmark).
Display rebalancing plan with suggested changes and estimated impact.
User can accept suggestions, which updates the roadmap.
```
## Evening – RAG for News & Warnings

```
Backend: News retrieval & alert
```
```
Build a vector store (Chroma) with pre‑indexed nancial news (use a public dataset or scrape
ET/Moneycontrol).
Use all-MiniLM-L6-v2 for embeddings.
GET /api/news/query takes user context (e.g., portfolio holdings, goals) and returns
top‑k relevant news items with relevance scores.
For warnings: if news contains keywords like “downgrade”, “sell”, “fraud” related to user’s
holdings, ag as warning.
Use LLM to generate a summary and potential impact.
```
```
Frontend: News widget (integrated into dashboard)
```
```
Display a sidebar or modal showing latest relevant news.
Highlight warnings with red background.
Allow user to expand for more details.
```
# 🗓 Day 3: Integration, Polish & Final Demo


## Morning – Integration with Dev

```
Combine frontend : Merge Dev1’s pages into the main app, ensure routing works.
Unify user session : Both must use the same session ID stored in localStorage/cookie.
Test cross ‑ feature ows :
User completes onboarding (Dev2) → goes to Tax Wizard (Dev1) → sees pre‑lled data.
User uploads Form 16 → Tax Wizard uses it → updates prole.
User runs Portfolio X‑Ray → news widget (Dev1) shows relevant warnings.
Fix API discrepancies : Ensure both use the same base URL, authentication (if any), and error
handling.
```
## Afternoon – Polish & Performance

### UI/UX

```
Add loading spinners for long operations.
Error messages for failed uploads or API calls.
Responsive design for mobile view.
Performance
Cache user prole in frontend to avoid repeated fetches.
Use debouncing for voice input.
Optimize OCR and LLM calls (batch where possible).
Guardrails
Add disclaimer on every page: “This is for educational purposes only. Consult a
SEBI‑registered advisor.”
Block any output that contains “guaranteed returns”.
```
## Evening – Final Deliverables

```
GitHub : Commit all code with descriptive messages. Write a README with setup instructions,
environment variables, and run commands.
3 ‑ minute pitch video : Record a walkthrough showing the entire journey:
Start with voice onboarding (Agent mode) → upload Form 16 → Tax Wizard → upload
portfolio → X‑Ray → news warnings → accept rebalancing → (optional) switch to Ask mode
for a question.
Architecture document : 1–2 page PDF with diagram (agents, data ow, error handling) and
description.
Impact model : Spreadsheet with assumptions and quantications (time saved, tax saved, returns
improved, etc.).
```

# 🔧 Technical Stack for Dev

```
Area Technology Choices
Backend FastAPI (Python), SQLAlchemy, SQLite (dev) / PostgreSQL (prod)
LLM Together AI (Llama 3) or OpenAI (if permitted) – with fallback to local Ollama
Voice Whisper (OpenAI API or local), pyttsx3 (TTS), langdetect
OCR Google Vision API (free tier) or Tesseract.js on frontend
RAG Chroma (vector DB), all-MiniLM-L6-v2 (sentence-transformers), LangChain
Frontend React + TypeScript, React Router, Axios, Zustand, Chart.js / Recharts
Deployment Vercel (frontend), Render or Railway (backend), PostgreSQL on Render
```
# 📌 API Endpoints (Dev1 Responsibility)

```
Method Endpoint Description
```
```
POST s/api/voice/proces Accepts audio/text, returns agent response (with mode,language).
```
```
POST /api/upload Accepts le, returns structured data.
```
```
POST /api/tax/analyze Accepts Form 16 data, returns deductions, regimecomparison, suggestions.
```
```
POST lyze/api/portfolio/ana Accepts portfolio data, returns XIRR, overlap, expense ratio,rebalancing.
```
```
GET /api/news/query Returns relevant news based on user context.
```
All endpoints will also update the user prole as needed (via /api/user/update shared with Dev2).

This plan ensures Dev1 can work independently for most of the hackathon while staying aligned with
Dev2 through shared APIs and the user session. Good luck!


