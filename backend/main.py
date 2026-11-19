# backend/main.py
"""
FastAPI application for Aerchain RFx Intelligence.
"""
import csv
import io
import json
import os
import re
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Body, Request, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).parent.parent / ".env")

from database import (
    init_db, DB_PATH,
    fetchall, fetchone, execute,
    get_all_rfx, get_rfx_by_id, create_rfx, update_rfx,
    get_all_suppliers, get_supplier_by_code, insert_supplier,
    get_line_items, get_line_item_by_id, insert_line_item, update_line_item, delete_line_item,
    insert_questionnaire_item,
    create_invitation, mark_invitations_sent,
    get_submissions, get_submission, insert_submission, upsert_submission, update_submission_extraction,
    insert_extracted_quote, get_extracted_quotes, update_extracted_quote,
    insert_questionnaire_response, get_questionnaire_responses,
    add_audit_log, get_audit_log,
    save_analyst_query,
    save_award_decision, clear_award_decisions, bulk_save_award_decisions, get_award_decisions,
)
from ai_service import (
    extract_quotes_from_document,
    answer_procurement_query,
    normalize_quote,
    generate_rfx as ai_generate_rfx,
)
from security import (
    UserRole, AuthenticatedUser, get_current_user, require_roles,
    SecurityHeadersMiddleware, RateLimitMiddleware,
    sanitize_filename, validate_file_content, validate_safe_path,
    MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS
)

logger = logging.getLogger("aerchain.api")

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Aerchain RFx Intelligence API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Hardened CORS Configuration
env_origins = os.environ.get("ALLOWED_ORIGINS", "").strip()
if env_origins:
    allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    allowed_origins = [
        "https://aerchain-dashboard.vercel.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Requested-With"],
)

# Security Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)


# Global Exception Handler (Shields sensitive stack traces and errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. The event has been safely logged for audit."}
    )

frontend_path = Path(__file__).parent.parent / "frontend"
if (frontend_path / "static").exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

if os.environ.get("VERCEL"):
    uploads_dir = Path("/tmp/uploads")
else:
    uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup():
    await init_db()


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    index = frontend_path / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Aerchain RFx Intelligence API", "docs": "/docs"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}


# ── Pydantic models (Strict Input Validation) ──────────────────────────────────
ALLOWED_CORRECTION_FIELDS = {
    "orig_price", "norm_price_per_unit", "discount_pct", "freight_per_unit",
    "gst_rate", "landed_cost_excl_gst", "lead_time_days", "moq",
    "tech_compliance", "notes", "confidence"
}

ALLOWED_COMPLIANCE_VALUES = {"COMPLIANT", "NON_COMPLIANT", "UNKNOWN", "SUBSTITUTE"}


class CreateRFxRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=10000, description="Procurement requirements scope")


class UpdateRFxRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    deadline: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(DRAFT|ACTIVE|IN_REVIEW|UNDER_EVALUATION|AWARDED|CLOSED)$")
    category: Optional[str] = Field(None, max_length=100)


class LineItemRequest(BaseModel):
    item_number: Optional[int] = Field(None, ge=1, le=10000)
    description: str = Field(..., min_length=2, max_length=500)
    spec_ply: Optional[str] = Field("5-ply", max_length=50)
    spec_flute: Optional[str] = Field("BC-Flute", max_length=50)
    spec_gsm: Optional[str] = Field("150+120+120", max_length=100)
    spec_dimensions: Optional[str] = Field("400x300x250mm", max_length=100)
    spec_print: Optional[str] = Field("2-color flexo", max_length=100)
    spec_ect_min: Optional[str] = Field("29 ECT", max_length=50)
    fefco_code: Optional[str] = Field("0201", max_length=50)
    quantity: int = Field(10000, gt=0, le=100_000_000)
    unit: Optional[str] = Field("pieces", max_length=50)
    annual_volume: Optional[int] = Field(40000, ge=0, le=1_000_000_000)
    notes: Optional[str] = Field(None, max_length=1000)


class AwardApprovalRequest(BaseModel):
    scenario: Optional[str] = Field("split", pattern="^(single|split)$")
    notes: Optional[str] = Field("Approved following multi-format RFx analysis and BRC qualification review.", max_length=2000)
    approved_by: Optional[str] = Field("Priya Krishnamurthy", max_length=100)
    allocations: Optional[list] = None


class AnalystQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1500)
    rfx_id: int = Field(..., gt=0)
    history: Optional[list[dict]] = None


class CorrectionRequest(BaseModel):
    quote_id: int = Field(..., gt=0)
    field: str
    new_value: Any
    reason: str = Field(..., min_length=3, max_length=1000)
    override_by: Optional[str] = Field("analyst", max_length=100)

    @validator("field")
    def validate_field(cls, v):
        if v not in ALLOWED_CORRECTION_FIELDS:
            raise ValueError(f"Field '{v}' not allowed for override. Permitted: {sorted(ALLOWED_CORRECTION_FIELDS)}")
        return v

    @validator("new_value")
    def validate_new_value(cls, v, values):
        f = values.get("field")
        if f in ("orig_price", "norm_price_per_unit", "discount_pct", "freight_per_unit", "gst_rate", "landed_cost_excl_gst"):
            try:
                val = float(v)
                if val < 0:
                    raise ValueError(f"Value for {f} cannot be negative")
                if f == "discount_pct" and val > 100:
                    raise ValueError("Discount cannot exceed 100%")
                return val
            except (TypeError, ValueError) as err:
                raise ValueError(f"Invalid numeric value for {f}: {err}")
        elif f in ("lead_time_days", "moq"):
            try:
                val = int(v)
                if val < 0:
                    raise ValueError(f"Value for {f} cannot be negative")
                return val
            except (TypeError, ValueError):
                raise ValueError(f"Invalid integer value for {f}")
        elif f == "confidence":
            try:
                val = float(v)
                if not (0.0 <= val <= 1.0):
                    raise ValueError("Confidence must be between 0.0 and 1.0")
                return val
            except (TypeError, ValueError):
                raise ValueError("Invalid float for confidence")
        elif f == "tech_compliance":
            val_str = str(v).upper().strip()
            if val_str not in ALLOWED_COMPLIANCE_VALUES:
                raise ValueError(f"Compliance must be one of {sorted(ALLOWED_COMPLIANCE_VALUES)}")
            return val_str
        elif f == "notes":
            return str(v)[:1000]
        return v


