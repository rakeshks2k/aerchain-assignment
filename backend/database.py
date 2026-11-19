# backend/database.py
import aiosqlite
import os
import shutil
from datetime import datetime

ORIGINAL_DB = os.path.join(os.path.dirname(__file__), "data", "aerchain.db")

# On Vercel serverless, /var/task is read-only; copy to /tmp for read & write operations
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/aerchain.db"
else:
    DB_PATH = ORIGINAL_DB


def ensure_db():
    if os.environ.get("VERCEL"):
        if not os.path.exists(DB_PATH) and os.path.exists(ORIGINAL_DB):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            shutil.copy2(ORIGINAL_DB, DB_PATH)


ensure_db()

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS rfx_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'Corrugated Packaging',
    description TEXT,
    status TEXT DEFAULT 'DRAFT',
    created_at TEXT DEFAULT (datetime('now')),
    deadline TEXT,
    buyer_name TEXT DEFAULT 'Priya Krishnamurthy',
    buyer_email TEXT DEFAULT 'priya.k@fmcgco.in'
);

CREATE TABLE IF NOT EXISTS line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    spec_ply TEXT,
    spec_flute TEXT,
    spec_gsm TEXT,
    spec_dimensions TEXT,
    spec_print TEXT,
    spec_ect_min TEXT,
    fefco_code TEXT,
    quantity INTEGER NOT NULL,
    unit TEXT DEFAULT 'pieces',
    annual_volume INTEGER,
    notes TEXT,
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id)
);

CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    contact_email TEXT,
    contact_name TEXT,
    city TEXT,
    certifications TEXT,
    tier TEXT DEFAULT 'Approved'
);

CREATE TABLE IF NOT EXISTS questionnaire_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER NOT NULL,
    question_code TEXT NOT NULL,
    question_text TEXT NOT NULL,
    is_mandatory INTEGER DEFAULT 0,
    answer_type TEXT DEFAULT 'TEXT',
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id)
);

CREATE TABLE IF NOT EXISTS rfx_invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    sent_at TEXT,
    response_deadline TEXT,
    status TEXT DEFAULT 'PENDING',
    email_body TEXT,
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS supplier_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    submitted_at TEXT DEFAULT (datetime('now')),
    extraction_status TEXT DEFAULT 'PENDING',
    extraction_confidence REAL,
    commercial_notes TEXT,
    unresolved_items TEXT,
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS extracted_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    rfx_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    line_item_id INTEGER,
    item_description_supplier TEXT,
    orig_price REAL,
    orig_unit TEXT,
    orig_currency TEXT DEFAULT 'INR',
    norm_price_per_unit REAL,
    norm_unit TEXT DEFAULT 'per piece',
    discount_pct REAL DEFAULT 0,
    freight_included INTEGER DEFAULT 0,
    freight_per_unit REAL DEFAULT 0,
    gst_rate REAL DEFAULT 18,
    landed_cost_excl_gst REAL,
    lead_time_days INTEGER,
    moq INTEGER,
    tech_compliance TEXT DEFAULT 'UNKNOWN',
    notes TEXT,
    confidence REAL DEFAULT 0.0,
    source_ref TEXT,
    orig_value_raw TEXT,
    is_manual_override INTEGER DEFAULT 0,
    override_reason TEXT,
    override_by TEXT,
    override_at TEXT,
    FOREIGN KEY (submission_id) REFERENCES supplier_submissions(id),
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (line_item_id) REFERENCES line_items(id)
);

CREATE TABLE IF NOT EXISTS questionnaire_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    rfx_id INTEGER NOT NULL,
    question_code TEXT NOT NULL,
    question_text TEXT,
    answer TEXT,
    is_compliant INTEGER,
    is_mandatory INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (submission_id) REFERENCES supplier_submissions(id)
);

CREATE TABLE IF NOT EXISTS analyst_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER,
    query_text TEXT NOT NULL,
    response_text TEXT,
    response_data TEXT,
    chart_type TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER,
    event_type TEXT NOT NULL,
    event_detail TEXT,
    performed_by TEXT DEFAULT 'system',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS award_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfx_id INTEGER NOT NULL,
    supplier_id INTEGER,
    line_item_id INTEGER,
    allocated_qty INTEGER,
    rationale TEXT,
    status TEXT DEFAULT 'DRAFT',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (rfx_id) REFERENCES rfx_events(id)
);

