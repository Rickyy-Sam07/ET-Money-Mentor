# 📘 ET Money Mentor: Final Project Report
### *A Comprehensive AI-Driven Personal Finance Operating System*

**Authors:**  
- **Yash Gupta** (Lead AI & Backend Architect)  
- **Sambhranta Ghosh** (Full-Stack & UI/UX Specialist)

**Date:** March 30, 2026  
**Status:** Version 1.0 (Production-Ready)

---

## 📑 Table of Contents
1. [Abstract](#1-abstract)
2. [Problem Statement & Vision](#2-problem-statement--vision)
3. [Architecture & System Design](#3-architecture--system-design)
4. [Functional Modules (The 13 Pillars)](#4-functional-modules-the-13-pillars)
5. [Technical Implementation Details](#5-technical-implementation-details)
6. [Design Philosophy & UX](#6-design-philosophy--ux)
7. [Security & Privacy Protocols](#7-security--privacy-protocols)
8. [Phase 2: Future Roadmap](#8-phase-2-future-roadmap)
9. [Conclusion](#9-conclusion)

---

## 1. Abstract
**ET Money Mentor** is an automated financial counseling system that bridges the gap between complex financial data and actionable user insight. By integrating **Large Language Models (Llama 3.3)**, **STT/TTS engines (Sarvam AI)**, and **Computer Vision (PaddleOCR)**, the project creates a unified ecosystem for wealth tracking, tax planning, and strategic investment guidance. This report details the technical architecture, design considerations, and functional capabilities of the platform.

## 2. Problem Statement & Vision
Modern personal finance is fragmented. Users manage wealth across multiple apps (Banks, Brokers, Tax portals, News sites), leading to "Data-Fatigue."
- **Complexity:** Indian Tax regimes and portfolio overlap are difficult for non-specialists to calculate.
- **Accessibility:** Most finance apps require heavy manual entry.
- **Motivation:** To build a "Hands-Free" financial mentor that talks to you, reads your documents, and simulates your future milestones.

---

## 3. Architecture & System Design

### 3.1 Frontend Layer (The Interface)
- **Framework:** React 18 with TypeScript for type safety.
- **Build Tool:** Vite for sub-second hot module replacement.
- **State Management:** Zustand to manage 13+ module states with zero boilerplate.
- **Routing:** React Router v6 for a single-page application (SPA) experience.

### 3.2 Backend Layer (The Logic)
- **Framework:** FastAPI (Python), chosen for its asynchronous performance and auto-generated OpenAPI docs.
- **ORM:** SQLAlchemy with PostgreSQL for high-concurrency data persistence.
- **API Design:** RESTful structure with session-based authentication.

### 3.3 Cognitive Layer (The Intelligence)
- **LLM Engine:** Groq (Llama 3.3-70B) for 200+ token/sec inference speeds.
- **Voice Engine:** Sarvam AI for state-of-the-art multilingual STT/TTS.
- **Vision Engine:** PaddleOCR for localized document text extraction.
- **Market Data:** NewsData.io for real-time sector-specific news feeds.

---

## 4. Functional Modules (The 13 Pillars)

### 4.1 Core Center
1. **Unified Dashboard:** Real-time data visualization of the "Financial Health Score."
2. **Onboarding:** Captures risk tolerance, liabilities, and multi-asset goals.
3. **Voice Hub:** Hands-free finance via natural language spoken commands.
4. **Smart Upload:** Automated ingestion of bank statements/Form 16s.
5. **Intelligent Report:** Consolidates all 13 modules into a printable summary.

### 4.2 Analytical Systems
6. **Tax Wizard:** Comparative analysis of Old vs. New Indian Income Tax regimes.
7. **Portfolio X-Ray:** Calculates mutual fund overlap and benchmark performance (XIRR).
8. **News Radar:** An AI filter that removes noise and highlights portfolio-linked news.
9. **Recommendations Engine:** Context-aware advice (e.g., "Shift 10% to Debt for goal safety").

### 4.3 Life Planning Tools
10. **Life-Event Simulation:** Models major life events (Home, Marriage, Kid) on current cash flows.
11. **Couple Planner:** Merges two distinct profiles for joint retirement and goal planning.
12. **What-If Simulator:** Stress-tests portfolios against market crashes or income shocks.
13. **Emergency Bot:** A triage AI for immediate crisis mitigation.

---

## 5. Technical Implementation Details

### 5.1 Voice Processing Workflow
1. User speaks in **Hinglish** (Hindi/English mix).
2. **Sarvam AI** captures the stream and converts it to text.
3. **Groq LLM** identifies the intent (e.g., `INTENT: TAX_QUERY`).
4. Backend fetches relevant tax data from PostgreSQL.
5. LLM generates a concise spoken response.
6. **Sarvam TTS** speaks the answer back.

### 5.2 Portfolio Overlap Algorithm
The system indexes every stock within your mutual fund holdings. It then performs a **set-intersection operation** to find overlaps, alerting users if they are unknowingly exposed to the same stock via multiple funds.

### 5.3 Tax Regime Simulator
Implements the specific deduction rules for **Section 80C, 80D, and HRA**. It iterates through both tax slabs and dynamically recommends the regime that yields the highest post-tax income.

---

## 6. Design Philosophy & UX

### 6.1 Glassmorphism
The UI uses **translucent layers** with background blurs to create depth. This aesthetic makes the financial data feel "fluid" rather than static and boring.
- **Color Palette:** Deep Sapphire (Primary), Emerald (Growth), Crimson (Risk).

### 6.2 Responsive Motion
Every chart and link transition is animated to reduce cognitive friction. The app feels "alive"—a critical factor for long-term user retention in financial tools.

---

## 7. Security & Privacy Protocols
- **Local Data-First:** Personal financial data resides on the user's controlled instance.
- **Anonymized LLM Calls:** Only necessary financial metadata is sent to the LLM (Groq), with PII (Personally Identifiable Information) stripped at the API layer.
- **Encrypted Env:** All API keys are stored in encrypted environment variables.

---

## 8. Phase 2: Future Roadmap

1. **Direct Broker API:** Live integration with Indian brokers (Zerodha/Upstox/Groww) for automated portfolio sync.
2. **Predictive Budgeting:** Using historical spending patterns to predict future liquidity crunches.
3. **Smart Invoicing:** OCR for utility bills with automated payment reminders.
4. **Cross-Border Tax:** Support for NRI (Non-Resident Indian) tax laws and foreign asset reporting.

---

## 9. Conclusion
**ET Money Mentor** succeeds in commoditizing high-end financial advice. By integrating AI at the core, we have moved from a "Calculator" to an "Advisor." The platform is ready for scale, providing a robust, premium, and secure framework for the future of personal wealth management.

---

<div align="center">
**Yash Gupta & Sambhranta Ghosh**  
*Lead Developers*  
[Project Repository](https://github.com/Rickyy-Sam07/ET-Money-Mentor)
</div>