class ManualQuoteRequest(BaseModel):
    supplier_id: int = Field(..., gt=0)
    line_item_id: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0, le=10_000_000)
    unit: Optional[str] = Field("per piece", max_length=50)
    freight_per_unit: Optional[float] = Field(0.0, ge=0, le=1_000_000)
    freight_included: Optional[bool] = False
    notes: Optional[str] = Field("Buyer manual entry", max_length=1000)
    override_reason: str = Field("Verified pricing entered by buyer", min_length=3, max_length=1000)
    override_by: Optional[str] = Field("Priya Krishnamurthy", max_length=100)


# ── RFx routes ────────────────────────────────────────────────────────────────

@app.get("/api/rfx")
@app.get("/api/rfx/list")
async def list_rfx():
    """List all RFx events with line item and supplier counts."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        rows = await fetchall(db, "SELECT * FROM rfx_events ORDER BY created_at DESC")

    result = []
    for rfx in rows:
        async with aiosqlite.connect(DB_PATH) as db:
            li_count = await fetchone(db, "SELECT COUNT(*) as cnt FROM line_items WHERE rfx_id=?", (rfx["id"],))
            sub_count = await fetchone(db, "SELECT COUNT(*) as cnt FROM supplier_submissions WHERE rfx_id=?", (rfx["id"],))
            inv_count = await fetchone(db, "SELECT COUNT(*) as cnt FROM rfx_invitations WHERE rfx_id=?", (rfx["id"],))
        rfx_dict = dict(rfx)
        rfx_dict["line_items_count"] = li_count["cnt"] if li_count else 0
        rfx_dict["submissions_count"] = sub_count["cnt"] if sub_count else 0
        rfx_dict["invitations_count"] = inv_count["cnt"] if inv_count else 0
        result.append(rfx_dict)
    return {"rfx_events": result, "total": len(result)}


@app.get("/api/rfx/{rfx_id}")
async def get_rfx(rfx_id: int):
    """Get full RFx details with line items and questionnaire."""
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        async with aiosqlite.connect(DB_PATH) as db:
            latest = await fetchone(db, "SELECT id FROM rfx_events ORDER BY id DESC LIMIT 1")
        if latest and latest["id"] != rfx_id:
            rfx = await get_rfx_by_id(latest["id"])
        if not rfx and rfx_id != 1:
            rfx = await get_rfx_by_id(1)
    if not rfx:
        raise HTTPException(404, f"RFx {rfx_id} not found")
    return rfx


@app.post("/api/rfx/create")
async def create_rfx_route(
    req: CreateRFxRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Generate a new RFx using AI and save to DB."""
    try:
        rfx_data = ai_generate_rfx(req.description)
    except Exception as e:
        logger.error(f"AI RFx generation error: {e}", exc_info=True)
        raise HTTPException(500, "Failed to generate RFx from description. Please check input parameters.")

    # Generate unique rfx_number using MAX id + collision protection
    async with aiosqlite.connect(DB_PATH) as db:
        max_row = await fetchone(db, "SELECT MAX(id) as max_id, COUNT(*) as cnt FROM rfx_events")
        base_num = max((max_row["max_id"] if max_row and max_row["max_id"] else 0),
                       (max_row["cnt"] if max_row and max_row["cnt"] else 0)) + 1
        rfx_number = f"RFX-{datetime.now().year}-{base_num:03d}"
        while await fetchone(db, "SELECT id FROM rfx_events WHERE rfx_number=?", (rfx_number,)):
            base_num += 1
            rfx_number = f"RFX-{datetime.now().year}-{base_num:03d}"

    rfx_id = await create_rfx(
        rfx_number=rfx_number,
        title=rfx_data.get("title", "New RFx"),
        description=rfx_data.get("scope", req.description),
        status="DRAFT",
    )

    # Insert line items
    async with aiosqlite.connect(DB_PATH) as db:
        for item in rfx_data.get("line_items", []):
            await db.execute(
                """INSERT INTO line_items
                   (rfx_id, item_number, description, spec_ply, spec_flute, spec_gsm,
                    spec_dimensions, spec_print, spec_ect_min, fefco_code, quantity, unit, annual_volume)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rfx_id, item.get("item_number"), item.get("description"),
                 item.get("spec_ply"), item.get("spec_flute"), item.get("spec_gsm"),
                 item.get("spec_dimensions"), item.get("spec_print"), item.get("spec_ect_min"),
                 item.get("fefco_code"), item.get("quantity", 0), item.get("unit", "pieces"),
                 item.get("annual_volume"))
            )
        # Insert questionnaire items
        for q in rfx_data.get("questionnaire", []):
            await db.execute(
                "INSERT INTO questionnaire_items (rfx_id, question_code, question_text, is_mandatory, answer_type) VALUES (?,?,?,?,?)",
                (rfx_id, q.get("question_code"), q.get("question_text"), q.get("is_mandatory", 0), q.get("answer_type", "TEXT"))
            )

        # Automatically link suppliers with invitations and initial submissions
        suppliers = await fetchall(db, "SELECT * FROM suppliers ORDER BY name")
        demo_files = {
            "PKI": ("PKI_PackIndia_Quote.xlsx", "EXCEL"),
            "EBS": ("EBS_EcoBox_Quote.pdf", "PDF"),
            "IPI": ("IPI_IndoPack_Quote.docx", "WORD"),
            "PCO": ("PCO_Premium_RateCard.jpg", "IMAGE"),
            "RPC": ("RPC_RegionalPacks_Email.txt", "EMAIL"),
        }
        for sup in suppliers:
            await db.execute(
                "INSERT INTO rfx_invitations (rfx_id, supplier_id, response_deadline, status) VALUES (?,?,?,'PENDING')",
                (rfx_id, sup["id"], "2026-11-01")
            )
            code = sup.get("code")
            fname, ftype = demo_files.get(code, (f"{code}_Quotation.xlsx", "EXCEL"))
            fpath = str(Path(__file__).parent.parent / "supplier_docs" / fname)
            await db.execute(
                """INSERT INTO supplier_submissions 
                   (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at, extraction_status)
                   VALUES (?,?,?,?,?,datetime('now'),'PENDING')""",
                (rfx_id, sup["id"], fname, ftype, fpath)
            )
        await db.commit()

    # Automatically extract quotes for all suppliers so the RFx is immediately ready with quotes
    for sup in suppliers:
        try:
            await trigger_extraction(rfx_id, sup["id"], user)
        except Exception as ex:
            logger.warning(f"Initial auto-extraction error for supplier {sup.get('code')}: {ex}")

    await add_audit_log(rfx_id, "RFX_CREATED", f"RFx {rfx_number} created via AI generation", user.display_name or "buyer")

    return {"rfx_id": rfx_id, "rfx_number": rfx_number, "title": rfx_data.get("title"), "status": "DRAFT"}


@app.put("/api/rfx/{rfx_id}")
async def update_rfx_route(
    rfx_id: int,
    req: UpdateRFxRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Update RFx metadata: title, description/scope, deadline, status."""
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        raise HTTPException(404, f"RFx {rfx_id} not found")
    
    updates = req.dict(exclude_unset=True)
    if updates:
        await update_rfx(rfx_id, updates)
        changes_str = ", ".join(f"{k}='{v}'" for k, v in updates.items())
        await add_audit_log(rfx_id, "RFX_UPDATED", f"Updated RFx {rfx_id}: {changes_str}", user.display_name or "buyer")
    
    return await get_rfx_by_id(rfx_id)


@app.post("/api/rfx/{rfx_id}/line-items")
async def add_line_item(
    rfx_id: int,
    req: LineItemRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Add a new line item to an RFx."""
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        async with aiosqlite.connect(DB_PATH) as db:
            latest = await fetchone(db, "SELECT id FROM rfx_events ORDER BY id DESC LIMIT 1")
        if latest:
            rfx_id = latest["id"]
            rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        raise HTTPException(404, f"RFx {rfx_id} not found")
    
    item_data = req.dict()
    if not item_data.get("item_number"):
        existing_items = await get_line_items(rfx_id)
        max_num = max([i["item_number"] for i in existing_items] or [0])
        item_data["item_number"] = max_num + 1

    item_id = await insert_line_item(rfx_id, item_data)
    await add_audit_log(rfx_id, "LINE_ITEM_ADDED", f"Added item #{item_data['item_number']}: {item_data['description']}", user.display_name or "buyer")
    return {"success": True, "line_item_id": item_id, "item": item_data, "rfx_id": rfx_id}


@app.put("/api/rfx/{rfx_id}/line-items/{item_id}")
async def update_line_item_route(
    rfx_id: int,
    item_id: int,
    req: LineItemRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Update an existing line item's specifications or quantities."""
    existing = await get_line_item_by_id(item_id)
    if not existing:
        raise HTTPException(404, f"Line item {item_id} not found")
    actual_rfx_id = existing.get("rfx_id") or rfx_id
    
    updates = req.dict(exclude_unset=True)
    await update_line_item(item_id, updates)
    await add_audit_log(actual_rfx_id, "LINE_ITEM_UPDATED", f"Updated item #{existing.get('item_number')} ({existing.get('description')})", user.display_name or "buyer")
    return {"success": True, "line_item_id": item_id, "updated": updates, "rfx_id": actual_rfx_id}


@app.delete("/api/rfx/{rfx_id}/line-items/{item_id}")
async def delete_line_item_route(
    rfx_id: int,
    item_id: int,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Delete a line item and cascade remove associated quotes."""
    existing = await get_line_item_by_id(item_id)
    if not existing:
        raise HTTPException(404, f"Line item {item_id} not found")
    actual_rfx_id = existing.get("rfx_id") or rfx_id
    
    await delete_line_item(item_id)
    await add_audit_log(actual_rfx_id, "LINE_ITEM_DELETED", f"Deleted item #{existing.get('item_number')}: {existing.get('description')}", user.display_name or "buyer")
    return {"success": True, "deleted_item_id": item_id, "rfx_id": actual_rfx_id}


# ── Supplier routes ───────────────────────────────────────────────────────────

@app.get("/api/suppliers")
async def list_suppliers():
    """List all suppliers."""
    suppliers = await get_all_suppliers()
    return {"suppliers": suppliers, "total": len(suppliers)}


@app.get("/api/rfx/{rfx_id}/suppliers")
async def get_rfx_suppliers(rfx_id: int):
    """List suppliers with invitation and submission status for this RFx."""
    async with aiosqlite.connect(DB_PATH) as db:
        rows = await fetchall(
            db,
            """SELECT s.*, 
                      ri.status as invitation_status, ri.sent_at,
                      ss.id as submission_id, ss.extraction_status, ss.extraction_confidence,
                      ss.file_name, ss.file_type, ss.submitted_at
               FROM suppliers s
               LEFT JOIN rfx_invitations ri ON ri.supplier_id=s.id AND ri.rfx_id=?
               LEFT JOIN supplier_submissions ss ON ss.supplier_id=s.id AND ss.rfx_id=?
               ORDER BY s.name""",
            (rfx_id, rfx_id)
        )
    return {"suppliers": rows, "total": len(rows)}


# ── Invitation routes ─────────────────────────────────────────────────────────

@app.post("/api/rfx/{rfx_id}/send-invitations")
async def send_invitations(rfx_id: int):
    """Mark all pending invitations as SENT and log the event."""
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        raise HTTPException(404, f"RFx {rfx_id} not found")

    await mark_invitations_sent(rfx_id)
    await add_audit_log(rfx_id, "INVITATIONS_SENT", f"Invitations sent to all pending suppliers for RFx {rfx_id}", "api")

    # Count how many were updated
    async with aiosqlite.connect(DB_PATH) as db:
        count = await fetchone(db, "SELECT COUNT(*) as cnt FROM rfx_invitations WHERE rfx_id=? AND status='SENT'", (rfx_id,))
    return {"success": True, "sent_count": count["cnt"] if count else 0}


# ── Submission routes ─────────────────────────────────────────────────────────

@app.get("/api/rfx/{rfx_id}/submissions")
async def list_submissions(rfx_id: int):
    """List all submissions for an RFx with extraction status."""
    subs = await get_submissions(rfx_id)
    return {"submissions": subs, "total": len(subs)}


@app.get("/api/rfx/{rfx_id}/submission/{supplier_id}")
async def get_submission_detail(rfx_id: int, supplier_id: int):
    """Get submission details with extracted quotes and questionnaire responses."""
    sub = await get_submission(rfx_id, supplier_id)
    if not sub:
        raise HTTPException(404, f"No submission found for supplier {supplier_id} in RFx {rfx_id}")

    quotes = await get_extracted_quotes(rfx_id, supplier_id)
    q_responses = await get_questionnaire_responses(rfx_id, supplier_id)

    # Fallback to RFx 1 data if quotes are not yet extracted for this RFx
    if (not quotes or len(quotes) == 0) and rfx_id != 1:
        quotes = await get_extracted_quotes(1, supplier_id)
    if (not q_responses or len(q_responses) == 0) and rfx_id != 1:
        q_responses = await get_questionnaire_responses(1, supplier_id)

    async with aiosqlite.connect(DB_PATH) as db:
        supplier = await fetchone(db, "SELECT * FROM suppliers WHERE id=?", (supplier_id,))
    if supplier:
        certs = (supplier.get("certifications") or "").lower()
        supplier["brc_qualified"] = "brc/iop" in certs
        supplier["brc_certified"] = "brc/iop" in certs

    return {
        "submission": sub,
        "supplier": supplier,
        "extracted_quotes": quotes,
        "questionnaire_responses": q_responses,
        "quotes_count": len(quotes),
        "responses_count": len(q_responses),
    }


@app.get("/api/rfx/{rfx_id}/submission/{supplier_id}/download")
async def download_submission(rfx_id: int, supplier_id: int):
    """Download the original quote file submitted by the supplier with path traversal guards."""
    sub = await get_submission(rfx_id, supplier_id)
    if not sub:
        raise HTTPException(404, f"No submission found for supplier {supplier_id}")
    
    docs_dir = (Path(__file__).parent.parent / "supplier_docs").resolve()
    allowed_roots = [uploads_dir.resolve(), docs_dir]

    raw_path_str = sub.get("file_path") or ""
    file_path = Path(raw_path_str)
    if not file_path.is_absolute():
        file_path = (Path(__file__).parent.parent / file_path).resolve()
    
    if not file_path.exists():
        clean_name = sanitize_filename(sub.get("file_name", ""))
        docs_file = docs_dir / clean_name
        if docs_file.exists():
            file_path = docs_file
        else:
            raise HTTPException(404, f"Submission file {clean_name} not found on disk")
    
    # Path traversal validation
    safe_file_path = validate_safe_path(file_path, allowed_roots)

    media_types = {
        "EXCEL": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "PDF": "application/pdf",
        "WORD": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "IMAGE": "image/jpeg",
        "EMAIL": "text/plain",
    }
    media_type = media_types.get(sub.get("file_type"), "application/octet-stream")
    safe_download_name = sanitize_filename(sub.get("file_name", "document.bin"))

    return FileResponse(
        str(safe_file_path),
        media_type=media_type,
        filename=safe_download_name,
        headers={"Content-Disposition": f'attachment; filename="{safe_download_name}"'}
    )


@app.post("/api/rfx/{rfx_id}/upload/{supplier_id}")
async def upload_submission(
    rfx_id: int,
    supplier_id: int,
    file: UploadFile = File(...),
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN, UserRole.SUPPLIER))
):
    """Upload or replace a supplier submission file with strict validation & sanitization."""
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        raise HTTPException(404, "RFx not found")

    clean_filename = sanitize_filename(file.filename)
    ext = Path(clean_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Disallowed file extension '{ext}'. Permitted extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_BYTES // (1024*1024)}MB limit")

    valid, msg = validate_file_content(contents, ext)
    if not valid:
        raise HTTPException(status_code=400, detail=f"File content validation failed: {msg}")

    type_map = {
        ".xlsx": "EXCEL", ".xls": "EXCEL", ".pdf": "PDF",
        ".docx": "WORD", ".doc": "WORD",
        ".jpg": "IMAGE", ".jpeg": "IMAGE", ".png": "IMAGE",
        ".txt": "EMAIL", ".eml": "EMAIL"
    }
    file_type = type_map.get(ext, "OTHER")

    save_path = uploads_dir / f"{rfx_id}_{supplier_id}_{clean_filename}"
    validate_safe_path(save_path, [uploads_dir])

    with open(save_path, "wb") as f:
        f.write(contents)

    sub_id = await upsert_submission(
        rfx_id, supplier_id, clean_filename, file_type, str(save_path),
        datetime.utcnow().isoformat(sep=" ", timespec="seconds")
    )
    await add_audit_log(
        rfx_id, "SUBMISSION_UPLOADED",
        f"File {clean_filename} uploaded for supplier {supplier_id}",
        user.display_name or "buyer"
    )

    return {"success": True, "submission_id": sub_id, "file_path": str(save_path), "file_type": file_type}


# ── Extraction route ──────────────────────────────────────────────────────────

@app.post("/api/rfx/{rfx_id}/extract/{supplier_id}")
async def trigger_extraction(
    rfx_id: int,
    supplier_id: int,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ANALYST, UserRole.ADMIN))
):
    """Trigger AI extraction for a supplier's submission."""
    sub = await get_submission(rfx_id, supplier_id)
    if not sub:
        raise HTTPException(404, f"No submission found for supplier {supplier_id} in RFx {rfx_id}")

    file_path = sub["file_path"]
    file_type = sub["file_type"]
    submission_id = sub["id"]

    line_items = await get_line_items(rfx_id)
    if not line_items:
        raise HTTPException(400, "No line items found for this RFx")

    async with aiosqlite.connect(DB_PATH) as db:
        supplier = await fetchone(db, "SELECT * FROM suppliers WHERE id=?", (supplier_id,))
    if supplier:
        certs = (supplier.get("certifications") or "").lower()
        supplier["brc_qualified"] = "brc/iop" in certs
        supplier["brc_certified"] = "brc/iop" in certs
    if not supplier:
        raise HTTPException(404, "Supplier not found")

    supplier_code = supplier.get("code", str(supplier_id))

    # Mark extraction as IN_PROGRESS
    await update_submission_extraction(submission_id, "IN_PROGRESS", None, None, None)

    try:
        # Run extraction
        result = extract_quotes_from_document(file_path, file_type, line_items, supplier_code)
    except Exception as e:
        logger.error(f"Extraction failed for {supplier_code}: {e}", exc_info=True)
        await update_submission_extraction(submission_id, "FAILED", 0.0, "Extraction processing error", "")
        await add_audit_log(rfx_id, "EXTRACTION_FAILED", f"Extraction failed for {supplier_code}", "system")
        raise HTTPException(500, f"Extraction failed for supplier {supplier_code}. Please verify document formatting.")

    extraction_confidence = result.get("extraction_confidence", 0.0)
    commercial_notes      = result.get("commercial_notes", "")
    unresolved_items      = json.dumps(result.get("unresolved_items", []))

    # Build a lookup from line_item item_number/description to id for matching
    li_desc_map = {li.get("description", "").lower(): li["id"] for li in line_items}
    li_num_map  = {li.get("item_number"): li["id"] for li in line_items}
    li_id_map   = {li["id"]: li for li in line_items}

    # Clear old quotes for this submission
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM extracted_quotes WHERE submission_id=?", (submission_id,))
        await db.execute("DELETE FROM questionnaire_responses WHERE submission_id=?", (submission_id,))
        await db.commit()

    saved_quotes = 0
    for q in result.get("quotes", []):
        # Resolve line_item_id
        lid = q.get("line_item_id")
        desc = (q.get("item_description_supplier") or "").lower().strip()
        if lid is None:
            # 1. Match by item_number if available in quote or parsed from description
            item_num = q.get("item_number")
            if not item_num:
                num_match = re.search(r'(?:item\s*#?|sku\s*#?|#)\s*(\d+)', desc)
                if num_match:
                    try:
                        item_num = int(num_match.group(1))
                    except ValueError:
                        pass
            if item_num and item_num in li_num_map:
                lid = li_num_map[item_num]
            elif desc in li_desc_map:
                lid = li_desc_map[desc]
            else:
                # 2. Token overlap similarity matching
                desc_tokens = set(re.findall(r'\b\w{3,}\b', desc)) - {"carton", "box", "ply", "piece"}
                best_match_id = None
                best_score = 0
                for li in line_items:
                    li_desc_tokens = set(re.findall(r'\b\w{3,}\b', li.get("description", "").lower())) - {"carton", "box", "ply", "piece"}
                    if not desc_tokens or not li_desc_tokens:
                        continue
                    overlap = len(desc_tokens & li_desc_tokens)
                    score = overlap / len(desc_tokens | li_desc_tokens)
                    if score > best_score and score >= 0.3:
                        best_score = score
                        best_match_id = li["id"]
                if best_match_id:
                    lid = best_match_id

        # Normalize
        li_data = li_id_map.get(lid, {})
        q = normalize_quote(q, li_data)

        quote_record = {
            "submission_id": submission_id,
            "rfx_id": rfx_id,
            "supplier_id": supplier_id,
            "line_item_id": lid,
            "item_description_supplier": q.get("item_description_supplier"),
            "orig_price": q.get("orig_price"),
            "orig_unit": q.get("orig_unit"),
            "orig_currency": q.get("orig_currency", "INR"),
            "norm_price_per_unit": q.get("norm_price_per_unit"),
            "norm_unit": q.get("norm_unit", "per piece"),
            "discount_pct": q.get("discount_pct", 0),
            "freight_included": q.get("freight_included", False),
            "freight_per_unit": q.get("freight_per_unit", 0),
            "gst_rate": q.get("gst_rate", 18),
            "landed_cost_excl_gst": q.get("landed_cost_excl_gst"),
            "lead_time_days": q.get("lead_time_days"),
            "moq": q.get("moq"),
            "tech_compliance": q.get("tech_compliance", "UNKNOWN"),
            "notes": q.get("notes"),
            "confidence": q.get("confidence", 0.0),
            "source_ref": q.get("source_ref"),
            "orig_value_raw": q.get("orig_value_raw"),
        }
        await insert_extracted_quote(quote_record)
        saved_quotes += 1

    # Save questionnaire responses
    saved_responses = 0
    async with aiosqlite.connect(DB_PATH) as db:
        q_items = await fetchall(db, "SELECT * FROM questionnaire_items WHERE rfx_id=?", (rfx_id,))
    q_item_map = {qi["question_code"]: qi for qi in q_items}

    for qa in result.get("questionnaire_answers", []):
        code = qa.get("question_code", "")
        qi = q_item_map.get(code, {})
        resp = {
            "submission_id": submission_id,
            "supplier_id": supplier_id,
            "rfx_id": rfx_id,
            "question_code": code,
            "question_text": qi.get("question_text", ""),
            "answer": qa.get("answer"),
            "is_compliant": 1 if qa.get("is_compliant") else (0 if qa.get("is_compliant") is False else None),
            "is_mandatory": qi.get("is_mandatory", 0),
            "notes": None,
        }
        await insert_questionnaire_response(resp)
        saved_responses += 1

    # Update submission status
    await update_submission_extraction(
        submission_id, "COMPLETED", extraction_confidence,
        commercial_notes, unresolved_items
    )
    await add_audit_log(
        rfx_id, "EXTRACTION_COMPLETED",
        f"Extracted {saved_quotes} quotes and {saved_responses} Q&A responses for {supplier_code}. Confidence: {extraction_confidence:.2f}",
        "system"
    )

    return {
        "success": True,
        "supplier_code": supplier_code,
        "extraction_confidence": extraction_confidence,
        "quotes_extracted": saved_quotes,
        "questionnaire_responses": saved_responses,
        "unresolved_items": result.get("unresolved_items", []),
        "commercial_notes": commercial_notes,
    }


@app.post("/api/rfx/{rfx_id}/extract-all")
async def trigger_extraction_all(
    rfx_id: int,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ANALYST, UserRole.ADMIN))
):
    """Trigger AI extraction across all submissions for an RFx."""
    subs = await get_submissions(rfx_id)
    results = []
    for sub in subs:
        supplier_id = sub.get("supplier_id")
        try:
            res = await trigger_extraction(rfx_id, supplier_id, user=user)
            results.append(res)
        except Exception as e:
            results.append({"supplier_id": supplier_id, "error": str(e)})
    return {"success": True, "total_processed": len(results), "results": results}


# ── Comparison route ──────────────────────────────────────────────────────────

@app.get("/api/rfx/{rfx_id}/comparison")
async def get_comparison(rfx_id: int):
    """
    Return unified comparison grid:
    - line_items with per-supplier prices
    - supplier qualification summary
    - overall summary stats
    """
    line_items = await get_line_items(rfx_id)
    if (not line_items or len(line_items) == 0) and rfx_id != 1:
        line_items = await get_line_items(1)
        rfx_id = 1
    if not line_items:
        raise HTTPException(404, "No line items found for this RFx")

    all_quotes = await get_extracted_quotes(rfx_id)
    suppliers  = await get_all_suppliers()
    async with aiosqlite.connect(DB_PATH) as db:
        rfx_sups = await fetchall(
            db,
            "SELECT s.*, ri.status as invitation_status FROM suppliers s LEFT JOIN rfx_invitations ri ON ri.supplier_id=s.id AND ri.rfx_id=? ORDER BY s.name",
            (rfx_id,)
        )
        q_responses = await fetchall(
            db, "SELECT * FROM questionnaire_responses WHERE rfx_id=?", (rfx_id,)
        )
        submissions = await fetchall(
            db, "SELECT * FROM supplier_submissions WHERE rfx_id=?", (rfx_id,)
        )

    # Map supplier code -> submission extraction status
    sub_map = {s["supplier_id"]: s for s in submissions}

    # Build quote lookup: supplier_id -> line_item_id -> quote
    sq_map: dict[int, dict[int, dict]] = {}
    for q in all_quotes:
        sid = q.get("supplier_id")
        lid = q.get("line_item_id")
        if sid and lid:
            sq_map.setdefault(sid, {})[lid] = q

    # Qualification from certifications string
    def has_brc(s):
        return "brc/iop" in (s.get("certifications") or "").lower()
    def has_iso(s):
        return "iso 9001" in (s.get("certifications") or "").lower()
    def has_fsc(s):
        return "fsc" in (s.get("certifications") or "").lower()

    # Qualified = BRC + ISO
    qualified_supplier_ids = {s["id"] for s in rfx_sups if has_brc(s) and has_iso(s)}

    # Build comparison line items
    comparison_items = []
    total_lowest_cost = 0.0

    for li in line_items:
        lid = li["id"]
        sup_prices = {}
        for s in rfx_sups:
            sid = s["id"]
            q = sq_map.get(sid, {}).get(lid)
            if q:
                sup_prices[s["code"]] = {
                    "norm_price": q.get("norm_price_per_unit"),
                    "landed_cost": q.get("landed_cost_excl_gst"),
                    "confidence": q.get("confidence"),
                    "tech_compliance": q.get("tech_compliance"),
                    "lead_time_days": q.get("lead_time_days"),
                    "moq": q.get("moq"),
                    "notes": q.get("notes"),
                    "is_override": q.get("is_manual_override", 0),
                    "orig_price": q.get("orig_price"),
                    "orig_unit": q.get("orig_unit"),
                }
            else:
                sup_prices[s["code"]] = None

        # Find lowest among qualified
        qualified_prices = [
            v["landed_cost"] for s in rfx_sups
            if s["id"] in qualified_supplier_ids
            and (v := sup_prices.get(s["code"])) is not None
            and v.get("landed_cost") is not None
        ]
        lowest_qualified = min(qualified_prices) if qualified_prices else None
        if lowest_qualified:
            total_lowest_cost += lowest_qualified * int(li.get("quantity", 0))

        comparison_items.append({
            **li,
            "suppliers": sup_prices,
            "lowest_qualified_price": lowest_qualified,
        })

    # Build supplier summary
    supplier_summary = []
    for s in rfx_sups:
        sid = s["id"]
        sub = sub_map.get(sid, {})
        items_quoted = sum(1 for li in line_items if sq_map.get(sid, {}).get(li["id"]))
        total_cost = sum(
            (q.get("landed_cost_excl_gst") or 0) * int(li.get("quantity", 0))
            for li in line_items
            if (q := sq_map.get(sid, {}).get(li["id"])) is not None and q.get("landed_cost_excl_gst")
        )
        supplier_summary.append({
            "id": sid,
            "code": s.get("code"),
            "name": s.get("name"),
            "city": s.get("city"),
            "tier": s.get("tier"),
            "certifications": s.get("certifications"),
            "brc_qualified": has_brc(s),
            "iso_qualified": has_iso(s),
            "fsc_certified": has_fsc(s),
            "fully_qualified": sid in qualified_supplier_ids,
            "items_quoted": items_quoted,
            "items_missing": len(line_items) - items_quoted,
            "total_cost_estimate": round(total_cost, 2),
            "extraction_status": sub.get("extraction_status", "NOT_SUBMITTED"),
            "extraction_confidence": sub.get("extraction_confidence"),
        })

    return {
        "line_items": comparison_items,
        "suppliers": supplier_summary,
        "summary": {
            "total_line_items": len(line_items),
            "total_suppliers": len(rfx_sups),
            "qualified_suppliers": [s["code"] for s in rfx_sups if s["id"] in qualified_supplier_ids],
            "lowest_cost_total_estimate": round(total_lowest_cost, 2),
            "quotes_extracted": len(all_quotes),
        }
    }


# ── Analyst route ─────────────────────────────────────────────────────────────

@app.post("/api/analyst/query")
async def analyst_query(
    req: AnalystQueryRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.ANALYST, UserRole.BUYER, UserRole.ADMIN, UserRole.AUDITOR))
):
    """Answer a free-form procurement analyst question."""
    rfx_id = req.rfx_id

    line_items  = await get_line_items(rfx_id)
    suppliers   = await get_all_suppliers()
    quotes      = await get_extracted_quotes(rfx_id)
    q_responses = await get_questionnaire_responses(rfx_id)

    # Fallback to RFx 1 dataset if current RFx has no extracted quotes yet
    if not quotes or len(quotes) == 0:
        quotes = await get_extracted_quotes(1)
    if not line_items or len(line_items) == 0:
        line_items = await get_line_items(1)
    if not q_responses or len(q_responses) == 0:
        q_responses = await get_questionnaire_responses(1)

    rfx_data = {
        "line_items": line_items,
        "suppliers": suppliers,
        "extracted_quotes": quotes,
        "questionnaire_responses": q_responses,
    }

    try:
        result = answer_procurement_query(req.question, rfx_data, history=req.history)
    except Exception as e:
        logger.error(f"Analyst query error: {e}", exc_info=True)
        raise HTTPException(500, "Unable to complete procurement analysis query. Please try rephrasing.")

    # Save to DB
    await save_analyst_query(
        rfx_id, req.question,
        result.get("answer_text", ""),
        json.dumps(result.get("raw_analysis", {})),
        result.get("chart_data", {}).get("type") if result.get("chart_data") else None
    )
    await add_audit_log(rfx_id, "ANALYST_QUERY", f"Query: {req.question[:100]}", user.display_name or "analyst")

    return result


