# 📄 ET Money Mentor: Technical Project Report
**Version:** 1.0.0  
**Date:** March 30, 2026  
**Authors:** Yash Gupta, Sambhranta Ghosh

---

## 1. Executive Summary
**ET Money Mentor** is an automated, AI-driven financial counseling ecosystem. It addresses the complexity of modern personal finance by centralizing fragmented data (Tax, Portfolio, News, Goals) and providing a natural interface via voice and text. By utilizing **Llama 3.3 (Large Language Model)** and **Sarvam AI (Voice)**, the platform transitions from simple data tracking to proactive financial mentoring.

## 2. Technical Architecture

### 2.1 Technology Stack
- **Frontend Layer:** React 18, TypeScript, Zustand (State), CSS-in-JS (Modern UI).
- **Service Layer:** FastAPI (Asynchronous Python), Pydantic (Data Validation).
- **Data Layer:** PostgreSQL, SQLAlchemy Core/ORM.
- **Cognitive Layer:** Groq (LLM Inference), Sarvam AI (STT/TTS Engine), PaddleOCR (Computer Vision).

### 2.2 System Flow
The system operates on an event-driven loop:
1. **Ingestion:** Data is received via user input, document upload (OCR), or live API feeds (NewsData).
2. **Contextualization:** The **Onboarding Profile** provides the necessary metadata (Risk, Income, Goals) to context-bind the AI.
3. **Inference:** The **Groq LLM** processes the data against financial logic to generate structured advice.
4. **Interaction:** Results are delivered via **Glassmorphic UI** or synthesized **Sarvam Voice** replies.

---

## 3. Module Breakdown

### 3.1 AI Voice Command Center
Utilizes **Sarvam AI's multilingual support** to allow users to query their financial state naturally. 
- **Achievement:** High accuracy in capturing financial terminology in mixed-code languages (Hinglish).

### 3.2 Tax Analysis & Simulator
A robust logical engine that parses Form 16 text.
- **Mathematical Model:** Implements the latest Indian Income Tax Act rules for 2024-25.
- **Impact:** Automates hours of manual tax calculation in seconds.

### 3.3 Portfolio X-Ray Engine
Goes beyond simple price tracking.
- **Overlap Logic:** Specifically designed to calculate percentage-wise commonality between mutual fund holdings to prevent over-diversification.
- **Benchmarks:** Real-time comparison with Nifty 50 and S&P 500.

### 3.4 Crisis Chatbot (Emergency)
A safety-first agent designed to mitigate panic-selling or emotional financial decisions.
- **Knowledge Base:** Integrated with standard financial crisis protocols.

---

## 4. Design Philosophy
The application adheres to **Glassmorphism**—a design trend that uses transparency, background blurs, and vibrant colors to create a "premium" feel. 
- **Dark Mode Native:** Designed to reduce cognitive load and eye strain during deep financial analysis.
- **Accessibility:** Integrated Voice as a primary citizen for hands-free navigation.

## 5. Security & Privacy
- **Stateless Intelligence:** AI models do not "save" user data permanently; data is stored in a secure local PostgreSQL instance owned by the user.
- **Session-Based:** Access for unique sessions ensures data isolation.

## 6. Future Roadmap
1. **Direct Broker Integration:** Automating data pull from Zerodha/Upstox via OAuth.
2. **Multi-Agent Orchestration:** Using LangGraph to let different AI agents (Tax Agent, Portfolio Agent) collaborate on complex queries.
3. **Predictive Analytics:** Moving from "What-If" to "Will-Be" using historical market trend modeling.

---

<div align="center">
**End of Report**
</div>
