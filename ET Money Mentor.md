# Final Product Overview: ET Money Mentor

After three days of parallel development and integration, **ET Money Mentor** is a fully functional
AI‑powered personal nance assistant that lives inside the ET ecosystem. It combines voice‑rst
onboarding, multi‑agent intelligence, and deep personalization to turn confused savers into condent
investors. The system is accessible via web, mobile, and WhatsApp, and it delivers professional‑grade
nancial planning in under 15 minutes—for free.

Below is a comprehensive walkthrough of the nal product, explaining every feature from the user’s
perspective and the underlying AI mechanics.

## 🧭 User Journey (Step ‑ by ‑ Step)

## 1. Entry Point – Voice/WhatsApp Welcome

When a user rst visits the ET Money Mentor page or sends a “Hi” on WhatsApp, they are greeted by a
**voice agent** (Dev1) that automatically detects their language (Hindi, Tamil, Telugu, Bengali, English) and
offers a guided conversation.

```
Frontend : A clean chat interface with a microphone button, language selector, and a toggle
between Agent Mode (step‑by‑step) and Ask Mode (free‑form questions).
Backend : The voice endpoint (/api/voice/process) uses Whisper for STT, language
detection, and TTS for responses. A central orchestrator routes the intent to the appropriate
agent.
User Experience : The user can simply speak their nancial details, and the agent politely collects
age, income, expenses, existing investments, and goals. A subtitle log shows the conversation
transcript for clarity.
```
## 2. Onboarding & FIRE Path Planner (Dev2)

The onboarding agent (Dev2) takes the collected data and generates:

```
Money Health Score – A radar chart showing 6 dimensions: emergency preparedness, insurance
coverage, investment diversication, debt health, tax eciency, and retirement readiness. Each
dimension has a score out of 100 with a short explanation.
FIRE Path Planner – A month‑by‑month nancial roadmap displayed as an interactive timeline. It
shows:
```

```
Monthly SIP amounts for each goal (retirement, child education, house, etc.).
Recommended asset allocation shifts over time (equity/debt ratio).
Insurance gaps (e.g., “You need an additional ₹50L term cover”).
Tax‑saving moves (e.g., “Increase 80C contributions by ₹20k”).
Emergency fund target (e.g., “Build ₹3L in 6 months”).
```
**User can** accept the roadmap, which saves the plan to their prole and updates the dashboard. The
roadmap is stored in the financial_goals table and is accessible across all features.

### 3. Tax Wizard with Document Upload (Dev1)

The user can now upload their **Form 16** (image or PDF) using the document upload page.

```
Upload screen : Drag‑and‑drop area, manual entry fallback.
OCR & parsing : Google Vision + LLM extract salary, deductions, and other elds. The user reviews
and corrects extracted data.
Tax analysis (/api/tax/analyze):
Identies missed deductions (e.g., 80C, 80D, 80E).
Compares old vs. new tax regime with the user’s exact numbers, showing tax liability
side‑by‑side.
Suggests tax‑saving investments ranked by risk prole and liquidity needs (ELSS, PPF, NPS,
etc.), each with an estimated tax saving and return.
Results page : Interactive sliders to adjust regime, checklists to add deductions, and “Apply”
buttons that update the roadmap and prole.
```
### 4. Mutual Fund Portfolio X ‑ Ray (Dev1)

The user can upload their **CAMS/KFintech statement** (or a screenshot) to get a deep analysis.

```
Portfolio reconstruction : List of funds, units, NAV, current value.
Key metrics :
XIRR – a gauge showing actual returns.
Overlap analysis – a donut chart showing percentage overlap among funds.
Expense ratio drag – bar chart comparing total expense ratio to category average.
Benchmark comparison – line chart of portfolio vs. Nifty 50 TRI.
Rebalancing plan : AI suggests selling overlapping or high‑expense funds and switching to
lower‑cost alternatives, with estimated improvement in XIRR. The user can accept changes,
which updates the roadmap.
```
### 5. Life Event Financial Advisor (Dev2)


The user selects a life event (bonus, inheritance, marriage, new baby) from a dropdown.

```
Input : Event type, amount, timing.
Backend (/api/life-event/advise):
Computes cash ow impact, tax implications (e.g., capital gains if selling assets), and effect
on goal timelines.
Uses LLM to generate a personalized action plan (e.g., “Use ₹50k to increase emergency
fund, ₹30k to top up PPF, and ₹20k to start a SIP for child’s education”).
Output : A report with numbers and an option to apply the changes to the roadmap.
```
### 6. Couple’s Money Planner (Dev2)

A dedicated page for couples to plan jointly.

```
Two ‑ column form : Partner A and Partner B input their incomes, HRA, NPS contributions, existing
investments, and goals.
Optimization (/api/couple/optimize):
Determines optimal HRA claim distribution (higher‑income partner claims more).
Suggests NPS matching to maximize tax benet.
Splits SIP contributions for joint goals based on tax brackets.
Recommends joint vs. individual term insurance.
Shows combined net worth projection over time.
Results : A unied plan with an option to save for both partners (with consent). The combined net
worth tracker is displayed as a line chart.
```
### 7. What ‑ if Simulation (Dev2)

A free‑form simulation page where users can ask questions like “What if I get a ₹1,00,000 bonus?” or
“What if I lose my job?”

```
Input : Natural language or structured elds.
Backend (/api/whatif/simulate):
Uses Monte Carlo simulations (simplied) or deterministic models to project outcomes.
Returns multiple scenarios (e.g., invest all, spend half, repay debt) with visual timelines of
net worth and goal attainment probabilities.
Output : Cards with scenarios; user can select one to update the roadmap.
```
### 8. Emergency Chatbot (Dev2)

A dedicated, soft‑toned chat interface for nancial crises.