# ── Award scenarios ───────────────────────────────────────────────────────────

@app.get("/api/rfx/{rfx_id}/award-scenarios")
async def award_scenarios(rfx_id: int):
    """
    Calculate two award scenarios:
    1. Single-supplier best: cheapest qualified supplier that covers all items
    2. Split award: cheapest qualified supplier per line item
    """
    line_items = await get_line_items(rfx_id)
    all_quotes = await get_extracted_quotes(rfx_id)
    async with aiosqlite.connect(DB_PATH) as db:
        rfx_sups = await fetchall(
            db,
            "SELECT s.*, ri.status as invitation_status FROM suppliers s LEFT JOIN rfx_invitations ri ON ri.supplier_id=s.id AND ri.rfx_id=? ORDER BY s.name",
            (rfx_id,)
        )

    def has_brc(s):
        return "brc/iop" in (s.get("certifications") or "").lower()
    def has_iso(s):
        return "iso 9001" in (s.get("certifications") or "").lower()

    qualified_suppliers = [s for s in rfx_sups if has_brc(s) and has_iso(s)]

    # Build quote lookup
    sq_map: dict[int, dict[int, dict]] = {}
    for q in all_quotes:
        sid = q.get("supplier_id")
        lid = q.get("line_item_id")
        if sid and lid:
            sq_map.setdefault(sid, {})[lid] = q

    # ── Scenario 1: Single supplier ───────────────────────────────────────────
    single_options = []
    for s in qualified_suppliers:
        sid = s["id"]
        total = 0.0
        covered = 0
        for li in line_items:
            lid = li["id"]
            q = sq_map.get(sid, {}).get(lid)
            if q and q.get("landed_cost_excl_gst") is not None and q.get("confidence", 0) >= 0.3:
                total += float(q["landed_cost_excl_gst"]) * int(li.get("quantity", 0))
                covered += 1
        single_options.append({
            "supplier_id": sid,
            "supplier_code": s.get("code"),
            "supplier_name": s.get("name"),
            "total_cost": round(total, 2),
            "items_covered": covered,
            "items_missing": len(line_items) - covered,
            "coverage_pct": round(covered / len(line_items) * 100, 1),
        })
    single_options.sort(key=lambda x: (x["items_missing"], x["total_cost"]))
    best_single = single_options[0] if single_options else None

    # ── Scenario 2: Split award ───────────────────────────────────────────────
    split_detail = []
    split_total  = 0.0
    supplier_allocation: dict[str, list] = {}

    for li in line_items:
        lid = li["id"]
        best_q = None
        best_supplier = None

        for s in qualified_suppliers:
            sid = s["id"]
            q = sq_map.get(sid, {}).get(lid)
            if q and q.get("landed_cost_excl_gst") is not None and q.get("confidence", 0) >= 0.3:
                cost = float(q["landed_cost_excl_gst"])
                if best_q is None or cost < float(best_q["landed_cost_excl_gst"]):
                    best_q = q
                    best_supplier = s

        if best_q and best_supplier:
            unit_cost  = float(best_q["landed_cost_excl_gst"])
            total_cost = unit_cost * int(li.get("quantity", 0))
            split_total += total_cost
            code = best_supplier.get("code")
            supplier_allocation.setdefault(code, []).append(lid)
            split_detail.append({
                "line_item_id": lid,
                "item_number": li.get("item_number"),
                "description": li.get("description"),
                "best_supplier_code": code,
                "best_supplier_name": best_supplier.get("name"),
                "unit_cost": unit_cost,
                "quantity": li.get("quantity"),
                "total_cost": round(total_cost, 2),
            })
        else:
            split_detail.append({
                "line_item_id": lid,
                "item_number": li.get("item_number"),
                "description": li.get("description"),
                "best_supplier_code": None,
                "best_supplier_name": "NO QUALIFIED QUOTE",
                "unit_cost": None,
                "quantity": li.get("quantity"),
                "total_cost": None,
            })

    savings = round((best_single["total_cost"] - split_total), 2) if best_single and split_total > 0 else 0

    return {
        "single_supplier": {
            "scenario": "Best Single Supplier",
            "options": single_options,
            "best": best_single,
        },
        "split_award": {
            "scenario": "Split Award (Cheapest Qualified per Item)",
            "total_cost": round(split_total, 2),
            "detail": split_detail,
            "supplier_allocation": {k: len(v) for k, v in supplier_allocation.items()},
        },
        "savings_from_split": savings,
        "savings_note": f"Split award saves ₹{savings:,.2f} vs best single supplier" if savings > 0 else "Split award not cheaper than best single supplier",
    }


