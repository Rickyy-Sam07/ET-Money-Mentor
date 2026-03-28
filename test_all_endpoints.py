"""Comprehensive endpoint test for ET Money Mentor — all Dev1 + Dev2 routes."""
import json
import requests

BASE = "http://127.0.0.1:8013/api"
passed = 0
failed = 0
errors = []

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        errors.append((name, str(e)))
        failed += 1

# 1. Health
def t_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

# 2. Session start
session_id = None
def t_session():
    global session_id
    r = requests.post(f"{BASE}/session/start")
    assert r.status_code == 200
    session_id = r.json()["session_id"]
    assert session_id

# 3. Get user
def t_get_user():
    r = requests.get(f"{BASE}/user", params={"session_id": session_id})
    assert r.status_code == 200
    assert "profile" in r.json()

# 4. Update user
def t_update_user():
    r = requests.post(f"{BASE}/user/update", json={
        "session_id": session_id, "age": 28, "income": 1200000,
        "expenses": 40000, "investments": [{"type": "SIP", "amount": 5000}],
        "goals": [{"type": "retirement", "target": 10000000, "years": 30}],
        "risk_profile": "moderate"
    })
    assert r.status_code == 200

# 5. Voice process (text mode)
def t_voice():
    r = requests.post(f"{BASE}/voice/process", json={
        "session_id": session_id, "text": "I earn 12 lakhs per year",
        "mode": "agent", "language": "en"
    })
    assert r.status_code == 200
    d = r.json()
    assert "response" in d
    print(f"       Voice response: {d['response'][:60]}...")

# 6. Voice resolve command
def t_voice_resolve():
    r = requests.post(f"{BASE}/voice/resolve-command", json={
        "session_id": session_id, "transcript": "show me tax wizard",
        "commands": [
            {"id": "run_tax", "description": "Open Tax Wizard", "examples": ["tax", "80c"]},
            {"id": "run_portfolio", "description": "Portfolio X-Ray", "examples": ["portfolio"]},
        ]
    })
    assert r.status_code == 200
    assert "command_id" in r.json()

# 7. Tax analyze
def t_tax():
    r = requests.post(f"{BASE}/tax/analyze", json={
        "session_id": session_id,
        "form16_data": {"gross_salary": 1200000, "deductions_80c": 50000, "deductions_80d": 5000, "hra_exemption": 0},
        "regime_preference": "new"
    })
    assert r.status_code == 200
    d = r.json()
    assert "deductions" in d and "regime_comparison" in d
    print(f"       Old tax: {d['regime_comparison']['old']}, New tax: {d['regime_comparison']['new']}")

# 8. Portfolio analyze
def t_portfolio():
    r = requests.post(f"{BASE}/portfolio/analyze", json={
        "session_id": session_id,
        "holdings": [
            {"name": "Axis Bluechip", "units": 100, "nav": 45.5, "expense_ratio": 0.8, "invested_amount": 4000, "buy_date": "2024-01-15"},
            {"name": "HDFC Index Nifty 50", "units": 200, "nav": 180, "expense_ratio": 0.2, "invested_amount": 30000, "buy_date": "2023-06-01"},
        ]
    })
    assert r.status_code == 200
    d = r.json()
    assert "metrics" in d
    print(f"       XIRR: {d['metrics']['xirr']}%, Total: {d['metrics']['total_value']}")

# 9. News query
def t_news():
    r = requests.get(f"{BASE}/news/query", params={"session_id": session_id})
    assert r.status_code == 200
    assert "items" in r.json()

# 10. Onboarding
def t_onboarding():
    r = requests.post(f"{BASE}/onboarding/submit", json={
        "session_id": session_id, "age": 28, "income": 1200000, "expenses": 40000,
        "investments": [{"type": "SIP", "amount": 5000}],
        "goals": [{"type": "retirement", "target": 10000000, "years": 30}],
        "risk_profile": "moderate", "emergency_fund": 100000,
        "health_insurance": 500000, "life_insurance": 5000000, "debt_emi": 0
    })
    assert r.status_code == 200
    d = r.json()
    print(f"       Onboarding keys: {list(d.keys())}")

# 11. Life Event
def t_life_event():
    r = requests.post(f"{BASE}/life-event/advise", json={
        "session_id": session_id, "event_type": "bonus", "amount": 200000, "timing": "now"
    })
    assert r.status_code == 200
    d = r.json()
    print(f"       Life event keys: {list(d.keys())}")

# 12. Couple optimize
def t_couple():
    partner = {"income": 1000000, "hra": 200000, "nps": 50000, "investments": [], "goals": []}
    r = requests.post(f"{BASE}/couple/optimize", json={
        "session_id": session_id,
        "partner1": partner,
        "partner2": {**partner, "income": 800000}
    })
    assert r.status_code == 200
    d = r.json()
    print(f"       Couple keys: {list(d.keys())}")

# 13. What-if simulate
def t_whatif():
    r = requests.post(f"{BASE}/whatif/simulate", json={
        "session_id": session_id, "scenario": "I get a 1 lakh bonus", "amount": 100000
    })
    assert r.status_code == 200
    d = r.json()
    print(f"       What-if keys: {list(d.keys())}")

# 14. Emergency respond
def t_emergency():
    r = requests.post(f"{BASE}/emergency/respond", json={
        "session_id": session_id, "crisis_type": "job_loss", "details": "Lost job, have EMIs"
    })
    assert r.status_code == 200
    d = r.json()
    print(f"       Emergency keys: {list(d.keys())}")

# 15. Recommendations
def t_recommendations():
    r = requests.get(f"{BASE}/recommendations", params={"session_id": session_id})
    assert r.status_code == 200
    d = r.json()
    print(f"       Recommendations keys: {list(d.keys())}")

print("\n=== ET Money Mentor Full API Test ===\n")

test("Health Check", t_health)
test("Session Start", t_session)
test("Get User Profile", t_get_user)
test("Update User Profile", t_update_user)
test("Voice Process (text)", t_voice)
test("Voice Resolve Command", t_voice_resolve)
test("Tax Analyze", t_tax)
test("Portfolio Analyze", t_portfolio)
test("News Query", t_news)
test("Onboarding Submit", t_onboarding)
test("Life Event Advise", t_life_event)
test("Couple Optimize", t_couple)
test("What-If Simulate", t_whatif)
test("Emergency Respond", t_emergency)
test("Recommendations", t_recommendations)

print(f"\n=== Results: {passed} passed, {failed} failed ===")
if errors:
    print("\nFailed tests:")
    for name, err in errors:
        print(f"  - {name}: {err}")