-- Performance & Query DoS Mitigation Indexes
CREATE INDEX IF NOT EXISTS idx_line_items_rfx ON line_items(rfx_id);
CREATE INDEX IF NOT EXISTS idx_invitations_rfx ON rfx_invitations(rfx_id);
CREATE INDEX IF NOT EXISTS idx_submissions_rfx ON supplier_submissions(rfx_id);
CREATE INDEX IF NOT EXISTS idx_submissions_rfx_sup ON supplier_submissions(rfx_id, supplier_id);
CREATE INDEX IF NOT EXISTS idx_quotes_rfx ON extracted_quotes(rfx_id);
CREATE INDEX IF NOT EXISTS idx_quotes_sub ON extracted_quotes(submission_id);
CREATE INDEX IF NOT EXISTS idx_quotes_line_item ON extracted_quotes(line_item_id);
CREATE INDEX IF NOT EXISTS idx_award_rfx ON award_decisions(rfx_id);
CREATE INDEX IF NOT EXISTS idx_audit_rfx ON audit_log(rfx_id);
"""


async def get_db():
    ensure_db()
    return await aiosqlite.connect(DB_PATH)


async def init_db():
    ensure_db()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.commit()


# ── Generic helpers ──────────────────────────────────────────────────────────

async def fetchall(db: aiosqlite.Connection, sql: str, params=()):
    db.row_factory = aiosqlite.Row
    async with db.execute(sql, params) as cur:
        rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def fetchone(db: aiosqlite.Connection, sql: str, params=()):
    db.row_factory = aiosqlite.Row
    async with db.execute(sql, params) as cur:
        row = await cur.fetchone()
    return dict(row) if row else None


async def execute(db: aiosqlite.Connection, sql: str, params=()):
    async with db.execute(sql, params) as cur:
        last_id = cur.lastrowid
    return last_id


# ── RFx events ───────────────────────────────────────────────────────────────

async def get_all_rfx():
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchall(db, "SELECT * FROM rfx_events ORDER BY created_at DESC")


async def get_rfx_by_id(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        rfx = await fetchone(db, "SELECT * FROM rfx_events WHERE id = ?", (rfx_id,))
        if rfx:
            rfx["line_items"] = await fetchall(db, "SELECT * FROM line_items WHERE rfx_id = ? ORDER BY item_number", (rfx_id,))
            rfx["questionnaire"] = await fetchall(db, "SELECT * FROM questionnaire_items WHERE rfx_id = ?", (rfx_id,))
        return rfx


async def create_rfx(rfx_number, title, description, category="Corrugated Packaging",
                     status="DRAFT", deadline=None, buyer_name="Priya Krishnamurthy",
                     buyer_email="priya.k@fmcgco.in"):
    async with aiosqlite.connect(DB_PATH) as db:
        rfx_id = await execute(
            db,
            "INSERT INTO rfx_events (rfx_number, title, description, category, status, deadline, buyer_name, buyer_email) VALUES (?,?,?,?,?,?,?,?)",
            (rfx_number, title, description, category, status, deadline, buyer_name, buyer_email)
        )
        await db.commit()
    return rfx_id


async def update_rfx(rfx_id: int, updates: dict):
    """Update RFx details like title, description, deadline, status, category."""
    allowed = {"title", "description", "category", "status", "deadline", "buyer_name", "buyer_email"}
    fields = [k for k in updates if k in allowed]
    if not fields:
        return
    set_clause = ", ".join(f"{f}=?" for f in fields)
    params = [updates[f] for f in fields] + [rfx_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE rfx_events SET {set_clause} WHERE id=?", params)
        await db.commit()


# ── Line items ────────────────────────────────────────────────────────────────

async def insert_line_item(rfx_id: int, item: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        item_id = await execute(
            db,
            """INSERT INTO line_items
               (rfx_id, item_number, description, spec_ply, spec_flute, spec_gsm,
                spec_dimensions, spec_print, spec_ect_min, fefco_code, quantity, unit, annual_volume, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rfx_id, item.get("item_number"), item.get("description"), item.get("spec_ply"),
             item.get("spec_flute"), item.get("spec_gsm"), item.get("spec_dimensions"),
             item.get("spec_print"), item.get("spec_ect_min"), item.get("fefco_code"),
             item.get("quantity"), item.get("unit", "pieces"), item.get("annual_volume"),
             item.get("notes"))
        )
        await db.commit()
    return item_id