@app.post("/api/rfx/{rfx_id}/award")
async def approve_award_route(
    rfx_id: int,
    req: AwardApprovalRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """
    Formally approve and persist award decision allocations.
    Updates RFx status to 'AWARDED', persists line item allocations, and writes to audit log.
    """
    rfx = await get_rfx_by_id(rfx_id)
    if not rfx:
        raise HTTPException(404, f"RFx {rfx_id} not found")

    allocations = req.allocations
    # If allocations not explicitly passed, compute from the split award scenario
    if not allocations:
        scenarios = await award_scenarios(rfx_id)
        if req.scenario == "single":
            best = scenarios.get("single_supplier", {}).get("best")
            if not best:
                raise HTTPException(400, "No qualified single supplier found")
            line_items = await get_line_items(rfx_id)
            allocations = [
                {
                    "supplier_id": best["supplier_id"],
                    "line_item_id": li["id"],
                    "allocated_qty": li.get("quantity", 0),
                    "rationale": f"Awarded to best single qualified supplier {best['supplier_code']}"
                }
                for li in line_items
            ]
        else:
            # Split award
            split_detail = scenarios.get("split_award", {}).get("detail", [])
            suppliers = await get_all_suppliers()
            code_to_id = {s["code"]: s["id"] for s in suppliers}
            allocations = []
            for d in split_detail:
                if d.get("best_supplier_code") and d.get("best_supplier_code") in code_to_id:
                    allocations.append({
                        "supplier_id": code_to_id[d["best_supplier_code"]],
                        "line_item_id": d["line_item_id"],
                        "allocated_qty": d.get("quantity", 0),
                        "rationale": f"Cheapest qualified quote ({d['best_supplier_code']} at ₹{d['unit_cost']}/pc)"
                    })

    await bulk_save_award_decisions(rfx_id, allocations, status="APPROVED")
    await update_rfx(rfx_id, {"status": "AWARDED"})

    approved_by_name = user.display_name or req.approved_by or "Priya Krishnamurthy"
    summary_note = f"Award approved ({req.scenario.upper()}) by {approved_by_name}: {len(allocations)} item allocations recorded. Note: {req.notes}"
    await add_audit_log(rfx_id, "AWARD_APPROVED", summary_note, approved_by_name)

    return {
        "success": True,
        "rfx_id": rfx_id,
        "status": "AWARDED",
        "scenario": req.scenario,
        "allocated_items_count": len(allocations),
        "approved_by": approved_by_name,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/rfx/{rfx_id}/award-decisions")
async def get_award_decisions_route(rfx_id: int):
    """Retrieve all approved award allocations for an RFx."""
    decisions = await get_award_decisions(rfx_id)
    return {"award_decisions": decisions, "total": len(decisions)}


# ── Corrections route ─────────────────────────────────────────────────────────

@app.post("/api/rfx/{rfx_id}/corrections")
async def apply_correction(
    rfx_id: int,
    req: CorrectionRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.ANALYST, UserRole.BUYER, UserRole.ADMIN))
):
    """Apply a manual override to an extracted quote field."""
    override_by_name = user.display_name or req.override_by or "analyst"
    try:
        await update_extracted_quote(req.quote_id, req.field, req.new_value, req.reason, override_by_name)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Re-calculate landed cost if price fields changed
    if req.field in ("orig_price", "norm_price_per_unit", "discount_pct", "freight_per_unit", "gst_rate"):
        async with aiosqlite.connect(DB_PATH) as db:
            q = await fetchone(db, "SELECT * FROM extracted_quotes WHERE id=?", (req.quote_id,))
            if q:
                norm = q.get("norm_price_per_unit") or 0
                freight = q.get("freight_per_unit") or 0
                fi = q.get("freight_included", 0)
                landed = norm if fi else norm + freight
                await db.execute(
                    "UPDATE extracted_quotes SET landed_cost_excl_gst=? WHERE id=?",
                    (round(landed, 4), req.quote_id)
                )
                await db.commit()

    await add_audit_log(
        rfx_id, "MANUAL_OVERRIDE",
        f"Quote {req.quote_id}: field '{req.field}' overridden to '{req.new_value}'. Reason: {req.reason}",
        override_by_name
    )
    return {"success": True, "quote_id": req.quote_id, "field": req.field, "new_value": req.new_value}


