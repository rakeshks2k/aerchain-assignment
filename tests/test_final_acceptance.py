import pytest
import json
import asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
import sys

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from main import app
from database import get_line_items, get_all_suppliers, get_extracted_quotes, get_questionnaire_responses
from ai_service import answer_procurement_query


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_dataset_realism_and_scale():
    """Verify exactly 30 line items, 5 suppliers, and authentic data scale."""
    items = await get_line_items(1)
    assert len(items) == 30, f"Expected 30 items, got {len(items)}"

    suppliers = await get_all_suppliers()
    assert len(suppliers) == 5, f"Expected 5 suppliers, got {len(suppliers)}"
    codes = {s["code"] for s in suppliers}
    assert codes == {"PKI", "EBS", "IPI", "PCO", "RPC"}

    quotes = await get_extracted_quotes(1)
    assert len(quotes) == 147, f"Expected 147 quotes, got {len(quotes)}"

    q_resp = await get_questionnaire_responses(1)
    assert len(q_resp) == 50, f"Expected 50 questionnaire responses, got {len(q_resp)}"


@pytest.mark.anyio
async def test_ground_truth_adherence():
    """Verify extracted quotes against the ground truth dataset."""
    ground_truth_path = Path(__file__).parent.parent / "supplier_docs" / "ground_truth.json"
    with open(ground_truth_path, encoding="utf-8") as f:
        gt = json.load(f)

    suppliers = await get_all_suppliers()
    s_map = {s["code"]: s["id"] for s in suppliers}

    # 1. Check PKI quotes (28 quoted, items 27 & 30 not produced)
    pki_quotes = await get_extracted_quotes(1, s_map["PKI"])
    assert len(pki_quotes) == 28
    pki_items_quoted = {q["line_item_id"] for q in pki_quotes}
    assert len(pki_items_quoted) == 28

    # 2. Check EBS trade discount (8% discount applied)
    ebs_quotes = await get_extracted_quotes(1, s_map["EBS"])
    assert len(ebs_quotes) == 30
    for q in ebs_quotes:
        assert q["discount_pct"] == 8.0

    # 3. Check IPI substitute on item 29
    ipi_quotes = await get_extracted_quotes(1, s_map["IPI"])
    assert len(ipi_quotes) == 29
    sub_quotes = [q for q in ipi_quotes if q["tech_compliance"] == "SUBSTITUTE"]
    assert len(sub_quotes) == 1
    assert "substitute" in sub_quotes[0]["notes"].lower()

    # 4. Check RPC unresolved items (13 items with confidence 0.10)
    rpc_quotes = await get_extracted_quotes(1, s_map["RPC"])
    unresolved = [q for q in rpc_quotes if q.get("confidence", 1.0) <= 0.15]
    assert len(unresolved) == 13

    # 5. Check mandatory qualification gates
    q_resp = await get_questionnaire_responses(1)
    ebs_q2 = [r for r in q_resp if r["supplier_id"] == s_map["EBS"] and r["question_code"] == "Q2"][0]
    rpc_q2 = [r for r in q_resp if r["supplier_id"] == s_map["RPC"] and r["question_code"] == "Q2"][0]
    pki_q2 = [r for r in q_resp if r["supplier_id"] == s_map["PKI"] and r["question_code"] == "Q2"][0]

    assert ebs_q2["is_compliant"] == 0, "EBS should fail BRC mandatory gate"
    assert rpc_q2["is_compliant"] == 0, "RPC should fail BRC mandatory gate"
    assert pki_q2["is_compliant"] == 1, "PKI should pass BRC mandatory gate"


@pytest.mark.anyio
async def test_analyst_split_award_mandatory_quality_query():
    """
    Specifically test Requirement F prompt:
    'What if we split the award, choosing the cheapest supplier per line, but only among suppliers who cleared the mandatory quality questionnaire?'
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        question = "What if we split the award, choosing the cheapest supplier per line, but only among suppliers who cleared the mandatory quality questionnaire?"
        resp = await client.post("/api/analyst/query", json={"rfx_id": 1, "question": question})
        assert resp.status_code == 200
        data = resp.json()

        raw = data.get("raw_analysis", {})
        assert "split_total" in raw
        assert "single_best" in raw
        assert "savings_vs_single" in raw
        assert "supplier_allocation" in raw

        # Split total should be 26,661,540
        assert raw["split_total"] == 26661540.0
        # Single best qualified supplier is PCO at 31,167,090
        assert raw["single_best"]["supplier_code"] == "PCO"
        assert raw["single_best"]["total"] == 31167090.0
        # Savings must be exactly 4,505,550
        assert raw["savings_vs_single"] == 4505550.0

        # Disqualified suppliers (EBS, RPC) must NOT receive any line items
        alloc = raw["supplier_allocation"]
        assert "EBS" not in alloc or alloc["EBS"] == 0
        assert "RPC" not in alloc or alloc["RPC"] == 0
        assert set(alloc.keys()) == {"IPI", "PKI", "PCO"}

        # Response must include chart data and table data
        assert data.get("chart_data") is not None
        assert data["chart_data"]["type"] == "bar"
        assert len(data.get("table_data", [])) == 30


@pytest.mark.anyio
async def test_comparison_endpoint_and_brc_filter():
    """Verify unified comparison endpoint and dynamic BRC qualification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/rfx/1/comparison")
        assert resp.status_code == 200
        data = resp.json()

        assert len(data["line_items"]) == 30
        assert len(data["suppliers"]) == 5

        # Only PKI, IPI, PCO should be qualified
        qualified = data["summary"]["qualified_suppliers"]
        assert set(qualified) == {"PKI", "IPI", "PCO"}

        # Export CSV endpoint works
        export_resp = await client.get("/api/rfx/1/export")
        assert export_resp.status_code == 200
        assert export_resp.headers["content-type"].startswith("text/csv")
        csv_text = export_resp.text
        assert "PKI_landed_cost" in csv_text
        assert "Lowest_Qualified_Price" in csv_text