async def get_line_items(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchall(db, "SELECT * FROM line_items WHERE rfx_id = ? ORDER BY item_number", (rfx_id,))


async def get_line_item_by_id(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchone(db, "SELECT * FROM line_items WHERE id = ?", (item_id,))


async def update_line_item(item_id: int, updates: dict):
    allowed = {
        "item_number", "description", "spec_ply", "spec_flute", "spec_gsm",
        "spec_dimensions", "spec_print", "spec_ect_min", "fefco_code",
        "quantity", "unit", "annual_volume", "notes"
    }
    fields = [k for k in updates if k in allowed]
    if not fields:
        return
    set_clause = ", ".join(f"{f}=?" for f in fields)
    params = [updates[f] for f in fields] + [item_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE line_items SET {set_clause} WHERE id=?", params)
        await db.commit()


async def delete_line_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM extracted_quotes WHERE line_item_id=?", (item_id,))
        await db.execute("DELETE FROM award_decisions WHERE line_item_id=?", (item_id,))
        await db.execute("DELETE FROM line_items WHERE id=?", (item_id,))
        await db.commit()


# ── Suppliers ─────────────────────────────────────────────────────────────────

async def get_all_suppliers():
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchall(db, "SELECT * FROM suppliers ORDER BY name")


async def get_supplier_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchone(db, "SELECT * FROM suppliers WHERE code = ?", (code,))


async def insert_supplier(supplier: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        sup_id = await execute(
            db,
            "INSERT OR IGNORE INTO suppliers (name, code, contact_email, contact_name, city, certifications, tier) VALUES (?,?,?,?,?,?,?)",
            (supplier["name"], supplier["code"], supplier.get("contact_email"),
             supplier.get("contact_name"), supplier.get("city"),
             supplier.get("certifications"), supplier.get("tier", "Approved"))
        )
        await db.commit()
    return sup_id


# ── Questionnaire ─────────────────────────────────────────────────────────────

async def insert_questionnaire_item(rfx_id: int, item: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        q_id = await execute(
            db,
            "INSERT INTO questionnaire_items (rfx_id, question_code, question_text, is_mandatory, answer_type) VALUES (?,?,?,?,?)",
            (rfx_id, item["question_code"], item["question_text"],
             item.get("is_mandatory", 0), item.get("answer_type", "TEXT"))
        )
        await db.commit()
    return q_id


# ── Invitations ───────────────────────────────────────────────────────────────

async def create_invitation(rfx_id: int, supplier_id: int, response_deadline: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        inv_id = await execute(
            db,
            "INSERT INTO rfx_invitations (rfx_id, supplier_id, response_deadline) VALUES (?,?,?)",
            (rfx_id, supplier_id, response_deadline)
        )
        await db.commit()
    return inv_id


async def mark_invitations_sent(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        # Check existing invitations for this RFx
        rows = await fetchall(db, "SELECT supplier_id FROM rfx_invitations WHERE rfx_id=?", (rfx_id,))
        existing_sup_ids = {r["supplier_id"] for r in rows}
        
        # Fetch all approved suppliers
        suppliers = await fetchall(db, "SELECT id FROM suppliers")
        for s in suppliers:
            sid = s["id"]
            if sid in existing_sup_ids:
                await db.execute(
                    "UPDATE rfx_invitations SET status='SENT', sent_at=datetime('now') WHERE rfx_id=? AND supplier_id=?",
                    (rfx_id, sid)
                )
            else:
                await db.execute(
                    "INSERT INTO rfx_invitations (rfx_id, supplier_id, response_deadline, status, sent_at) VALUES (?,?,?,?,datetime('now'))",
                    (rfx_id, sid, "2026-11-01", "SENT")
                )
        await db.commit()


# ── Submissions ───────────────────────────────────────────────────────────────

async def insert_submission(rfx_id: int, supplier_id: int, file_name: str,
                             file_type: str, file_path: str, submitted_at: str):
    async with aiosqlite.connect(DB_PATH) as db:
        sub_id = await execute(
            db,
            "INSERT INTO supplier_submissions (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at) VALUES (?,?,?,?,?,?)",
            (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at)
        )
        await db.commit()
    return sub_id


async def upsert_submission(rfx_id: int, supplier_id: int, file_name: str,
                            file_type: str, file_path: str, submitted_at: str):
    """
    Update existing submission or insert new.
    Resets extraction state and cleans prior quotes if replaced.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await fetchone(
            db,
            "SELECT id FROM supplier_submissions WHERE rfx_id=? AND supplier_id=?",
            (rfx_id, supplier_id)
        )
        if existing:
            sub_id = existing["id"]
            # Clear old quotes and questionnaire responses
            await db.execute("DELETE FROM extracted_quotes WHERE submission_id=?", (sub_id,))
            await db.execute("DELETE FROM questionnaire_responses WHERE submission_id=?", (sub_id,))
            await db.execute(
                """UPDATE supplier_submissions 
                   SET file_name=?, file_type=?, file_path=?, submitted_at=?,
                       extraction_status='PENDING', extraction_confidence=NULL,
                       commercial_notes=NULL, unresolved_items=NULL
                   WHERE id=?""",
                (file_name, file_type, file_path, submitted_at, sub_id)
            )
            await db.commit()
            return sub_id
        else:
            sub_id = await execute(
                db,
                "INSERT INTO supplier_submissions (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at) VALUES (?,?,?,?,?,?)",
                (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at)
            )
            await db.commit()
            return sub_id


async def get_submissions(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await fetchall(
            db,
            """SELECT ss.*, s.name as supplier_name, s.code as supplier_code,
                      s.city as supplier_city, s.certifications as supplier_certifications
               FROM supplier_submissions ss
               JOIN suppliers s ON ss.supplier_id = s.id
               WHERE ss.rfx_id = ?
               ORDER BY s.name""",
            (rfx_id,)
        )
        for r in rows:
            certs = (r.get("supplier_certifications") or "").lower()
            r["brc_qualified"] = "brc/iop" in certs
        return rows


async def get_submission(rfx_id: int, supplier_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchone(
            db,
            "SELECT * FROM supplier_submissions WHERE rfx_id=? AND supplier_id=?",
            (rfx_id, supplier_id)
        )


async def update_submission_extraction(submission_id: int, status: str,
                                        confidence: float, commercial_notes: str,
                                        unresolved_items: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE supplier_submissions SET extraction_status=?, extraction_confidence=?, commercial_notes=?, unresolved_items=? WHERE id=?",
            (status, confidence, commercial_notes, unresolved_items, submission_id)
        )
        await db.commit()


# ── Extracted quotes ──────────────────────────────────────────────────────────

async def insert_extracted_quote(quote: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        q_id = await execute(
            db,
            """INSERT INTO extracted_quotes
               (submission_id, rfx_id, supplier_id, line_item_id,
                item_description_supplier, orig_price, orig_unit, orig_currency,
                norm_price_per_unit, norm_unit, discount_pct, freight_included,
                freight_per_unit, gst_rate, landed_cost_excl_gst, lead_time_days,
                moq, tech_compliance, notes, confidence, source_ref, orig_value_raw)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (quote["submission_id"], quote["rfx_id"], quote["supplier_id"],
             quote.get("line_item_id"), quote.get("item_description_supplier"),
             quote.get("orig_price"), quote.get("orig_unit"), quote.get("orig_currency", "INR"),
             quote.get("norm_price_per_unit"), quote.get("norm_unit", "per piece"),
             quote.get("discount_pct", 0), 1 if quote.get("freight_included") else 0,
             quote.get("freight_per_unit", 0), quote.get("gst_rate", 18),
             quote.get("landed_cost_excl_gst"),
             quote.get("lead_time_days"), quote.get("moq"),
             quote.get("tech_compliance", "UNKNOWN"),
             quote.get("notes"), quote.get("confidence", 0.0),
             quote.get("source_ref"), quote.get("orig_value_raw"))
        )
        await db.commit()
    return q_id


async def get_extracted_quotes(rfx_id: int, supplier_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if supplier_id:
            return await fetchall(
                db,
                "SELECT * FROM extracted_quotes WHERE rfx_id=? AND supplier_id=? ORDER BY line_item_id",
                (rfx_id, supplier_id)
            )
        return await fetchall(
            db,
            "SELECT * FROM extracted_quotes WHERE rfx_id=? ORDER BY supplier_id, line_item_id",
            (rfx_id,)
        )


async def update_extracted_quote(quote_id: int, field: str, new_value,
                                  reason: str, override_by: str = "analyst"):
    allowed_fields = {
        "orig_price", "norm_price_per_unit", "discount_pct", "freight_per_unit",
        "gst_rate", "landed_cost_excl_gst", "lead_time_days", "moq",
        "tech_compliance", "notes", "confidence"
    }
    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' not allowed for override")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE extracted_quotes SET {field}=?, is_manual_override=1, override_reason=?, override_by=?, override_at=datetime('now') WHERE id=?",
            (new_value, reason, override_by, quote_id)
        )
        await db.commit()


# ── Questionnaire responses ───────────────────────────────────────────────────

async def insert_questionnaire_response(resp: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        r_id = await execute(
            db,
            """INSERT INTO questionnaire_responses
               (submission_id, supplier_id, rfx_id, question_code, question_text, answer, is_compliant, is_mandatory, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (resp["submission_id"], resp["supplier_id"], resp["rfx_id"],
             resp["question_code"], resp.get("question_text"), resp.get("answer"),
             resp.get("is_compliant"), resp.get("is_mandatory", 0), resp.get("notes"))
        )
        await db.commit()
    return r_id


async def get_questionnaire_responses(rfx_id: int, supplier_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if supplier_id:
            return await fetchall(
                db,
                "SELECT * FROM questionnaire_responses WHERE rfx_id=? AND supplier_id=?",
                (rfx_id, supplier_id)
            )
        return await fetchall(
            db,
            "SELECT * FROM questionnaire_responses WHERE rfx_id=?",
            (rfx_id,)
        )


# ── Audit log ─────────────────────────────────────────────────────────────────

async def add_audit_log(rfx_id: int, event_type: str, event_detail: str,
                         performed_by: str = "system"):
    async with aiosqlite.connect(DB_PATH) as db:
        await execute(
            db,
            "INSERT INTO audit_log (rfx_id, event_type, event_detail, performed_by) VALUES (?,?,?,?)",
            (rfx_id, event_type, event_detail, performed_by)
        )
        await db.commit()


async def get_audit_log(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchall(
            db,
            "SELECT * FROM audit_log WHERE rfx_id=? ORDER BY created_at DESC",
            (rfx_id,)
        )


# ── Analyst queries ───────────────────────────────────────────────────────────

async def save_analyst_query(rfx_id: int, query_text: str, response_text: str,
                              response_data: str = None, chart_type: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        q_id = await execute(
            db,
            "INSERT INTO analyst_queries (rfx_id, query_text, response_text, response_data, chart_type) VALUES (?,?,?,?,?)",
            (rfx_id, query_text, response_text, response_data, chart_type)
        )
        await db.commit()
    return q_id


# ── Award decisions ───────────────────────────────────────────────────────────

async def save_award_decision(rfx_id: int, supplier_id: int, line_item_id: int,
                               allocated_qty: int, rationale: str, status: str = "DRAFT"):
    async with aiosqlite.connect(DB_PATH) as db:
        d_id = await execute(
            db,
            "INSERT INTO award_decisions (rfx_id, supplier_id, line_item_id, allocated_qty, rationale, status) VALUES (?,?,?,?,?,?)",
            (rfx_id, supplier_id, line_item_id, allocated_qty, rationale, status)
        )
        await db.commit()
    return d_id


async def clear_award_decisions(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM award_decisions WHERE rfx_id=?", (rfx_id,))
        await db.commit()


async def bulk_save_award_decisions(rfx_id: int, allocations: list, status: str = "APPROVED"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM award_decisions WHERE rfx_id=?", (rfx_id,))
        for item in allocations:
            await db.execute(
                "INSERT INTO award_decisions (rfx_id, supplier_id, line_item_id, allocated_qty, rationale, status) VALUES (?,?,?,?,?,?)",
                (rfx_id, item.get("supplier_id"), item.get("line_item_id"),
                 item.get("allocated_qty", 0), item.get("rationale", ""), status)
            )
        await db.commit()


async def get_award_decisions(rfx_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        return await fetchall(
            db,
            """SELECT ad.*, s.name as supplier_name, s.code as supplier_code,
                      li.item_number, li.description as item_description
               FROM award_decisions ad
               LEFT JOIN suppliers s ON ad.supplier_id = s.id
               LEFT JOIN line_items li ON ad.line_item_id = li.id
               WHERE ad.rfx_id=?
               ORDER BY li.item_number""",
            (rfx_id,)
        )
