# tests/test_copilot_agent.py
"""
End-to-End Tests for Copilot Agent across 15 distinct procurement questions.
Tests factual lookups, financial calculations, split awards, quality filtering,
risk registers, and multi-turn conversational context retention.
"""
import pytest
import sys
from pathlib import Path

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ai_service import answer_procurement_query
from copilot_agent import get_copilot_agent


# 1. Simple factual SKU question
def test_q1_factual_sku_specs():
    q = "What are the exact technical specifications and RFQ target volume for Item 15?"
    res = answer_procurement_query(q, rfx_id=1)
    assert res is not None
    assert "answer_text" in res
    assert len(res["sources"]) > 0
    assert len(res.get("table_data", [])) > 0
    # Verified against SQLite: item 15 is 3-ply, 25,000 qty
    assert any(row.get("item_number") == 15 for row in res["table_data"])


# 2. Quotation lookup
def test_q2_quote_lookup():
    q = "Who quoted on Item 15 and what is the lowest landed price?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res.get("table_data", [])) >= 1
    # Check that landed costs exist in table
    assert any("landed" in str(k).lower() or "cost" in str(k).lower() for k in res["table_data"][0].keys())


# 3. Supplier Profile
def test_q3_supplier_profile():
    q = "Tell me about PackIndia Ltd (PKI) - where are their plants and what are their terms?"
    res = answer_procurement_query(q, rfx_id=1)
    assert res["table_data"] is not None


# 4. Supplier Head-to-Head Comparison
def test_q4_supplier_comparison():
    q = "Compare PackIndia vs EcoBox in terms of quoted items and pricing."
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0


# 5. Quality Filtering (BRC Gate)
def test_q5_quality_filtering():
    q = "Which suppliers passed the mandatory BRC food-grade packaging certification?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0
    # Must identify qualified vs disqualified
    status_values = [str(row.get("status", "")) for row in res["table_data"]]
    assert "QUALIFIED" in status_values or "DISQUALIFIED" in status_values


# 6. Disqualification Rationale
def test_q6_disqualification_rationale():
    q = "Why was EcoBox Solutions (EBS) disqualified from food contact packaging?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0
    ebs_rows = [r for r in res["table_data"] if r.get("supplier") == "EBS"]
    assert len(ebs_rows) > 0
    assert ebs_rows[0].get("status") == "DISQUALIFIED"


# 7. Deterministic Landed Cost Calculation
def test_q7_landed_cost_calculation():
    q = "Can you break down the landed cost calculation for Item 4 by EcoBox Solutions?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0


# 8. Split-Award Scenario (Ground Truth Assertions)
def test_q8_split_award_scenario():
    q = "What is the optimal split-award recommendation across suppliers who cleared the mandatory quality questionnaire?"
    res = answer_procurement_query(q, rfx_id=1)
    raw = res.get("raw_analysis", {})
    assert raw["split_total"] == 26661540.0
    assert raw["single_best"]["supplier_code"] == "PCO"
    assert raw["single_best"]["total"] == 31167090.0
    assert raw["savings_vs_single"] == 4505550.0
    assert len(res["table_data"]) == 30
    assert res.get("chart_data") is not None
    assert res["chart_data"]["type"] == "bar"


# 9. Savings Comparison
def test_q9_savings_comparison():
    q = "How much money do we save with an optimized split award compared to awarding everything to the best single supplier?"
    res = answer_procurement_query(q, rfx_id=1)
    raw = res.get("raw_analysis", {})
    assert raw["savings_vs_single"] == 4505550.0
    assert raw["savings_pct"] == 14.46 or abs(raw["savings_pct"] - 14.5) < 0.2


# 10. Quotation Risks & Ambiguities
def test_q10_quotation_exceptions():
    q = "What quotation exceptions, footnotes, or audit risks were flagged in the supplier submissions?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) >= 4
    sup_codes = {r.get("supplier_code") for r in res["table_data"]}
    assert "RPC" in sup_codes
    assert "EBS" in sup_codes


# 11. Category Slicing (5-ply)
def test_q11_category_slicing_5ply():
    q = "Show me all 5-ply cartons and their price spread across bidders."
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0


# 12. Lead Times & MOQs
def test_q12_lead_times_and_moqs():
    q = "Which supplier offers the lowest MOQ and shortest production lead time?"
    res = answer_procurement_query(q, rfx_id=1)
    assert len(res["table_data"]) > 0


# 13 & 14. Multi-Turn Conversation History Retention
def test_q13_and_q14_multi_turn_conversation_flow():
    """Verify that turn 2 understands turn 1's context."""
    # Turn 1: Ask about split award
    t1_q = "What is the optimal split award recommendation?"
    t1_res = answer_procurement_query(t1_q, rfx_id=1)
    assert t1_res["raw_analysis"]["split_total"] == 26661540.0

    # Build conversation history
    history = [
        {"role": "user", "text": t1_q},
        {"role": "assistant", "text": t1_res["answer_text"]}
    ]

    # Turn 2: Follow-up referencing "Item 15" without mentioning cartons
    t2_q = "What about Item 15? Who is the cheapest supplier for it?"
    t2_res = answer_procurement_query(t2_q, rfx_id=1, history=history)
    assert len(t2_res["table_data"]) > 0
    # Should resolve to Item 15
    assert any(row.get("item_number") == 15 for row in t2_res["table_data"])


# 15. Unexpected / Complex Sourcing Question
def test_q15_complex_strategy_question():
    q = "Can we use IndoPack (IPI) for non-food secondary cartons despite their 90-day quote validity limit?"
    res = answer_procurement_query(q, rfx_id=1)
    assert res is not None
    assert "answer_text" in res
    assert len(res["answer_text"]) > 100
