# backend/seed_data.py
"""
Seed the database with realistic demo data for the Aerchain RFx Intelligence prototype.
Run once AFTER supplier_docs/ files have been created.
"""
import asyncio
import os
import sys

# Ensure backend/ is on the path
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_db, DB_PATH,
    get_all_rfx, fetchone, fetchall, execute,
    add_audit_log
)
import aiosqlite

# ── Master data ───────────────────────────────────────────────────────────────

RFX = {
    "rfx_number": "RFX-2026-001",
    "title": "Corrugated Packaging Annual Contract FY2026-27",
    "category": "Corrugated Packaging",
    "description": (
        "Annual requirement for corrugated packaging materials across 30 SKUs covering "
        "shipping cartons, retail display boxes, layer pads, corner protectors, and "
        "specialty packaging. Suppliers must demonstrate ISO 9001:2015 and BRC/IoP "
        "Packaging compliance. Evaluation based on landed cost, quality certification, "
        "lead time, and production capacity."
    ),
    "status": "ACTIVE",
    "deadline": "2026-11-01",
    "buyer_name": "Priya Krishnamurthy",
    "buyer_email": "priya.k@fmcgco.in",
}

LINE_ITEMS = [
    {"item_number": 1,  "description": "RSC 3-ply Shipping Carton - Small",          "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "300x200x150mm",    "spec_print": "Plain",              "spec_ect_min": "14 ECT", "fefco_code": "0201", "quantity": 50000,  "unit": "pieces", "annual_volume": 200000},
    {"item_number": 2,  "description": "RSC 3-ply Shipping Carton - Medium",         "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "400x300x250mm",    "spec_print": "Plain",              "spec_ect_min": "14 ECT", "fefco_code": "0201", "quantity": 30000,  "unit": "pieces", "annual_volume": 120000},
    {"item_number": 3,  "description": "RSC 3-ply Shipping Carton - Large",          "spec_ply": "3-ply", "spec_flute": "C-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "600x400x400mm",    "spec_print": "Plain",              "spec_ect_min": "23 ECT", "fefco_code": "0201", "quantity": 20000,  "unit": "pieces", "annual_volume": 80000},
    {"item_number": 4,  "description": "RSC 5-ply Retail Display Carton",            "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+150+150+200",           "spec_dimensions": "350x250x300mm",    "spec_print": "2-color flexo",      "spec_ect_min": "32 ECT", "fefco_code": "0201", "quantity": 25000,  "unit": "pieces", "annual_volume": 100000},
    {"item_number": 5,  "description": "RSC 5-ply Heavy Goods Carton",               "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "500x350x400mm",    "spec_print": "Plain",              "spec_ect_min": "32 ECT", "fefco_code": "0201", "quantity": 15000,  "unit": "pieces", "annual_volume": 60000},
    {"item_number": 6,  "description": "Die-cut Shelf-ready Tray",                   "spec_ply": "3-ply", "spec_flute": "E-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "450x300x80mm",     "spec_print": "1-color flexo",      "spec_ect_min": "14 ECT", "fefco_code": "0421", "quantity": 40000,  "unit": "pieces", "annual_volume": 160000},
    {"item_number": 7,  "description": "Die-cut Packing Tray",                       "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "600x400x100mm",    "spec_print": "Plain",              "spec_ect_min": "14 ECT", "fefco_code": "0421", "quantity": 20000,  "unit": "pieces", "annual_volume": 80000},
    {"item_number": 8,  "description": "RSC 3-ply Consumer Outer Carton",            "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "250x200x200mm",    "spec_print": "1-color flexo",      "spec_ect_min": "14 ECT", "fefco_code": "0201", "quantity": 60000,  "unit": "pieces", "annual_volume": 240000},
    {"item_number": 9,  "description": "RSC 5-ply Bulk Export Carton",               "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+200+150+200",           "spec_dimensions": "700x500x500mm",    "spec_print": "Plain",              "spec_ect_min": "44 ECT", "fefco_code": "0201", "quantity": 10000,  "unit": "pieces", "annual_volume": 40000},
    {"item_number": 10, "description": "Die-cut Premium Retail Box FEFCO 0427",      "spec_ply": "3-ply", "spec_flute": "E-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "300x200x150mm",    "spec_print": "4-color offset litho","spec_ect_min": "14 ECT", "fefco_code": "0427", "quantity": 20000,  "unit": "pieces", "annual_volume": 80000},
    {"item_number": 11, "description": "RSC 3-ply Mid-range Carton",                 "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "140+90+140",                    "spec_dimensions": "350x250x200mm",    "spec_print": "2-color flexo",      "spec_ect_min": "14 ECT", "fefco_code": "0201", "quantity": 35000,  "unit": "pieces", "annual_volume": 140000},
    {"item_number": 12, "description": "Corrugated Layer Pad - 3-ply",               "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "1200x800mm",       "spec_print": "Plain",              "spec_ect_min": "14 ECT", "fefco_code": "N/A", "quantity": 100000, "unit": "pieces", "annual_volume": 400000},
    {"item_number": 13, "description": "Corrugated Layer Pad - 5-ply Heavy",         "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "150+90+150+90+150",             "spec_dimensions": "1200x1000mm",      "spec_print": "Plain",              "spec_ect_min": "32 ECT", "fefco_code": "N/A", "quantity": 50000,  "unit": "pieces", "annual_volume": 200000},
    {"item_number": 14, "description": "Corrugated Corner Protector",                "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "180+90+180",                    "spec_dimensions": "100x100x500mm",    "spec_print": "Plain",              "spec_ect_min": "N/A",    "fefco_code": "N/A", "quantity": 80000,  "unit": "pieces", "annual_volume": 320000},
    {"item_number": 15, "description": "RSC 3-ply Standard Export Carton",           "spec_ply": "3-ply", "spec_flute": "C-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "450x350x300mm",    "spec_print": "Plain",              "spec_ect_min": "23 ECT", "fefco_code": "0201", "quantity": 25000,  "unit": "pieces", "annual_volume": 100000},
    {"item_number": 16, "description": "Die-cut Lid Box 4-color Premium",            "spec_ply": "5-ply", "spec_flute": "E-Flute",   "spec_gsm": "200+90+150+90+200",             "spec_dimensions": "400x300x50mm",     "spec_print": "4-color offset litho","spec_ect_min": "32 ECT", "fefco_code": "0330", "quantity": 15000,  "unit": "pieces", "annual_volume": 60000},
    {"item_number": 17, "description": "RSC 3-ply Large Consumer Carton",            "spec_ply": "3-ply", "spec_flute": "C-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "550x400x350mm",    "spec_print": "2-color flexo",      "spec_ect_min": "23 ECT", "fefco_code": "0201", "quantity": 20000,  "unit": "pieces", "annual_volume": 80000},
    {"item_number": 18, "description": "Bulk Bin 7-ply Heavy Duty",                  "spec_ply": "7-ply", "spec_flute": "AA-Flute",  "spec_gsm": "300+180+200+180+200+180+300",   "spec_dimensions": "800x600x800mm",    "spec_print": "Plain",              "spec_ect_min": "71 ECT", "fefco_code": "0215", "quantity": 5000,   "unit": "pieces", "annual_volume": 20000},
    {"item_number": 19, "description": "Corrugated Internal Divider",                "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "300x50x200mm",     "spec_print": "Plain",              "spec_ect_min": "N/A",    "fefco_code": "N/A", "quantity": 150000, "unit": "pieces", "annual_volume": 600000},
    {"item_number": 20, "description": "RSC 5-ply Heavy Retail Carton",              "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "600x450x500mm",    "spec_print": "1-color flexo",      "spec_ect_min": "32 ECT", "fefco_code": "0201", "quantity": 10000,  "unit": "pieces", "annual_volume": 40000},
    {"item_number": 21, "description": "Die-cut Auto-lock Retail Unit",              "spec_ply": "3-ply", "spec_flute": "E-Flute",   "spec_gsm": "150+90+150",                    "spec_dimensions": "200x150x100mm",    "spec_print": "4-color offset litho","spec_ect_min": "14 ECT", "fefco_code": "0215", "quantity": 30000,  "unit": "pieces", "annual_volume": 120000},
    {"item_number": 22, "description": "RSC 3-ply Oversized Shipping Carton",        "spec_ply": "3-ply", "spec_flute": "C-Flute",   "spec_gsm": "180+90+180",                    "spec_dimensions": "800x600x600mm",    "spec_print": "Plain",              "spec_ect_min": "23 ECT", "fefco_code": "0201", "quantity": 8000,   "unit": "pieces", "annual_volume": 32000},
    {"item_number": 23, "description": "Corrugated Void Fill Sheet",                 "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "120+90+120",                    "spec_dimensions": "500x300mm (sheet)","spec_print": "Plain",              "spec_ect_min": "N/A",    "fefco_code": "N/A", "quantity": 200000, "unit": "pieces", "annual_volume": 800000},
    {"item_number": 24, "description": "RSC 5-ply Standard Industrial Carton",       "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "450x350x400mm",    "spec_print": "2-color flexo",      "spec_ect_min": "32 ECT", "fefco_code": "0201", "quantity": 20000,  "unit": "pieces", "annual_volume": 80000},
    {"item_number": 25, "description": "Telescope Top 5-ply",                        "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "600x400x100mm",    "spec_print": "Plain",              "spec_ect_min": "32 ECT", "fefco_code": "0304", "quantity": 12000,  "unit": "pieces", "annual_volume": 48000},
    {"item_number": 26, "description": "Telescope Base 5-ply",                       "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "600x400x200mm",    "spec_print": "Plain",              "spec_ect_min": "32 ECT", "fefco_code": "0303", "quantity": 12000,  "unit": "pieces", "annual_volume": 48000},
    {"item_number": 27, "description": "Honeycomb Protective Panel",                 "spec_ply": "N/A",   "spec_flute": "Honeycomb 25mm", "spec_gsm": "N/A",                    "spec_dimensions": "1200x800mm",       "spec_print": "Plain",              "spec_ect_min": "N/A",    "fefco_code": "N/A", "quantity": 10000,  "unit": "pieces", "annual_volume": 40000},
    {"item_number": 28, "description": "RSC 3-ply Pharma Outer Carton",              "spec_ply": "3-ply", "spec_flute": "B-Flute",   "spec_gsm": "140+90+140",                    "spec_dimensions": "300x250x250mm",    "spec_print": "1-color flexo",      "spec_ect_min": "14 ECT", "fefco_code": "0201", "quantity": 25000,  "unit": "pieces", "annual_volume": 100000, "notes": "Must be GMP-grade board. Moisture resistance required."},
    {"item_number": 29, "description": "RSC 5-ply Cold Chain Carton",                "spec_ply": "5-ply", "spec_flute": "BC-Flute",  "spec_gsm": "200+150+180+150+200",           "spec_dimensions": "350x300x350mm",    "spec_print": "2-color flexo",      "spec_ect_min": "32 ECT", "fefco_code": "0201", "quantity": 15000,  "unit": "pieces", "annual_volume": 60000,  "notes": "Temperature range: 2-8°C storage. Moisture barrier required."},
    {"item_number": 30, "description": "Corrugated Display Pallet 7-ply",            "spec_ply": "7-ply", "spec_flute": "AA-Flute",  "spec_gsm": "300+180+200+180+200+180+300",   "spec_dimensions": "1200x800x150mm",   "spec_print": "Plain",              "spec_ect_min": "N/A",    "fefco_code": "N/A", "quantity": 3000,   "unit": "pieces", "annual_volume": 12000},
]

SUPPLIERS = [
    {"name": "PackIndia Ltd",             "code": "PKI", "contact_email": "rahul.sharma@packindia.com",         "contact_name": "Rahul Sharma",  "city": "Pune",      "certifications": "ISO 9001:2015, BRC/IoP Packaging",                            "tier": "Preferred"},
    {"name": "EcoBox Solutions",          "code": "EBS", "contact_email": "priya.patel@ecoboxsolutions.in",     "contact_name": "Priya Patel",   "city": "Ahmedabad", "certifications": "ISO 9001:2015",                                               "tier": "Approved"},
    {"name": "IndoPack Industries",       "code": "IPI", "contact_email": "suresh.kumar@indopack.co.in",        "contact_name": "Suresh Kumar",  "city": "Chennai",   "certifications": "ISO 9001:2015, FSC-CoC, BRC/IoP Packaging",                   "tier": "Preferred"},
    {"name": "PremiumCorrugated Pvt Ltd", "code": "PCO", "contact_email": "anita.desai@premiumcorrugated.com",  "contact_name": "Anita Desai",   "city": "Mumbai",    "certifications": "ISO 9001:2015, BRC/IoP Packaging, FSC-CoC, GMP+",            "tier": "Strategic"},
    {"name": "RegionalPacks Co",          "code": "RPC", "contact_email": "vikram@regionalpacks.in",            "contact_name": "Vikram Reddy",  "city": "Hyderabad", "certifications": "ISO 9001:2015",                                               "tier": "Approved"},
]

QUESTIONNAIRE = [
    {"question_code": "Q1",  "question_text": "Is your ISO 9001:2015 certification current and valid? Please provide certificate number and expiry date.", "is_mandatory": 1, "answer_type": "TEXT"},
    {"question_code": "Q2",  "question_text": "Do you hold a current BRC/IoP Packaging Standard certification? If yes, please provide grade, certificate number, and expiry date.", "is_mandatory": 1, "answer_type": "TEXT"},
    {"question_code": "Q3",  "question_text": "Can you supply all 30 line items as specified in the technical annexure? If not, list items you cannot supply.", "is_mandatory": 1, "answer_type": "TEXT"},
    {"question_code": "Q4",  "question_text": "What is your monthly production capacity in metric tonnes?", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q5",  "question_text": "Do you have in-house printing capability? If yes, specify maximum number of colors and printing process (flexo/offset).", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q6",  "question_text": "What is your average quality rejection rate (% defective) over the last 12 months?", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q7",  "question_text": "What payment terms can you accept? (e.g., 30 days credit, advance, LC)", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q8",  "question_text": "Do you offer volume-based discounts? If yes, please describe your discount tiers.", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q9",  "question_text": "What is your minimum order quantity (MOQ) per SKU for standard and custom items?", "is_mandatory": 0, "answer_type": "TEXT"},
    {"question_code": "Q10", "question_text": "Do you hold FSC Chain of Custody (FSC-CoC) certification? Please provide certificate number.", "is_mandatory": 0, "answer_type": "TEXT"},
]

SUBMISSIONS = [
    {"supplier_code": "PKI", "file_name": "PKI_PackIndia_Quote.xlsx",        "file_type": "EXCEL", "submitted_at": "2026-10-14 09:30:00"},
    {"supplier_code": "EBS", "file_name": "EBS_EcoBox_Quote.pdf",            "file_type": "PDF",   "submitted_at": "2026-10-15 14:22:00"},
    {"supplier_code": "IPI", "file_name": "IPI_IndoPack_Quote.docx",         "file_type": "WORD",  "submitted_at": "2026-10-16 11:05:00"},
    {"supplier_code": "PCO", "file_name": "PCO_Premium_RateCard.jpg",        "file_type": "IMAGE", "submitted_at": "2026-10-17 16:45:00"},
    {"supplier_code": "RPC", "file_name": "RPC_RegionalPacks_Email.txt",     "file_type": "EMAIL", "submitted_at": "2026-10-20 15:47:00"},
]

SUPPLIER_DOCS_DIR = "c:/Users/rakes/Code/aerchain-assignment/supplier_docs"


async def seed():
    print("Initialising database …")
    await init_db()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # ── Check if already seeded ───────────────────────────────────────────
        async with db.execute("SELECT id FROM rfx_events WHERE rfx_number=?", (RFX["rfx_number"],)) as cur:
            existing = await cur.fetchone()
        if existing:
            print(f"RFx {RFX['rfx_number']} already exists (id={existing[0]}). Skipping seed.")
            return

        # ── Insert RFx event ──────────────────────────────────────────────────
        async with db.execute(
            """INSERT INTO rfx_events
               (rfx_number, title, category, description, status, deadline, buyer_name, buyer_email)
               VALUES (?,?,?,?,?,?,?,?)""",
            (RFX["rfx_number"], RFX["title"], RFX["category"], RFX["description"],
             RFX["status"], RFX["deadline"], RFX["buyer_name"], RFX["buyer_email"])
        ) as cur:
            rfx_id = cur.lastrowid
        await db.commit()
        print(f"Created RFx id={rfx_id}")

        # ── Insert line items ─────────────────────────────────────────────────
        for item in LINE_ITEMS:
            await db.execute(
                """INSERT INTO line_items
                   (rfx_id, item_number, description, spec_ply, spec_flute, spec_gsm,
                    spec_dimensions, spec_print, spec_ect_min, fefco_code,
                    quantity, unit, annual_volume, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rfx_id, item["item_number"], item["description"], item.get("spec_ply"),
                 item.get("spec_flute"), item.get("spec_gsm"), item.get("spec_dimensions"),
                 item.get("spec_print"), item.get("spec_ect_min"), item.get("fefco_code"),
                 item["quantity"], item.get("unit", "pieces"), item.get("annual_volume"),
                 item.get("notes"))
            )
        await db.commit()
        print(f"Inserted {len(LINE_ITEMS)} line items")

        # ── Insert suppliers ──────────────────────────────────────────────────
        supplier_id_map = {}
        for sup in SUPPLIERS:
            async with db.execute(
                "INSERT OR IGNORE INTO suppliers (name, code, contact_email, contact_name, city, certifications, tier) VALUES (?,?,?,?,?,?,?)",
                (sup["name"], sup["code"], sup["contact_email"], sup["contact_name"],
                 sup["city"], sup["certifications"], sup["tier"])
            ) as cur:
                sup_id = cur.lastrowid
            if sup_id == 0:
                # Already existed – fetch the id
                async with db.execute("SELECT id FROM suppliers WHERE code=?", (sup["code"],)) as cur2:
                    row = await cur2.fetchone()
                    sup_id = row[0]
            supplier_id_map[sup["code"]] = sup_id
        await db.commit()
        print(f"Inserted/confirmed {len(SUPPLIERS)} suppliers")

        # ── Insert questionnaire items ────────────────────────────────────────
        for q in QUESTIONNAIRE:
            await db.execute(
                "INSERT INTO questionnaire_items (rfx_id, question_code, question_text, is_mandatory, answer_type) VALUES (?,?,?,?,?)",
                (rfx_id, q["question_code"], q["question_text"], q["is_mandatory"], q["answer_type"])
            )
        await db.commit()
        print(f"Inserted {len(QUESTIONNAIRE)} questionnaire items")

        # ── Insert rfx_invitations ────────────────────────────────────────────
        for sup in SUPPLIERS:
            sup_id = supplier_id_map[sup["code"]]
            await db.execute(
                "INSERT INTO rfx_invitations (rfx_id, supplier_id, response_deadline, status, sent_at) VALUES (?,?,?,?,?)",
                (rfx_id, sup_id, "2026-10-20", "SENT", "2026-09-30 10:00:00")
            )
        await db.commit()
        print(f"Inserted {len(SUPPLIERS)} rfx_invitations")

        # ── Insert supplier submissions ───────────────────────────────────────
        for sub in SUBMISSIONS:
            sup_id = supplier_id_map[sub["supplier_code"]]
            file_path = f"{SUPPLIER_DOCS_DIR}/{sub['file_name']}"
            await db.execute(
                "INSERT INTO supplier_submissions (rfx_id, supplier_id, file_name, file_type, file_path, submitted_at) VALUES (?,?,?,?,?,?)",
                (rfx_id, sup_id, sub["file_name"], sub["file_type"], file_path, sub["submitted_at"])
            )
        await db.commit()
        print(f"Inserted {len(SUBMISSIONS)} supplier submissions")

        # ── Audit log entries ─────────────────────────────────────────────────
        audit_entries = [
            (rfx_id, "RFX_CREATED",       f"RFx {RFX['rfx_number']} created by {RFX['buyer_name']}",           "priya.k@fmcgco.in"),
            (rfx_id, "RFX_ACTIVATED",     f"RFx status changed to ACTIVE",                                      "priya.k@fmcgco.in"),
            (rfx_id, "INVITATIONS_SENT",  f"Invitation sent to 5 suppliers on 2026-09-30",                      "priya.k@fmcgco.in"),
            (rfx_id, "SUBMISSION_RCVD",   f"Submission received from PackIndia Ltd (PKI) on 2026-10-14",        "system"),
            (rfx_id, "SUBMISSION_RCVD",   f"Submission received from EcoBox Solutions (EBS) on 2026-10-15",     "system"),
            (rfx_id, "SUBMISSION_RCVD",   f"Submission received from IndoPack Industries (IPI) on 2026-10-16",  "system"),
            (rfx_id, "SUBMISSION_RCVD",   f"Submission received from PremiumCorrugated Pvt Ltd (PCO) on 2026-10-17", "system"),
            (rfx_id, "SUBMISSION_RCVD",   f"Submission received from RegionalPacks Co (RPC) on 2026-10-20",    "system"),
        ]
        for (rid, etype, edetail, epby) in audit_entries:
            await db.execute(
                "INSERT INTO audit_log (rfx_id, event_type, event_detail, performed_by) VALUES (?,?,?,?)",
                (rid, etype, edetail, epby)
            )
        await db.commit()
        print(f"Inserted {len(audit_entries)} audit log entries")

    print("\n✅ Seed completed successfully!")
    print(f"   RFx ID  : {rfx_id}")
    print(f"   DB path : {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(seed())
