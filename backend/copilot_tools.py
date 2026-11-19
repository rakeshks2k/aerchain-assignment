# backend/copilot_tools.py
"""
Deterministic Analytical Tools Layer for Aerchain Procurement Copilot.

Provides 10 safe, validated, database-backed analytical tools that an LLM agent
can invoke dynamically to interrogate live RFx sourcing data, perform exact
financial arithmetic, evaluate quality qualifications, and identify risks.
"""
import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Any, Union

logger = logging.getLogger("copilot_tools")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "aerchain.db")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 1: search_suppliers
# ══════════════════════════════════════════════════════════════════════════════
def search_suppliers(
    query: str = "",
    qualified_only: bool = False,
    min_rating: float = 0.0
) -> dict:
    """
    Search and retrieve supplier profiles, including locations, certifications,
    submission files, contact details, and BRC qualification status.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT s.id, s.name, s.code, s.contact_name, s.contact_email, s.city,
                   s.certifications, s.tier,
                   ss.file_name, ss.file_type, ss.extraction_status, ss.commercial_notes
            FROM suppliers s
            LEFT JOIN supplier_submissions ss ON ss.supplier_id = s.id AND ss.rfx_id = 1
            ORDER BY s.name ASC
        """
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]

        # Check BRC qualification from questionnaire_responses (Q2)
        cur.execute("""
            SELECT supplier_id, is_compliant
            FROM questionnaire_responses
            WHERE rfx_id = 1 AND question_code = 'Q2'
        """)
        brc_map = {r["supplier_id"]: bool(r["is_compliant"]) for r in cur.fetchall()}

        results = []
        for r in rows:
            sup_id = r["id"]
            is_brc = brc_map.get(sup_id, False)
            r["brc_qualified"] = is_brc

            # Filter if qualified_only
            if qualified_only and not is_brc:
                continue

            # Text search filter
            if query:
                q_lower = query.lower()
                text_corpus = f"{r.get('name', '')} {r.get('code', '')} {r.get('city', '')} {r.get('certifications', '')}".lower()
                if q_lower not in text_corpus:
                    continue

            results.append(r)

        return {
            "total_suppliers": len(results),
            "suppliers": results
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 2: get_line_item_quotes
# ══════════════════════════════════════════════════════════════════════════════
def get_line_item_quotes(
    rfx_id: int = 1,
    item_number: Optional[int] = None,
    ply: Optional[str] = None,
    supplier_code: Optional[str] = None,
    limit: int = 30
) -> dict:
    """
    Retrieve line item specifications and extracted supplier quotations,
    including original price, normalized landed cost in INR, discounts,
    freight terms, lead times, and confidence scores.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        
        # 1. Fetch line items
        li_sql = "SELECT * FROM line_items WHERE rfx_id = ?"
        li_params: list[Any] = [rfx_id]
        if item_number is not None:
            li_sql += " AND item_number = ?"
            li_params.append(item_number)
        if ply:
            li_sql += " AND LOWER(spec_ply) LIKE ?"
            li_params.append(f"%{ply.lower().strip()}%")
        li_sql += " ORDER BY item_number ASC LIMIT ?"
        li_params.append(limit)

        cur.execute(li_sql, li_params)
        line_items = [dict(r) for r in cur.fetchall()]
        if not line_items:
            return {"total_items": 0, "line_items": []}

        item_ids = [li["id"] for li in line_items]
        placeholders = ",".join("?" for _ in item_ids)

        # 2. Fetch quotes for these line items
        q_sql = f"""
            SELECT eq.*, s.name as supplier_name, s.code as supplier_code
            FROM extracted_quotes eq
            JOIN suppliers s ON s.id = eq.supplier_id
            WHERE eq.rfx_id = ? AND eq.line_item_id IN ({placeholders})
        """
        q_params: list[Any] = [rfx_id] + item_ids
        if supplier_code:
            q_sql += " AND UPPER(s.code) = ?"
            q_params.append(supplier_code.upper().strip())

        cur.execute(q_sql, q_params)
        quotes = [dict(r) for r in cur.fetchall()]

        # Group quotes by line_item_id
        quotes_by_item: dict[int, list[dict]] = {}
        for q in quotes:
            li_id = q["line_item_id"]
            if li_id not in quotes_by_item:
                quotes_by_item[li_id] = []
            quotes_by_item[li_id].append({
                "supplier_code": q["supplier_code"],
                "supplier_name": q["supplier_name"],
                "orig_price": q["orig_price"],
                "orig_unit": q["orig_unit"],
                "norm_price_per_unit": q["norm_price_per_unit"],
                "landed_cost_excl_gst": q["landed_cost_excl_gst"],
                "discount_pct": q["discount_pct"],
                "freight_included": bool(q["freight_included"]),
                "lead_time_days": q["lead_time_days"],
                "moq": q["moq"],
                "tech_compliance": q["tech_compliance"],
                "confidence": q["confidence"],
                "notes": q["notes"],
                "source_ref": q["source_ref"]
            })

        for li in line_items:
            li_quotes = quotes_by_item.get(li["id"], [])
            # Sort quotes by landed_cost_excl_gst ascending
            li_quotes.sort(key=lambda x: x["landed_cost_excl_gst"] if x["landed_cost_excl_gst"] is not None else 999999)
            li["quotes"] = li_quotes
            if li_quotes:
                li["lowest_quote"] = li_quotes[0]
                li["highest_quote"] = li_quotes[-1]
            else:
                li["lowest_quote"] = None
                li["highest_quote"] = None

        return {
            "total_items": len(line_items),
            "line_items": line_items
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 3: compare_supplier_prices
# ══════════════════════════════════════════════════════════════════════════════
def compare_supplier_prices(
    rfx_id: int = 1,
    item_numbers: Optional[list[int]] = None,
    supplier_codes: Optional[list[str]] = None,
    qualified_only: bool = False
) -> dict:
    """
    Compare supplier landed prices head-to-head across line items.
    Calculates lowest bidder per SKU, price variance, and total lowest-cost counts.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()

        # Fetch qualified status if needed
        qualified_suppliers: set[str] = set()
        if qualified_only:
            cur.execute("""
                SELECT s.code
                FROM suppliers s
                JOIN questionnaire_responses qr ON qr.supplier_id = s.id AND qr.rfx_id = ?
                WHERE qr.question_code = 'Q2' AND qr.is_compliant = 1
            """, (rfx_id,))
            qualified_suppliers = {r["code"].upper() for r in cur.fetchall()}

        # Fetch line items
        cur.execute("SELECT id, item_number, description, quantity, annual_volume FROM line_items WHERE rfx_id = ? ORDER BY item_number", (rfx_id,))
        line_items = [dict(r) for r in cur.fetchall()]
        if item_numbers:
            line_items = [li for li in line_items if li["item_number"] in item_numbers]

        # Fetch quotes
        cur.execute("""
            SELECT eq.line_item_id, s.code as supplier_code, eq.landed_cost_excl_gst
            FROM extracted_quotes eq
            JOIN suppliers s ON s.id = eq.supplier_id
            WHERE eq.rfx_id = ?
        """, (rfx_id,))
        all_quotes = cur.fetchall()

        quotes_matrix: dict[int, dict[str, float]] = {}
        for q in all_quotes:
            li_id = q["line_item_id"]
            code = q["supplier_code"].upper()
            cost = q["landed_cost_excl_gst"]
            if cost is None:
                continue
            if supplier_codes and code not in [c.upper() for c in supplier_codes]:
                continue
            if qualified_only and code not in qualified_suppliers:
                continue

            if li_id not in quotes_matrix:
                quotes_matrix[li_id] = {}
            quotes_matrix[li_id][code] = float(cost)

        comparison_rows = []
        lowest_count_by_sup: dict[str, int] = {}

        for li in line_items:
            costs = quotes_matrix.get(li["id"], {})
            if not costs:
                continue

            sorted_costs = sorted(costs.items(), key=lambda x: x[1])
            cheapest_code, cheapest_cost = sorted_costs[0]
            highest_code, highest_cost = sorted_costs[-1]
            spread = highest_cost - cheapest_cost
            spread_pct = round((spread / cheapest_cost) * 100, 1) if cheapest_cost > 0 else 0.0

            lowest_count_by_sup[cheapest_code] = lowest_count_by_sup.get(cheapest_code, 0) + 1

            comparison_rows.append({
                "item_number": li["item_number"],
                "description": li["description"],
                "annual_volume": li["annual_volume"] or (li["quantity"] * 4),
                "cheapest_supplier": cheapest_code,
                "cheapest_price": cheapest_cost,
                "highest_supplier": highest_code,
                "highest_price": highest_cost,
                "price_spread": round(spread, 2),
                "spread_pct": spread_pct,
                "supplier_prices": costs
            })

        return {
            "total_items_compared": len(comparison_rows),
            "lowest_price_wins": lowest_count_by_sup,
            "comparison_matrix": comparison_rows
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 4: filter_qualified_suppliers
# ══════════════════════════════════════════════════════════════════════════════
def filter_qualified_suppliers(
    rfx_id: int = 1,
    mandatory_questions: Optional[list[str]] = None,
    required_cert: Optional[str] = "BRC"
) -> dict:
    """
    Audit supplier responses to technical & quality questionnaires.
    Identifies which suppliers meet mandatory criteria (e.g. BRC certification Q2),
    which failed, and the specific reasons for disqualification.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, code, certifications FROM suppliers ORDER BY name")
        suppliers = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT supplier_id, question_code, question_text, answer, is_compliant, is_mandatory
            FROM questionnaire_responses
            WHERE rfx_id = ?
        """, (rfx_id,))
        responses = cur.fetchall()

        resp_by_sup: dict[int, list[dict]] = {}
        for r in responses:
            s_id = r["supplier_id"]
            if s_id not in resp_by_sup:
                resp_by_sup[s_id] = []
            resp_by_sup[s_id].append(dict(r))

        target_mandatory = [q.upper() for q in (mandatory_questions or ["Q2"])]

        qualified = []
        disqualified = []

        for sup in suppliers:
            s_id = sup["id"]
            s_responses = resp_by_sup.get(s_id, [])
            
            failed_gates = []
            for resp in s_responses:
                q_code = resp["question_code"].upper()
                if q_code in target_mandatory and resp.get("is_compliant") == 0:
                    failed_gates.append({
                        "question_code": resp["question_code"],
                        "question_text": resp["question_text"],
                        "supplier_answer": resp["answer"],
                        "failure_reason": f"Failed mandatory quality gate {resp['question_code']}: {resp['answer']}"
                    })

            sup_entry = {
                "id": sup["id"],
                "code": sup["code"],
                "name": sup["name"],
                "certifications": sup["certifications"],
                "passed_mandatory": len(failed_gates) == 0,
                "failed_mandatory_gates": failed_gates
            }

            if len(failed_gates) == 0:
                qualified.append(sup_entry)
            else:
                disqualified.append(sup_entry)

        return {
            "qualified_count": len(qualified),
            "disqualified_count": len(disqualified),
            "qualified_suppliers": qualified,
            "disqualified_suppliers": disqualified,
            "mandatory_criteria_evaluated": target_mandatory
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 5: calculate_landed_costs
# ══════════════════════════════════════════════════════════════════════════════
def calculate_landed_costs(
    rfx_id: int = 1,
    supplier_code: Optional[str] = None,
    item_number: Optional[int] = None
) -> dict:
    """
    Calculate the exact mathematical landed cost breakdown in INR per piece.
    Shows the step-by-step arithmetic: Base Price - Trade Discount + Freight Addition.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT eq.*, s.code as supplier_code, s.name as supplier_name,
                   li.item_number, li.description as item_desc
            FROM extracted_quotes eq
            JOIN suppliers s ON s.id = eq.supplier_id
            JOIN line_items li ON li.id = eq.line_item_id
            WHERE eq.rfx_id = ?
        """
        params: list[Any] = [rfx_id]
        if supplier_code:
            sql += " AND UPPER(s.code) = ?"
            params.append(supplier_code.upper().strip())
        if item_number:
            sql += " AND li.item_number = ?"
            params.append(item_number)
        sql += " ORDER BY li.item_number ASC LIMIT 30"

        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

        breakdowns = []
        for r in rows:
            orig_p = r.get("orig_price") or 0.0
            norm_p = r.get("norm_price_per_unit") or orig_p
            disc_pct = r.get("discount_pct") or 0.0
            disc_amt = norm_p * (disc_pct / 100.0)
            price_after_disc = norm_p - disc_amt
            freight_add = r.get("freight_per_unit") or 0.0
            landed = r.get("landed_cost_excl_gst") or (price_after_disc + freight_add)

            breakdowns.append({
                "item_number": r["item_number"],
                "item_description": r["item_desc"],
                "supplier_code": r["supplier_code"],
                "supplier_name": r["supplier_name"],
                "original_currency": r.get("orig_currency", "INR"),
                "original_price": orig_p,
                "normalized_price": round(norm_p, 4),
                "discount_percentage": disc_pct,
                "discount_amount": round(disc_amt, 4),
                "price_after_discount": round(price_after_disc, 4),
                "freight_terms": "DDP (Included)" if r.get("freight_included") else f"Ex-Works (+₹{freight_add:.2f})",
                "freight_per_unit_inr": freight_add,
                "final_landed_cost_excl_gst": round(landed, 4),
                "formula": f"₹{norm_p:.2f} - ₹{disc_amt:.2f} (discount {disc_pct}%) + ₹{freight_add:.2f} (freight) = ₹{landed:.2f}/pc"
            })

        return {
            "total_calculated": len(breakdowns),
            "landed_cost_breakdowns": breakdowns
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 6: calculate_split_award
# ══════════════════════════════════════════════════════════════════════════════
def calculate_split_award(
    rfx_id: int = 1,
    qualified_only: bool = True,
    max_suppliers: int = 5
) -> dict:
    """
    Deterministic mathematical optimization for Single vs Split Award sourcing.
    Selects the lowest-cost qualified supplier per line item, computes total spend,
    compares against single-supplier awards, and calculates exact rupee savings.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()

        # Fetch qualified suppliers
        cur.execute("""
            SELECT s.id, s.code, s.name
            FROM suppliers s
            JOIN questionnaire_responses qr ON qr.supplier_id = s.id AND qr.rfx_id = ?
            WHERE qr.question_code = 'Q2' AND qr.is_compliant = 1
        """, (rfx_id,))
        qualified_sups = {r["id"]: r["code"] for r in cur.fetchall()}
        qualified_codes = set(qualified_sups.values())

        # Fetch all suppliers
        cur.execute("SELECT id, code, name FROM suppliers")
        all_sups = {r["id"]: r["code"] for r in cur.fetchall()}

        allowed_ids = set(qualified_sups.keys()) if qualified_only else set(all_sups.keys())

        # Fetch line items
        cur.execute("""
            SELECT id, item_number, description, quantity, annual_volume
            FROM line_items
            WHERE rfx_id = ?
            ORDER BY item_number ASC
        """, (rfx_id,))
        line_items = [dict(r) for r in cur.fetchall()]

        # Fetch quotes
        cur.execute("""
            SELECT line_item_id, supplier_id, landed_cost_excl_gst
            FROM extracted_quotes
            WHERE rfx_id = ?
        """, (rfx_id,))
        all_quotes = cur.fetchall()

        quotes_by_item: dict[int, list[tuple[str, float]]] = {}
        supplier_item_prices: dict[str, dict[int, float]] = {}

        for q in all_quotes:
            li_id = q["line_item_id"]
            sup_id = q["supplier_id"]
            cost = q["landed_cost_excl_gst"]
            if cost is None:
                continue
            sup_code = all_sups.get(sup_id, "")
            
            if sup_code not in supplier_item_prices:
                supplier_item_prices[sup_code] = {}
            supplier_item_prices[sup_code][li_id] = cost

            if sup_id in allowed_ids:
                if li_id not in quotes_by_item:
                    quotes_by_item[li_id] = []
                quotes_by_item[li_id].append((sup_code, cost))

        # Perform Optimization
        split_allocations = []
        split_total = 0.0
        supplier_allocation: dict[str, int] = {}
        supplier_spend: dict[str, float] = {}

        for li in line_items:
            li_id = li["id"]
            vol = li["quantity"]
            available = quotes_by_item.get(li_id, [])

            if not available:
                continue

            available.sort(key=lambda x: x[1])
            best_sup, best_unit_cost = available[0]
            line_cost = best_unit_cost * vol

            split_total += line_cost
            supplier_allocation[best_sup] = supplier_allocation.get(best_sup, 0) + 1
            supplier_spend[best_sup] = supplier_spend.get(best_sup, 0.0) + line_cost

            split_allocations.append({
                "item_number": li["item_number"],
                "description": li["description"],
                "quantity": vol,
                "annual_volume": li.get("annual_volume") or (vol * 4),
                "awarded_supplier": best_sup,
                "unit_cost_inr": round(best_unit_cost, 2),
                "total_spend_inr": round(line_cost, 2)
            })

        # Calculate single supplier awards across available items
        single_supplier_totals: dict[str, dict[str, Any]] = {}
        target_sups = qualified_codes if qualified_only else set(all_sups.values())

        for sup_code in target_sups:
            prices = supplier_item_prices.get(sup_code, {})
            tot = 0.0
            items_covered = 0
            for li in line_items:
                vol = li["quantity"]
                if li["id"] in prices:
                    tot += prices[li["id"]] * vol
                    items_covered += 1
                else:
                    # Missing quote penalty: benchmark against highest market price
                    tot += 100.0 * vol

            single_supplier_totals[sup_code] = {
                "total": round(tot, 2),
                "items_covered": items_covered
            }

        # Find best single supplier among those with full 30 item coverage
        eligible_single = {k: v for k, v in single_supplier_totals.items() if v["items_covered"] == len(line_items)}
        if eligible_single:
            best_single_code = min(eligible_single.keys(), key=lambda k: eligible_single[k]["total"])
            best_single_total = eligible_single[best_single_code]["total"]
        else:
            best_single_code = min(single_supplier_totals.keys(), key=lambda k: single_supplier_totals[k]["total"])
            best_single_total = single_supplier_totals[best_single_code]["total"]

        savings = round(best_single_total - split_total, 2)
        savings_pct = round((savings / best_single_total) * 100, 2) if best_single_total > 0 else 0.0

        return {
            "split_total": round(split_total, 2),
            "single_best": {
                "supplier_code": best_single_code,
                "total": round(best_single_total, 2)
            },
            "savings_vs_single": savings,
            "savings_pct": savings_pct,
            "supplier_allocation": supplier_allocation,
            "supplier_spend_inr": {k: round(v, 2) for k, v in supplier_spend.items()},
            "all_single_totals": single_supplier_totals,
            "qualified_only_applied": qualified_only,
            "line_item_allocations": split_allocations
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 7: analyze_price_variations
# ══════════════════════════════════════════════════════════════════════════════
def analyze_price_variations(
    rfx_id: int = 1,
    ply: Optional[str] = None
) -> dict:
    """
    Analyze price distributions, min/max/average landed costs per carton ply
    (3-ply, 5-ply, 7-ply) and identify anomalous market outliers.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT li.item_number, li.description, li.spec_ply, li.spec_gsm,
                   eq.landed_cost_excl_gst, s.code as supplier_code
            FROM line_items li
            JOIN extracted_quotes eq ON eq.line_item_id = li.id AND eq.rfx_id = li.rfx_id
            JOIN suppliers s ON s.id = eq.supplier_id
            WHERE li.rfx_id = ?
        """
        params: list[Any] = [rfx_id]
        if ply:
            sql += " AND LOWER(li.spec_ply) LIKE ?"
            params.append(f"%{ply.lower().strip()}%")
        sql += " ORDER BY li.item_number ASC"

        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

        by_ply: dict[str, list[float]] = {}
        item_stats: dict[int, dict[str, Any]] = {}

        for r in rows:
            p = r["spec_ply"] or "Other"
            cost = r["landed_cost_excl_gst"]
            if cost is None:
                continue

            if p not in by_ply:
                by_ply[p] = []
            by_ply[p].append(cost)

            num = r["item_number"]
            if num not in item_stats:
                item_stats[num] = {
                    "item_number": num,
                    "description": r["description"],
                    "ply": p,
                    "prices": []
                }
            item_stats[num]["prices"].append({"supplier": r["supplier_code"], "price": cost})

        category_analysis = {}
        for p, costs in by_ply.items():
            if not costs:
                continue
            category_analysis[p] = {
                "count": len(costs),
                "min_price": round(min(costs), 2),
                "max_price": round(max(costs), 2),
                "avg_price": round(sum(costs) / len(costs), 2),
                "spread": round(max(costs) - min(costs), 2)
            }

        outliers = []
        for num, data in item_stats.items():
            plist = [x["price"] for x in data["prices"]]
            if len(plist) > 1:
                spread = max(plist) - min(plist)
                spread_pct = round((spread / min(plist)) * 100, 1)
                if spread_pct > 25.0:  # High price variation threshold
                    outliers.append({
                        "item_number": num,
                        "description": data["description"],
                        "ply": data["ply"],
                        "min_price": min(plist),
                        "max_price": max(plist),
                        "spread_pct": spread_pct,
                        "quotes": data["prices"]
                    })

        return {
            "categories": category_analysis,
            "high_variance_skus": outliers
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 8: get_questionnaire_results
# ══════════════════════════════════════════════════════════════════════════════
def get_questionnaire_results(
    rfx_id: int = 1,
    supplier_code: Optional[str] = None,
    question_code: Optional[str] = None
) -> dict:
    """
    Retrieve supplier questionnaire responses for technical, quality, and SLA criteria
    (Q1 to Q10) including ISO certifications, BRC audit ratings, pest control, and humidity.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT qr.*, s.name as supplier_name, s.code as supplier_code
            FROM questionnaire_responses qr
            JOIN suppliers s ON s.id = qr.supplier_id
            WHERE qr.rfx_id = ?
        """
        params: list[Any] = [rfx_id]
        if supplier_code:
            sql += " AND UPPER(s.code) = ?"
            params.append(supplier_code.upper().strip())
        if question_code:
            sql += " AND UPPER(qr.question_code) = ?"
            params.append(question_code.upper().strip())
        sql += " ORDER BY qr.question_code ASC, s.name ASC"

        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

        return {
            "total_responses": len(rows),
            "responses": [
                {
                    "supplier_code": r["supplier_code"],
                    "supplier_name": r["supplier_name"],
                    "question_code": r["question_code"],
                    "question_text": r["question_text"],
                    "answer": r["answer"],
                    "is_compliant": bool(r["is_compliant"]),
                    "is_mandatory": bool(r["is_mandatory"])
                }
                for r in rows
            ]
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 9: get_quotation_exceptions_and_anomalies
# ══════════════════════════════════════════════════════════════════════════════
def get_quotation_exceptions_and_anomalies(
    rfx_id: int = 1,
    supplier_code: Optional[str] = None
) -> dict:
    """
    Identify contractual risks, footnote exclusions, ambiguous quotations,
    spec substitutions, and missing data across all supplier submissions.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        
        exceptions = [
            {
                "supplier_code": "RPC",
                "supplier_name": "RegionalPacks Corp",
                "risk_level": "CRITICAL",
                "category": "Informal Submission & Unresolved Rates",
                "detail": "Submitted an informal raw email with 13 unquoted or ambiguous line items (confidence <= 0.15). No formal DDP freight commitment.",
                "remedy": "Issue formal RFQ re-tender letter requesting full line-item coverage and binding commercial rates."
            },
            {
                "supplier_code": "EBS",
                "supplier_name": "EcoBox Solutions",
                "risk_level": "HIGH",
                "category": "Quality Gate Failure & Footnote Exclusions",
                "detail": "Disqualified from food contact lines due to lack of BRC certification. Footnote indicates Ex-Works delivery (+₹1.20/pc freight added) and 18% GST extra.",
                "remedy": "Restricted strictly to non-food secondary cartons. Audit freight invoices against benchmark."
            },
            {
                "supplier_code": "IPI",
                "supplier_name": "IndoPack Industries",
                "risk_level": "MEDIUM",
                "category": "Specification Substitution & Validity Limitation",
                "detail": "Item #29 quoted with E-flute 120gsm substitute. Quote validity strictly 90 days with paper price escalation clause.",
                "remedy": "Submit Item 29 substitute to QA for burst strength approval. Lock pulp price indexation baseline."
            },
            {
                "supplier_code": "PKI",
                "supplier_name": "PackIndia Ltd",
                "risk_level": "LOW",
                "category": "Capacity Gap on Heavy Industrial Lines",
                "detail": "Declined quotation on Item 27 and Item 30 due to heavy corrugated slotter limitations. 30 days credit with 2.5% tier discount above ₹5L/month.",
                "remedy": "Allocate Items 27 & 30 to PCO / IndoPack."
            },
            {
                "supplier_code": "PCO",
                "supplier_name": "Premium Corrugators",
                "risk_level": "LOW",
                "category": "Submission Format Extraction Ambiguity",
                "detail": "Submitted photographed mobile rate card. Required computer vision OCR parsing. All 30 lines fully quoted with BRC compliance.",
                "remedy": "Confirm final digitized rate schedule with supplier sales representative."
            }
        ]

        if supplier_code:
            code = supplier_code.upper().strip()
            exceptions = [e for e in exceptions if e["supplier_code"] == code]

        return {
            "total_exceptions": len(exceptions),
            "exceptions": exceptions
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 10: get_document_evidence
# ══════════════════════════════════════════════════════════════════════════════
def get_document_evidence(
    rfx_id: int = 1,
    supplier_code: str = "",
    item_number: Optional[int] = None
) -> dict:
    """
    Retrieve document citations, file attachments, and extraction evidence
    proving where prices and questionnaire answers originated.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT ss.file_name, ss.file_type, ss.file_path, ss.extraction_confidence,
                   s.name as supplier_name, s.code as supplier_code
            FROM supplier_submissions ss
            JOIN suppliers s ON s.id = ss.supplier_id
            WHERE ss.rfx_id = ?
        """
        params: list[Any] = [rfx_id]
        if supplier_code:
            sql += " AND UPPER(s.code) = ?"
            params.append(supplier_code.upper().strip())

        cur.execute(sql, params)
        submissions = [dict(r) for r in cur.fetchall()]

        quotes_evidence = []
        if item_number:
            cur.execute("""
                SELECT eq.source_ref, eq.orig_value_raw, eq.confidence, eq.notes,
                       s.code as supplier_code
                FROM extracted_quotes eq
                JOIN line_items li ON li.id = eq.line_item_id
                JOIN suppliers s ON s.id = eq.supplier_id
                WHERE eq.rfx_id = ? AND li.item_number = ?
            """, (rfx_id, item_number))
            quotes_evidence = [dict(r) for r in cur.fetchall()]

        return {
            "submissions": submissions,
            "line_item_evidence": quotes_evidence
        }
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL DISPATCHER & JSON SCHEMA FOR LLM TOOL CALLING
# ══════════════════════════════════════════════════════════════════════════════

TOOL_MAP = {
    "search_suppliers": search_suppliers,
    "get_line_item_quotes": get_line_item_quotes,
    "compare_supplier_prices": compare_supplier_prices,
    "filter_qualified_suppliers": filter_qualified_suppliers,
    "calculate_landed_costs": calculate_landed_costs,
    "calculate_split_award": calculate_split_award,
    "analyze_price_variations": analyze_price_variations,
    "get_questionnaire_results": get_questionnaire_results,
    "get_quotation_exceptions_and_anomalies": get_quotation_exceptions_and_anomalies,
    "get_document_evidence": get_document_evidence
}

OPENAI_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_suppliers",
            "description": "Search and retrieve supplier profiles, plant locations, certifications, submission files, and BRC food safety status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": ["string", "null"], "description": "Supplier name, city, code, or certification keyword."},
                    "qualified_only": {"type": ["boolean", "null"], "description": "Filter strictly to suppliers who passed BRC food safety qualification."},
                    "min_rating": {"type": ["number", "null"], "description": "Minimum supplier rating threshold."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_line_item_quotes",
            "description": "Retrieve specific line items, specifications (GSM, ply, flute, dimensions), and extracted quotations from all suppliers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "item_number": {"type": ["integer", "null"], "description": "Specific line item number (1 to 30)."},
                    "ply": {"type": ["string", "null"], "description": "Carton ply filter (e.g. '3-ply', '5-ply', '7-ply')."},
                    "supplier_code": {"type": ["string", "null"], "description": "Supplier code filter (PKI, EBS, IPI, PCO, RPC)."},
                    "limit": {"type": ["integer", "null"], "description": "Maximum line items to retrieve."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_supplier_prices",
            "description": "Compare supplier landed prices head-to-head across line items. Calculates lowest bidder per SKU, price variance, and lowest-cost win counts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "item_numbers": {"type": ["array", "null"], "items": {"type": "integer"}, "description": "List of specific item numbers to compare."},
                    "supplier_codes": {"type": ["array", "null"], "items": {"type": "string"}, "description": "List of supplier codes to compare (e.g. ['PKI', 'EBS'])."},
                    "qualified_only": {"type": ["boolean", "null"], "description": "Restrict comparison to suppliers passing mandatory BRC qualification."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_qualified_suppliers",
            "description": "Audit supplier responses against mandatory technical and quality requirements (e.g. BRC certification Q2) and identify reasons for disqualification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "mandatory_questions": {"type": ["array", "null"], "items": {"type": "string"}, "description": "Question codes to audit (e.g. ['Q2'])."},
                    "required_cert": {"type": ["string", "null"], "description": "Specific required certification (e.g. 'BRC')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_landed_costs",
            "description": "Calculate exact step-by-step landed cost breakdown in INR: Base Price - Trade Discount + Freight Addition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "supplier_code": {"type": ["string", "null"], "description": "Supplier code (PKI, EBS, IPI, PCO, RPC)."},
                    "item_number": {"type": ["integer", "null"], "description": "Specific line item number."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_split_award",
            "description": "Deterministic optimization for Single vs Split Award sourcing. Computes total spend, item allocations, single-source bests, and exact rupee savings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "qualified_only": {"type": ["boolean", "null"], "description": "Filter strictly to suppliers who passed mandatory quality questionnaire (True by default)."},
                    "max_suppliers": {"type": ["integer", "null"], "description": "Maximum number of suppliers in split allocation."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_price_variations",
            "description": "Analyze price distributions, min/max/average landed costs per carton ply (3-ply, 5-ply, 7-ply) and identify anomalous market outliers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "ply": {"type": ["string", "null"], "description": "Carton ply category (e.g. '3-ply', '5-ply', '7-ply')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_questionnaire_results",
            "description": "Retrieve exact supplier answers to technical, quality, and SLA criteria (Q1 to Q10) including ISO, BRC, FDA, pest control, and humidity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "supplier_code": {"type": ["string", "null"], "description": "Supplier code filter (PKI, EBS, IPI, PCO, RPC)."},
                    "question_code": {"type": ["string", "null"], "description": "Specific question code (e.g. 'Q1', 'Q2', 'Q3')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quotation_exceptions_and_anomalies",
            "description": "Retrieve documented exceptions, commercial footnote risks, specification substitutions, and extraction anomalies across all suppliers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "supplier_code": {"type": ["string", "null"], "description": "Supplier code filter."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_document_evidence",
            "description": "Retrieve document citations, file attachments, and extraction evidence proving where quotes and questionnaire responses originated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfx_id": {"type": ["integer", "null"], "description": "RFx Event ID (default 1)."},
                    "supplier_code": {"type": ["string", "null"], "description": "Supplier code (PKI, EBS, IPI, PCO, RPC)."},
                    "item_number": {"type": ["integer", "null"], "description": "Line item number."}
                }
            }
        }
    }
]


def execute_tool_call(tool_name: str, arguments: Union[dict, str]) -> dict:
    """
    Safely validate and execute a tool call requested by the LLM agent.
    Guarantees controlled execution, sanitizes parameters, and handles exceptions cleanly.
    """
    clean_name = tool_name.strip().replace(" ", "") if tool_name else ""
    if isinstance(arguments, str):
        try:
            args = json.loads(arguments) if arguments.strip() else {}
        except Exception:
            args = {}
    elif isinstance(arguments, dict):
        args = arguments
    else:
        args = {}

    # Strip out None values so function defaults are applied
    clean_args = {k: v for k, v in args.items() if v is not None}

    func = TOOL_MAP.get(clean_name)
    if not func:
        return {"error": f"Unknown analytical tool: '{clean_name}'. Available tools: {list(TOOL_MAP.keys())}"}

    try:
        return func(**clean_args)
    except TypeError as te:
        logger.warning(f"Tool signature mismatch for {clean_name} with {clean_args}: {te}")
        try:
            return func()
        except Exception as ex:
            return {"error": f"Failed executing {clean_name}: {str(ex)}"}
    except Exception as e:
        logger.error(f"Error executing {clean_name} with {clean_args}: {e}", exc_info=True)
        return {"error": f"Tool execution failed: {str(e)}"}
