"""
Comprehensive Dev2 Test Suite
=============================
Tests:
  1. Supabase (PostgreSQL) connectivity
  2. Groq LLM connectivity
  3. All 6 Dev2 API endpoints via FastAPI TestClient
  4. Unit tests for each service module
"""

import json
import os
import sys
import traceback
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Results collector
results = []

def record(name, passed, detail=""):
    results.append({"name": name, "passed": passed, "detail": detail})
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status}  {name}")
    if detail:
        safe = detail.encode('ascii', 'replace').decode('ascii')
        print(f"          -> {safe[:200]}")


# ===================================================================
# 1. SUPABASE / DATABASE CONNECTIVITY
# ===================================================================
print("\n" + "=" * 60)
print("  TEST GROUP 1: Supabase / Database Connectivity")
print("=" * 60)

try:
    from sqlalchemy import text
    from app.db.database import engine, DATABASE_URL

    # Check env var loaded
    record(
        "ENV: DATABASE_URL is set",
        bool(DATABASE_URL) and "supabase" in DATABASE_URL.lower(),
        f"URL starts with: {DATABASE_URL[:40]}...",
    )

    # Actually connect
    with engine.connect() as conn:
        row = conn.execute(text("SELECT 1")).fetchone()
        record("DB: Can execute SELECT 1", row is not None and row[0] == 1)

    # Check tables exist
    from app.db.database import Base
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = [
        "users",
        "profiles",
        "financial_goals",
        "life_events",
        "couple_data",
        "emergency_interactions",
        "recommendations",
    ]
    for t in expected_tables:
        record(f"DB: Table '{t}' exists", t in tables)

