# DEV1 Handoff — Merge Guide for Dev2

Every file owned by Dev1 has a `// [DEV1]` (frontend) or `# [DEV1]` (backend) comment on line 1.
**Do not rename any file.** Imports are wired by filename — renaming breaks everything.

---

## Ownership Map

### Frontend — `frontend/src/`

| File | Owner | Dev2 merge instruction |
|---|---|---|
| `App.tsx` | DEV1 | Add your `<Route>` entries inside `<Routes>`. Do not remove existing routes. |
| `components/NavBar.tsx` | DEV1 | Add your nav links to the `links` array. |
| `components/VoiceCommandCenter.tsx` | DEV1 | Do not modify. |
| `lib/api.ts` | DEV1 | Append your API functions at the bottom. Do not modify existing functions. |
| `lib/voiceState.ts` | DEV1 | Append your own `KEYS` entries and save/load functions at the bottom. |
| `pages/DashboardPage.tsx` | DEV1 | Add your widgets inside the card, below the existing `insight-panel` sections. |
| `pages/VoicePage.tsx` | DEV1 | Do not modify. |
| `pages/UploadPage.tsx` | DEV1 | Do not modify. |
| `pages/TaxPage.tsx` | DEV1 | Do not modify. |
| `pages/PortfolioPage.tsx` | DEV1 | Do not modify. |
| `pages/NewsPage.tsx` | DEV1 | Do not modify. |
| `pages/ReportPage.tsx` | DEV1 | Do not modify. |
| `styles.css` | DEV1 | Append your CSS classes at the bottom. Do not modify existing classes. |

### Backend — `backend/app/`

| File | Owner | Dev2 merge instruction |
|---|---|---|
| `routes/api.py` | DEV1 | Add your routes at the **bottom** of the file only. Do not modify existing routes. |
| `schemas.py` | DEV1 | Append your Pydantic models at the bottom. |
| `db/models.py` | DEV1 | Append your SQLAlchemy table classes at the bottom. |
| `services/groq_service.py` | DEV1 | Do not modify. |
| `services/sarvam_service.py` | DEV1 | Do not modify. |
| `services/voice_service.py` | DEV1 | Do not modify. |
| `services/upload_service.py` | DEV1 | Do not modify. |
| `services/tax_service.py` | DEV1 | Do not modify. |
| `services/portfolio_service.py` | DEV1 | Do not modify. |
| `services/news_service.py` | DEV1 | Do not modify. |
| `services/newsdata_service.py` | DEV1 | Do not modify. |

---

## Shared Contracts Dev2 Must Respect

### Session
- Session ID is stored in `localStorage` under key `"session_id"`.
- Always call `ensureSession()` from `lib/api.ts` to get/create it.
- Pass `session_id` to every backend API call.

### API Base URL
- Set in `frontend/.env` as `VITE_API_BASE_URL=http://127.0.0.1:8000`
- All routes are prefixed `/api/`

### localStorage Keys (Dev1 owns these — do not reuse)
```
et_tax_input
et_tax_result
et_portfolio_input
et_portfolio_result
et_news_items
et_upload_payload
et_unified_report
```
Dev2: use a different prefix for your keys, e.g. `et2_onboarding`, `et2_goals`, etc.

### Database Tables (Dev1 owns these — do not alter)
```
users       — id, session_id, created_at, last_active
profiles    — user_id, age, income, expenses, investments, goals, risk_profile
tax_data    — user_id, form16_data, deductions, regime_choice
portfolio   — user_id, holdings, xirr, overlap, expense_ratio, benchmark
```

### Existing API Endpoints (do not duplicate)
```
GET  /api/health
POST /api/session/start
GET  /api/user
POST /api/user/update
POST /api/voice/process
POST /api/voice/process-audio
POST /api/voice/resolve-command
POST /api/upload
POST /api/tax/analyze
POST /api/portfolio/analyze
GET  /api/news/query
```

---

## Environment Variables Dev2 Needs to Know About

```
GROQ_API_KEY          — LLM (Groq/Llama 3.3)
SARVAM_API_SUBSCRIPTION_KEY — Sarvam STT + TTS
NEWSDATA_API_KEY      — Live news feed
ENABLE_TTS            — "true" to enable Sarvam TTS (default: false)
```

---

## Merge Steps for Dev2

1. Checkout `main` branch, pull latest Dev1 code.
2. Create your branch: `git checkout -b dev2`.
3. Add your new page files (e.g. `OnboardingPage.tsx`) — do not touch Dev1 pages.
4. In `App.tsx` — add your routes inside `<Routes>` below the existing ones.
5. In `NavBar.tsx` — add your links to the `links` array.
6. In `api.ts` — append your API functions at the bottom.
7. In `voiceState.ts` — append your keys/functions at the bottom with `et2_` prefix.
8. In `backend/app/routes/api.py` — add your routes at the bottom.
9. In `backend/app/schemas.py` — append your Pydantic models at the bottom.
10. In `backend/app/db/models.py` — append your table classes at the bottom.
11. Run `git diff` — if you see changes to any `[DEV1]` file other than the allowed append zones, revert them.
12. Test: `uvicorn app.main:app --reload` + `npm run dev` — both must start without errors.
13. Open a PR from `dev2` → `main`.