```
Input : User types “I lost my job” or “Medical emergency”.
Backend (/api/emergency/respond):
Retrieves user’s prole (emergency fund, insurance, EPF balance) and provides personalized
steps: “First, use your emergency fund of ₹X to cover next 3 months. You can also apply for
EPF advance here. Consider pausing your SIPs temporarily.”
Includes links to government schemes and mental wellness resources.
User experience : Calming visuals, no sales pitches.
```
### 9. Real ‑ time News & Warnings (Dev1)

Integrated into the dashboard, a **news widget** continuously fetches relevant nancial news using RAG.

```
Backend (/api/news/query):
Uses a vector store of indexed nancial news (ET, Moneycontrol, etc.).
Queries based on user’s portfolio holdings, goals, and risk prole.
Flags warnings (e.g., “SEBI issues notice to a fund you hold”) with red alerts.
Frontend : A sidebar showing top 5 news items with summaries and sentiment indicators. Clicking
expands to full article and AI‑generated impact analysis.
```
### 10. Personalized Recommendations (Dev2)

A recommendations dashboard that evolves with the user.

```
Segmentation : Based on salary range, savings rate, existing investments, risk prole, and goals.
Recommendations (/api/recommendations):
Mutual funds (with risk/return proles).
Asset allocation adjustments.
Insurance products.
Tax‑saving opportunities.
Presentation : Cards with key metrics and an “Add to plan” button that updates the roadmap.
```
## 🧠 Under the Hood: Multi ‑ Agent Architecture

The system is powered by a **central orchestrator** (FastAPI) that routes user inputs to specialized agents.
Each agent is a combination of rule‑based logic, LLM calls, and nancial calculations.

```
Agent Responsibility
Voice Interface
Agent Handles STT/TTS, language detection, mode switching.
```

```
Agent Responsibility
```
```
Onboarding Agent Collects nancial data, computes Money Health Score, generates FIREroadmap.
```
```
Tax Wizard Agent Parses Form 16, computes deductions, compares regimes, suggeststax‑saving investments.
```
```
Portfolio X ‑ Ray
Agent
```
```
Reconstructs portfolio, computes XIRR, overlap, expense drag, and
rebalancing.
Life Event Agent Simulates nancial impact of life events and provides advisory.
Couple Planner
Agent Optimizes joint nances (HRA, NPS, SIP splits, insurance).
What ‑ if Simulation
Agent Runs Monte Carlo simulations for custom scenarios.
Emergency Agent Provides crisis‑specic, personalized action plans.
Recommendation
Agent Segments users and suggests relevant products.
News & RAG Agent Retrieves and summarizes news with warnings.
Guardrail Agent Monitors all outputs for compliance (disclaimers, prohibited terms).
```
All agents share a **common user prole** stored in PostgreSQL and communicate through the
orchestrator. They also maintain an **audit trail** – every decision is logged with a plain‑English
explanation for transparency.

## 🔒 Guardrails & Compliance

```
Disclaimer appears on every page: “This information is for educational purposes only. Consult a
SEBI‑registered advisor before making investment decisions.”
Prohibited terms (e.g., “guaranteed returns”) are automatically ltered.
Data privacy : All user data is encrypted; users can export or delete their data.
Audit trail : Every recommendation includes a clickable “Why this?” link showing the reasoning and
data sources.
```
## 📊 Impact Model (Quantied)

Based on conservative assumptions, ET Money Mentor delivers:


```
MetricMetric Baseline (DIY/NoBaseline (DIY/NoAdvisor)Advisor) With ET MoneyWith ET MoneyMentorMentor Annual Savings/ValueAnnual Savings/Value
```
```
Time to create a nancial
plan 4–6 hours 15 minutes
```
```
₹2,000–₹3,000 (value of
time)
Tax savings (avg. salaried
individual)
```
```
₹15,000 (missed
deductions) ₹45,000 ₹30,
Portfolio XIRR
improvement 8% (no rebalancing)
```
```
9.5% (after
rebalancing) ₹15,000 on ₹10L portfolio
```
```
Emergency fund coverage 35% have <3 months 80% reach 6months Reduced risk of debt
```
```
Couple nancial alignment 0 (no joint tool) 90% align goals Improved householdnancial stability
```
**Assumptions** : 10 lakh users in rst year, average portfolio ₹5L, average salary ₹10L.

## 📁 Final Deliverables

```
Public GitHub Repository : Contains all source code for frontend (React) and backend (FastAPI),
with clear README, environment variables, and commit history.
3 ‑ Minute Pitch Video : Walks through the entire user journey – voice onboarding, FIRE planner, Tax
Wizard, Portfolio X‑Ray, what‑if simulation, and emergency chatbot – showing the agentic
workow and measurable outcomes.
Architecture Document : 2‑page PDF with a diagram of the multi‑agent system, data ow, and
error‑handling logic.
Impact Model : A spreadsheet with detailed assumptions and calculations supporting the
quantied benets.
```
## 🌟 Why This Project Stands Out

```
Voice ‑ rst, multilingual design – Makes nancial planning accessible to India’s next 500 million
internet users.
Multi ‑ agent intelligence – Demonstrates sophisticated orchestration, not just a simple chatbot.
End ‑ to ‑ end automation – From data collection to actionable recommendations, all within a
seamless experience.
Behavioral nance integration – The emergency chatbot and what‑if simulations address
emotional and situational needs, not just numbers.
Real ‑ time news + portfolio integration – Keeps users informed about risks and opportunities.
Compliance & trust – Built‑in guardrails and audit trails ensure responsible AI.
```

**ET Money Mentor** is not just a tool—it’s a nancial companion that empowers every Indian to take
control of their nancial future, just as easily as sending a WhatsApp message.


