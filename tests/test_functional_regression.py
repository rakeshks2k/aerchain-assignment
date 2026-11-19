# tests/test_functional_regression.py
"""
Functional Regression Test Suite to ensure zero breakage of business functionality.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
for p in (str(ROOT_DIR), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"


def test_rfx_list():
    resp = client.get("/api/rfx/list")
    assert resp.status_code == 200
    data = resp.json()
    assert "rfx_events" in data
    assert len(data["rfx_events"]) > 0


def test_rfx_detail():
    resp = client.get("/api/rfx/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 1
    assert "line_items" in data
    assert len(data["line_items"]) == 30


def test_suppliers_list():
    resp = client.get("/api/suppliers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data.get("suppliers", [])) >= 5


def test_submissions_list():
    resp = client.get("/api/rfx/1/submissions")
    assert resp.status_code == 200
    data = resp.json()
    assert "submissions" in data
    assert len(data["submissions"]) >= 5


def test_comparison_matrix():
    resp = client.get("/api/rfx/1/comparison")
    assert resp.status_code == 200
    data = resp.json()
    assert "line_items" in data
    assert len(data["line_items"]) == 30
    assert "suppliers" in data
    assert "summary" in data


def test_award_scenarios():
    resp = client.get("/api/rfx/1/award-scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert "single_supplier" in data
    assert "split_award" in data
    assert data.get("savings_from_split", 0) > 0


def test_audit_log():
    resp = client.get("/api/rfx/1/audit-log")
    assert resp.status_code == 200
    data = resp.json()
    assert "audit_log" in data
    assert len(data["audit_log"]) > 0


def test_analyst_query():
    resp = client.post("/api/analyst/query", json={"question": "What is the optimal split award?", "rfx_id": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer_text" in data
    assert len(data["answer_text"]) > 20


def test_csv_export():
    resp = client.get("/api/rfx/1/export")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "text/csv; charset=utf-8"
    assert "Item#" in resp.text
