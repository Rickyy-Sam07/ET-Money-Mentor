# ET Money Mentor Backend (Dev1)

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variable for Sarvam:

```bash
copy .env.example .env
# then edit .env and set:
# SARVAM_API_SUBSCRIPTION_KEY=your_key_here
# GROQ_API_KEY=your_key_here
# NEWSDATA_API_KEY=your_key_here
# ENABLE_TTS=false  # set true only when you want mentor audio replies
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
- `POST /api/voice/process-audio?session_id=...&mode=agent&language=hi`
- `POST /api/upload?session_id=...`
- `POST /api/tax/analyze`
- `POST /api/portfolio/analyze`
- `GET /api/news/query?session_id=...`
