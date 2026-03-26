# Dev2 Integration Checklist

Use this checklist while merging Dev1 and Dev2 branches.

## 1. Session & Profile Contract

- Confirm both apps use one shared `session_id` in browser storage.
- Confirm Dev2 onboarding writes profile values through `POST /api/user/update`.
- Confirm Dev2 reads profile bootstrap from `GET /api/user`.

## 2. API Compatibility

- Keep these Dev1 endpoints reachable with same payload contracts:
  - `POST /api/voice/process`
  - `POST /api/upload`
  - `POST /api/tax/analyze`
  - `POST /api/portfolio/analyze`
  - `GET /api/news/query`
- Keep shared endpoints stable:
  - `POST /api/session/start`
  - `GET /api/user`
  - `POST /api/user/update`

## 3. UI Routing Merge

- Merge routes from Dev2 into [frontend/src/App.tsx](frontend/src/App.tsx).
- Preserve Dev1 pages under:
  - `/voice`
  - `/upload`
  - `/tax`
  - `/portfolio`
  - `/news`
- Add links for Dev2 pages in [frontend/src/components/NavBar.tsx](frontend/src/components/NavBar.tsx).

## 4. Data Flow Scenarios to Test

- Onboarding (Dev2) -> Tax Wizard (Dev1) should show meaningful prefill.
- Onboarding (Dev2) -> Portfolio X-Ray (Dev1) should use same session.
- Portfolio analysis (Dev1) -> News (Dev1) should show relevant warning cards.
- Dev2 roadmap save -> `GET /api/user` should expose goals/investments updates.

## 5. Guardrails & Compliance

- Verify disclaimer appears on every final merged page.
- Verify outputs do not contain prohibited phrases like "guaranteed returns".
- Verify failures return non-breaking UI messages (no white screen).

## 6. Demo Readiness

- Start backend and frontend locally and run one full scripted flow.
- Keep one backup demo path using text input fallback if mic/browser permissions fail.
- Freeze API contracts before final merge to reduce last-hour breakage.
