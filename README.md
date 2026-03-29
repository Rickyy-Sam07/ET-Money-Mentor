<div align="center">

<img src="./banner.png" alt="ET Money Mentor Banner" width="100%">

# 💰 ET Money Mentor
### *Your AI-Powered Financial Guardian & Personalized Wealth Advisor*

[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()
[![Frontend](https://img.shields.io/badge/Frontend-React%2018-61dafb.svg)]()
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)]()
[![LLM](https://img.shields.io/badge/Model-Llama%203.3%20(Groq)-orange.svg)]()
[![Voice](https://img.shields.io/badge/Voice-Sarvam%20AI-purple.svg)]()

---

**ET Money Mentor** is an industry-grade, comprehensive financial ecosystem designed to democratize wealth management. By leveraging cutting-edge AI, Voice processing, and OCR, it empowers users with actionable insights, personalized tax planning, and deep portfolio analysis—all through a seamless, premium interface.

[Explore Features](#-key-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Documentation](#-api-endpoints)

</div>

---

## 🌟 Key Features

### 🎙️ AI Voice Command Center
*   **Multilingual Support:** Interact with your mentor in English, Hindi, and more.
*   **STT & TTS:** High-fidelity speech-to-text and text-to-speech powered by Sarvam AI.
*   **Smart Resolution:** natural language processing to execute financial queries via voice.

### 📈 Advanced Portfolio Analyzer
*   **Holdings Audit:** Deep dive into your investment spread across asset classes.
*   **Performance Metrics:** Real-time XIRR calculations and benchmark comparisons.
*   **Portfolio Overlap:** Identify and reduce redundancy in your mutual fund holdings.

### 📑 Intelligent Tax Planner
*   **OCR Engine:** Automatic data extraction from Form 16 and financial documents.
*   **Regime Comparison:** Dynamic comparison between Old and New tax regimes.
*   **Deduction Optimizer:** AI-driven suggestions to maximize your tax savings.

### 📊 Unified Financial Dashboard
*   **Comprehensive Health Score:** A single metric to evaluate your financial wellness.
*   **Personalized Roadmap:** FIRE (Financial Independence, Retire Early) planning and life-event simulations.
*   **Live News Feed:** Real-time curated financial news based on your interest profile.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** [React 18](https://reactjs.org/) (TypeScript)
- **Styling:** Vanilla CSS (Glassmorphism & Dark Mode)
- **State Management:** [Zustand](https://github.com/pmndrs/zustand)
- **Build Tool:** [Vite](https://vitejs.dev/)
- **Routing:** React Router v6

### Backend
- **Core:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database:** PostgreSQL (with migrations via Alembic)
- **Authentication:** Session-based (LocalStorage-linked)

### Intelligence & Services
- **LLM:** Groq (Llama 3.3) for high-speed, intelligent reasoning.
- **Voice:** Sarvam AI (Speech-to-Text & Text-to-Speech).
- **OCR:** PaddleOCR for document data extraction.
- **News:** NewsData.io API for real-time market updates.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL Instance
- API Keys: Groq, Sarvam AI, NewsData.io

### 1. Clone the Repository
```bash
git clone https://github.com/Rickyy-Sam07/ET-Money-Mentor.git
cd ET-Money-Mentor
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --host 127.0.0.1 --port 8013 --reload
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
cp .env.example .env
# Set VITE_API_BASE_URL=http://127.0.0.1:8013
npm run dev -- --port 8014
```

---

## 📂 Project Structure

```text
ET-Money-Mentor/
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Dashboard, Voice, Tax pages
│   │   ├── lib/          # API & Voice state logic
│   │   └── styles/       # CSS modules & global styles
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── routes/       # API endpoints (Restful)
│   │   ├── services/     # AI, OCR, & News business logic
│   │   ├── db/           # Models & Database config
│   │   └── schemas/      # Pydantic models
├── artifacts/            # Generated reports & design assets
└── docs/                 # Detailed documentation
```

---

## 🔌 API Endpoints (Core)

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/session/start` | Initialize user session |
| `POST` | `/api/voice/process` | Process text command via LLM |
| `POST` | `/api/voice/process-audio` | End-to-end Voice-to-Action |
| `POST` | `/api/tax/analyze` | OCR + Tax regime analysis |
| `POST` | `/api/portfolio/analyze` | Detailed portfolio audit |
| `GET` | `/api/news/query` | Sector-specific news retrieval |

---

## 🎨 UI Design Philosophy

ET Money Mentor follows a **"Premium Dark"** aesthetic:
- **Glassmorphism:** Frosted glass effect on card components.
- **Micro-animations:** Smooth transitions for financial charts.
- **Responsiveness:** Fully optimized for Mobile, Tablet, and Desktop.
- **Accessibility:** High-contrast text and ARIA-compliant voice indicators.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Meet the Developers

| Developer | Socials |
|:---|:---|
| **Yash Gupta** | [![GitHub](https://img.shields.io/badge/GitHub-YashGupta404-black?style=flat-square&logo=github)](https://github.com/YashGupta404) |
| **Sambhranta Ghosh** | [![GitHub](https://img.shields.io/badge/GitHub-Rickky--Sam07-black?style=flat-square&logo=github)](https://github.com/Rickky-Sam07) |

---

<div align="center">
Built with ❤️ for the future of Financial Intelligence.
</div>