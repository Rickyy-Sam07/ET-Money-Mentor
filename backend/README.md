# ET Money Mentor Backend (Dev1)

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run server:

```bash
uvicorn app.main:app --reload
```

## Available Endpoints

- `GET /api/health`
- `POST /api/session/start`
- `GET /api/user?session_id=...`
- `POST /api/user/update`
- `POST /api/voice/process`
- `POST /api/upload?session_id=...`
- `POST /api/tax/analyze`
- `POST /api/portfolio/analyze`
- `GET /api/news/query?session_id=...`