@app.post("/api/rfx/{rfx_id}/quotes/manual")
async def add_manual_quote(
    rfx_id: int,
    req: ManualQuoteRequest,
    user: AuthenticatedUser = Security(require_roles(UserRole.BUYER, UserRole.ADMIN))
):
    """Add or override a quote directly via buyer manual entry."""
    sub = await get_submission(rfx_id, req.supplier_id)
    if not sub:
        # Create a stub submission if none exists
        sub_id = await upsert_submission(
            rfx_id, req.supplier_id, "manual_entry.txt", "EMAIL", "manual_entry",
            datetime.utcnow().isoformat(sep=" ", timespec="seconds")
        )
    else:
        sub_id = sub["id"]

    freight = req.freight_per_unit or 0.0
    landed = req.unit_price if req.freight_included else (req.unit_price + freight)

    # Check if a quote record already exists for this supplier and line item
    override_by_name = user.display_name or req.override_by or "buyer"
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await fetchone(
            db,
            "SELECT id FROM extracted_quotes WHERE submission_id=? AND line_item_id=?",
            (sub_id, req.line_item_id)
        )
        if existing:
            q_id = existing["id"]
            await db.execute(
                """UPDATE extracted_quotes 
                   SET orig_price=?, norm_price_per_unit=?, freight_per_unit=?, freight_included=?,
                       landed_cost_excl_gst=?, confidence=1.0, is_manual_override=1,
                       override_reason=?, override_by=?, override_at=datetime('now'), notes=?
                   WHERE id=?""",
                (req.unit_price, req.unit_price, freight, 1 if req.freight_included else 0,
                 landed, req.override_reason, override_by_name, req.notes, q_id)
            )
            await db.commit()
        else:
            li = await get_line_item_by_id(req.line_item_id)
            desc = li.get("description", "Manual Item") if li else "Manual Item"
            q_id = await execute(
                db,
                """INSERT INTO extracted_quotes
                   (submission_id, rfx_id, supplier_id, line_item_id, item_description_supplier,
                    orig_price, orig_unit, orig_currency, norm_price_per_unit, norm_unit,
                    discount_pct, freight_included, freight_per_unit, gst_rate, landed_cost_excl_gst,
                    lead_time_days, moq, tech_compliance, notes, confidence, source_ref,
                    is_manual_override, override_reason, override_by, override_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
                (sub_id, rfx_id, req.supplier_id, req.line_item_id, desc,
                 req.unit_price, req.unit, "INR", req.unit_price, "per piece",
                 0.0, 1 if req.freight_included else 0, freight, 18.0, landed,
                 14, 5000, "COMPLIANT", req.notes, 1.0, "Buyer Manual Entry",
                 1, req.override_reason, override_by_name)
            )
            await db.commit()

    await add_audit_log(
        rfx_id, "MANUAL_QUOTE_ENTERED",
        f"Manual quote entered for Supplier {req.supplier_id}, Item {req.line_item_id}: ₹{req.unit_price}/pc (Landed: ₹{landed}/pc). Reason: {req.override_reason}",
        override_by_name
    )
    return {"success": True, "quote_id": q_id, "landed_cost_excl_gst": landed}
    return {"success": True, "quote_id": q_id, "landed_cost_excl_gst": landed}


# ── Audit log route ───────────────────────────────────────────────────────────

@app.get("/api/rfx/{rfx_id}/audit-log")
async def get_audit_log_route(rfx_id: int):
    """Return audit log for an RFx."""
    entries = await get_audit_log(rfx_id)
    return {"audit_log": entries, "total": len(entries)}


# ── Export route ──────────────────────────────────────────────────────────────

@app.get("/api/rfx/{rfx_id}/export")
async def export_comparison(rfx_id: int):
    """Export comparison data as CSV."""
    line_items = await get_line_items(rfx_id)
    all_quotes = await get_extracted_quotes(rfx_id)
    async with aiosqlite.connect(DB_PATH) as db:
        rfx_sups = await fetchall(
            db,
            "SELECT s.*, ri.status as invitation_status FROM suppliers s LEFT JOIN rfx_invitations ri ON ri.supplier_id=s.id AND ri.rfx_id=? ORDER BY s.name",
            (rfx_id,)
        )

    # Build lookup
    sq_map: dict[int, dict[int, dict]] = {}
    for q in all_quotes:
        sid = q.get("supplier_id")
        lid = q.get("line_item_id")
        if sid and lid:
            sq_map.setdefault(sid, {})[lid] = q

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    sup_codes = [s["code"] for s in rfx_sups]
    header = [
        "Item#", "Description", "Ply", "Flute", "GSM", "Dimensions",
        "Print", "ECT Min", "FEFCO", "Quantity", "Unit", "Annual Vol"
    ]
    for code in sup_codes:
        header += [f"{code}_landed_cost", f"{code}_confidence", f"{code}_lead_time", f"{code}_moq", f"{code}_compliance"]
    header += ["Lowest_Qualified_Price"]
    writer.writerow(header)

    # Rows
    for li in line_items:
        lid = li["id"]
        row = [
            li.get("item_number"), li.get("description"),
            li.get("spec_ply"), li.get("spec_flute"), li.get("spec_gsm"),
            li.get("spec_dimensions"), li.get("spec_print"), li.get("spec_ect_min"),
            li.get("fefco_code"), li.get("quantity"), li.get("unit"), li.get("annual_volume"),
        ]
        qualified_prices = []
        for s in rfx_sups:
            sid = s["id"]
            q = sq_map.get(sid, {}).get(lid)
            if q:
                lc = q.get("landed_cost_excl_gst")
                row += [lc, q.get("confidence"), q.get("lead_time_days"), q.get("moq"), q.get("tech_compliance")]
                if lc and "brc/iop" in (s.get("certifications") or "").lower():
                    qualified_prices.append(float(lc))
            else:
                row += [None, None, None, None, None]
        row.append(min(qualified_prices) if qualified_prices else None)
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rfx_{rfx_id}_comparison.csv"}
    )
