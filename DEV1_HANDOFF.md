# Dev1 Handoff - ET Money Mentor

This workspace now contains a runnable Dev1 implementation:

- `backend/` FastAPI API with Dev1 endpoints
- `frontend/` React + TypeScript UI with Dev1 pages

## What Is Implemented

### Backend (FastAPI)

Base URL: `http://127.0.0.1:8000`

- `GET /api/health`
- `POST /api/session/start`
- `GET /api/user?session_id=...`
- `POST /api/user/update`
- `POST /api/voice/process`
- `POST /api/upload?session_id=...`
- `POST /api/tax/analyze`
- `POST /api/portfolio/analyze`
- `GET /api/news/query?session_id=...`

Data layer:

- SQLite + SQLAlchemy models (`users`, `profiles`, `tax_data`, `portfolio`)
- Session-centric flow for cross-feature continuity

### Frontend (React)

Base URL: `http://127.0.0.1:5173`

Pages:

- `/` Dashboard
- `/voice` Voice Agent (Agent/Ask mode + conversation log)
- `/upload` Document Upload (Form16/Portfolio parser mock)
- `/tax` Tax Wizard (regime compare + deduction gaps)
- `/portfolio` Portfolio X-Ray (XIRR/overlap/expense mock analytics)
- `/news` News & warning cards

## Run Instructions

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Integration Notes for Dev2

- Session ID is created automatically in frontend and reused for all endpoints.
- Dev2 can consume `GET /api/user` and `POST /api/user/update` for shared profile state.
- Dev1 pages already rely on shared session + profile model and can be merged into main router.
- Current AI logic is intentionally hackathon-safe prototype logic (deterministic + explainable).

## Known Prototype Limits

- Voice endpoint currently uses text input fallback and heuristic language detection.
- Upload parser is mocked extraction, not production OCR.
- Tax/portfolio/news use simplified calculation and ranking logic for rapid demo readiness.