except Exception as e:
    record("DB: Connection", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# ===================================================================
# 2. GROQ LLM CONNECTIVITY
# ===================================================================
print("\n" + "=" * 60)
print("  TEST GROUP 2: Groq LLM Connectivity")
print("=" * 60)

try:
    groq_key = os.getenv("GROQ_API_KEY", "")
    record("ENV: GROQ_API_KEY is set", bool(groq_key) and len(groq_key) > 10)

    from app.services.llm_client import _get_client, generate_explanation

    client_llm = _get_client()
    record("GROQ: Client initialised", client_llm is not None)

    # Quick LLM call
    test_response = generate_explanation(
        "Say 'hello' in one word.", fallback="FALLBACK_USED"
    )
    used_llm = test_response != "FALLBACK_USED" and "unavailable" not in test_response.lower()
    safe_resp = test_response.encode('ascii', 'replace').decode('ascii')[:100]
    record(
        "GROQ: LLM responds to prompt",
        used_llm,
        f"Response: {safe_resp}",
    )

except Exception as e:
    record("GROQ: Connection", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# ===================================================================
# 3. UNIT TESTS - SERVICE MODULES
# ===================================================================
print("\n" + "=" * 60)
print("  TEST GROUP 3: Service Unit Tests")
print("=" * 60)

# 3a. Onboarding Service
try:
    from app.services.onboarding_service import compute_health_score, compute_fire_roadmap

    hs = compute_health_score(
        age=30,
        income=1200000,
        expenses=40000,
        investments=[
            {"type": "ELSS", "amount": 50000},
            {"type": "PPF", "amount": 100000},
            {"type": "equity_mf", "amount": 200000},
        ],
        emergency_fund=200000,
        health_insurance=500000,
        life_insurance=5000000,
        debt_emi=10000,
    )
    record(
        "SVC: compute_health_score returns dict with 7 keys",
        isinstance(hs, dict) and len(hs) == 7 and "overall" in hs,
        f"overall={hs.get('overall')}",
    )
    record(
        "SVC: health_score dimensions 0-100",
        all(0 <= v <= 100 for v in hs.values()),
        str(hs),
    )

    rm = compute_fire_roadmap(
        age=30,
        income=1200000,
        expenses=40000,
        investments=[{"type": "ELSS", "amount": 50000}],
        goals=[{"type": "retirement", "target": 50000000}],
        risk_profile="moderate",
        emergency_fund=200000,
        health_insurance=500000,
        debt_emi=10000,
    )
    record(
        "SVC: compute_fire_roadmap returns 12 months",
        isinstance(rm, list) and len(rm) == 12,
        f"Month 1 SIP: {rm[0].get('sip_amount', 0)}" if rm else "",
    )
    record(
        "SVC: roadmap entries have required keys",
        all({"month", "actions", "sip_amount", "allocation"}.issubset(set(m.keys())) for m in rm),
    )

except Exception as e:
    record("SVC: onboarding_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# 3b. Life Event Service
try:
    from app.services.life_event_service import advise_life_event

    for event in ["bonus", "inheritance", "marriage", "new_baby"]:
        res = advise_life_event(
            event, 500000, {"income": 1200000, "expenses": 40000}
        )
        record(
            f"SVC: advise_life_event('{event}') returns valid dict",
            isinstance(res, dict)
            and "allocations" in res
            and "priority_steps" in res
            and len(res["allocations"]) > 0,
            f"allocations count: {len(res.get('allocations', []))}",
        )

except Exception as e:
    record("SVC: life_event_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# 3c. Couple Service
try:
    from app.services.couple_service import optimize_couple

    p1 = {"income": 1500000, "expenses": 50000, "rent": 20000, "nps_contribution": 20000, "investments": []}
    p2 = {"income": 800000, "expenses": 30000, "rent": 0, "nps_contribution": 0, "investments": []}
    couple_res = optimize_couple(p1, p2)
    record(
        "SVC: optimize_couple returns required keys",
        all(
            k in couple_res
            for k in ["hra_optimization", "nps_matching", "sip_splits", "insurance", "net_worth_projection"]
        ),
    )
    record(
        "SVC: HRA tax_saved is numeric",
        isinstance(couple_res["hra_optimization"]["tax_saved"], (int, float)),
        f"tax_saved={couple_res['hra_optimization']['tax_saved']}",
    )
    record(
        "SVC: net_worth_projection has 10 years",
        len(couple_res["net_worth_projection"]) == 10,
    )

except Exception as e:
    record("SVC: couple_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# 3d. What-if Service
try:
    from app.services.whatif_service import simulate_whatif

    wif = simulate_whatif(
        "I get a 1 lakh bonus",
        100000,
        {"income": 1200000, "expenses": 40000, "investments": [{"amount": 500000}]},
    )
    record(
        "SVC: simulate_whatif returns scenarios",
        isinstance(wif, dict)
        and "scenarios" in wif
        and len(wif["scenarios"]) == 3,
        f"Scenarios: {[s['name'] for s in wif['scenarios']]}",
    )
    record(
        "SVC: whatif base_projection has year_5 and year_10",
        "year_5" in wif["base_projection"] and "year_10" in wif["base_projection"],
    )

except Exception as e:
    record("SVC: whatif_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# 3e. Emergency Service
try:
    from app.services.emergency_service import respond_emergency

    for crisis in ["job_loss", "medical", "debt_crisis", "market_crash"]:
        eres = respond_emergency(
            crisis, "Test details", {"income": 1200000, "expenses": 40000, "emergency_fund": 240000}
        )
        record(
            f"SVC: respond_emergency('{crisis}') returns valid",
            isinstance(eres, dict)
            and "action_steps" in eres
            and len(eres["action_steps"]) > 0
            and "empathy_message" in eres,
            f"steps: {len(eres['action_steps'])}, months: {eres.get('emergency_fund_months')}",
        )

except Exception as e:
    record("SVC: emergency_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# 3f. Recommendations Service
try:
    from app.services.recommendations_service import get_recommendations

    for risk in ["conservative", "moderate", "aggressive"]:
        recs = get_recommendations(
            {"income": 1200000, "expenses": 40000, "risk_profile": risk, "investments": []}
        )
        record(
            f"SVC: get_recommendations(risk='{risk}') returns valid",
            isinstance(recs, dict)
            and "recommended_funds" in recs
            and len(recs["recommended_funds"]) > 0
            and "asset_allocation" in recs
            and "segment" in recs,
            f"segment={recs.get('segment')}, funds={len(recs['recommended_funds'])}",
        )

except Exception as e:
    record("SVC: recommendations_service", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()

# ===================================================================
# 4. FULL API ENDPOINT TESTS (via FastAPI TestClient)
# ===================================================================
print("\n" + "=" * 60)
print("  TEST GROUP 4: API Endpoint Integration Tests")
print("=" * 60)

try:
    from fastapi.testclient import TestClient
    from app.main import app

    tc = TestClient(app)

    # 4.0 Health check
    r = tc.get("/api/health")
    record("API: GET /api/health -> 200", r.status_code == 200)

    # 4.1 Start session
    r = tc.post("/api/session/start")
    record("API: POST /api/session/start -> 200", r.status_code == 200)
    session_id = r.json().get("session_id", "")
    record("API: session_id is a UUID", len(session_id) == 36 and "-" in session_id)

    # 4.2 Onboarding submit
    onboarding_payload = {
        "session_id": session_id,
        "age": 28,
        "income": 1200000,
        "expenses": 35000,
        "investments": [
            {"type": "ELSS", "amount": 50000},
            {"type": "equity_mf", "amount": 200000},
        ],
        "goals": [{"type": "retirement", "target": 50000000, "years": 30}],
        "risk_profile": "moderate",
        "emergency_fund": 150000,
        "health_insurance": 500000,
        "life_insurance": 5000000,
        "debt_emi": 8000,
    }
    r = tc.post("/api/onboarding/submit", json=onboarding_payload)
    record(
        "API: POST /api/onboarding/submit -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: onboarding response has health_score & roadmap",
            "health_score" in body and "roadmap" in body,
        )
        record(
            "API: health_score has 'overall' key",
            "overall" in body.get("health_score", {}),
            f"overall={body.get('health_score', {}).get('overall')}",
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.3 Life event advise
    life_payload = {
        "session_id": session_id,
        "event_type": "bonus",
        "amount": 200000,
        "timing": "now",
    }
    r = tc.post("/api/life-event/advise", json=life_payload)
    record(
        "API: POST /api/life-event/advise -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: life-event response has allocations",
            "allocations" in body and len(body["allocations"]) > 0,
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.4 Couple optimize
    couple_payload = {
        "session_id": session_id,
        "partner1": {
            "income": 1500000, "expenses": 50000, "rent": 20000,
            "nps_contribution": 20000, "investments": [],
        },
        "partner2": {
            "income": 800000, "expenses": 30000, "rent": 0,
            "nps_contribution": 0, "investments": [],
        },
    }
    r = tc.post("/api/couple/optimize", json=couple_payload)
    record(
        "API: POST /api/couple/optimize -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: couple response has hra_optimization",
            "hra_optimization" in body,
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.5 What-if simulate
    whatif_payload = {
        "session_id": session_id,
        "scenario": "I get a 1 lakh bonus",
        "amount": 100000,
    }
    r = tc.post("/api/whatif/simulate", json=whatif_payload)
    record(
        "API: POST /api/whatif/simulate -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: whatif response has scenarios",
            "scenarios" in body and len(body["scenarios"]) == 3,
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.6 Emergency respond
    emerg_payload = {
        "session_id": session_id,
        "crisis_type": "job_loss",
        "details": "I just lost my job and have a home loan EMI",
    }
    r = tc.post("/api/emergency/respond", json=emerg_payload)
    record(
        "API: POST /api/emergency/respond -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: emergency response has action_steps",
            "action_steps" in body and len(body["action_steps"]) > 0,
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.7 Recommendations
    r = tc.get("/api/recommendations", params={"session_id": session_id})
    record(
        "API: GET /api/recommendations -> 200",
        r.status_code == 200,
        f"status={r.status_code}",
    )
    if r.status_code == 200:
        body = r.json()
        record(
            "API: recommendations response has recommended_funds",
            "recommended_funds" in body and len(body["recommended_funds"]) > 0,
        )
    else:
        print(f"    ERROR body: {r.text[:300]}")

    # 4.8 Guardrail check
    r_onb = tc.post("/api/onboarding/submit", json=onboarding_payload)
    if r_onb.status_code == 200:
        full_text = json.dumps(r_onb.json()).lower()
        record(
            "GUARDRAIL: No 'guaranteed return' in onboarding response",
            "guaranteed return" not in full_text,
        )

    # 4.9 Invalid session should 404
    r_bad = tc.post(
        "/api/life-event/advise",
        json={"session_id": "non-existent-session", "event_type": "bonus", "amount": 100},
    )
    record("API: Invalid session -> 404", r_bad.status_code == 404)

except Exception as e:
    record("API: TestClient setup", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()


# ===================================================================
# SUMMARY
# ===================================================================
print("\n" + "=" * 60)
print("  TEST SUMMARY")
print("=" * 60)

passed = sum(1 for r in results if r["passed"])
failed = sum(1 for r in results if not r["passed"])
total = len(results)

print(f"\n  Total : {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Rate  : {passed/total*100:.1f}%\n")

if failed > 0:
    print("  -- Failed Tests --")
    for r in results:
        if not r["passed"]:
            print(f"    [FAIL]  {r['name']}")
            if r["detail"]:
                safe = r["detail"].encode('ascii', 'replace').decode('ascii')
                print(f"        -> {safe[:300]}")
    print()

sys.exit(0 if failed == 0 else 1)
