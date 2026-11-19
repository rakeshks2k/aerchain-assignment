# Aerchain RFx Intelligence Platform
> **"Kill the Quote Spreadsheet"** — AI-Native Autonomous Sourcing & Commercial Comparison Engine for Enterprise Procurement

---

## Executive Overview

Enterprise category buyers spend 3 to 9 days per RFx event manually reading disparate supplier quotation formats — complex multi-sheet Excels, branded PDFs with footnote terms, unstructured Word documents, mobile photos of printed rate cards, and terse informal emails.

**Aerchain RFx Intelligence** eliminates this manual friction by unifying:
1. **AI-Assisted RFx Generation:** Creates structured 30-item packaging scopes and 10 technical qualification questions from plain natural language.
2. **Multiformat Document Intelligence:** Extracts commercial rates, footnote discounts, taxes, freight terms, and questionnaire answers across 5 unstructured supplier file formats (**Excel, PDF, Word, Photographed Rate Card, and Email**).
3. **Automated Normalization Engine:** Converts disparate units (per-sqm, per-kg, per-sheet) into standardized per-piece landed costs in INR, taking into account volume discounts, freight terms, and GST classifications.
4. **Unified Comparison Workspace:** A 30×5 sticky-header matrix with dynamic BRC qualification filtering, visual confidence indicators, and drill-down source attribution.
5. **Conversational Procurement Analyst Copilot:** Combines intent classification, deterministic arithmetic modeling, and LLM reasoning to answer complex split-award and margin variance queries with real charts and data tables.
6. **Scenario Award Modeling & CSV Export:** Compares single-source awards vs. multi-vendor split allocations and produces instant audit-compliant CSV downloads.

---

## Live Demonstration Stack

- **Backend:** Python FastAPI, `aiosqlite` (Async SQLite 3), `google-generativeai` (Gemini 2.0 Flash / 1.5 Flash), `openpyxl`, `PyPDF2`, `python-docx`, `Pillow`, `fpdf2`, `numpy`.
- **Frontend:** Vanilla ES6+ SPA (Zero build step, high performance), Chart.js 4.4, Inter Typography, Responsive Enterprise Design System.
- **Data Scale:** 30 corrugated packaging line items, 5 distinct suppliers, 10 qualification criteria, 5 authentic format submissions.

---

## Quick Start & Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher (use `py -3` on Windows)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Install Python Dependencies
Open PowerShell or your terminal in the project directory:
```powershell
py -3 -m pip install -r backend/requirements.txt
```

### 3. Configure LLM API Keys (Groq Cloud Recommended)
Copy the template configuration file:
```powershell
Copy-Item backend/.env.example backend/.env
```
Open `backend/.env` and insert your API keys:
```env
# RECOMMENDED & PRIORITIZED: Free Groq Cloud API Key (Llama 3.3 70B with ultra-fast tool calling)
# Get a free key with zero card required at: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_actual_groq_key_here

# Alternative LLM Providers:
# GOOGLE_GENERATIVEAI_API_KEY=your_actual_gemini_api_key_here
# OPENAI_API_KEY=sk-proj-your_actual_openai_key_here
```
*(Note: If no API key is configured, the application's deterministic backend analytical tool layer continues to execute all mathematical calculations, landed cost formulas, and split-award optimizations directly against SQLite without crashing).*

### 4. Database Verification
The SQLite database at `backend/data/aerchain.db` is already pre-seeded with 1 RFx event, 30 line items, 5 suppliers, and 5 supplier submission attachments.

*(Optional)* To re-seed from scratch:
```powershell
cd backend
py -3 seed_data.py
cd ..
```

### 5. Launch the Application
Run the backend server directly from the `backend/` directory:
```powershell
cd backend
py -3 -m uvicorn main:app --reload --port 8000
```

### 6. Access the Web App
Open your browser and navigate to:
**[http://localhost:8000](http://localhost:8000)**

---

## Sourcing Scenario & Data Highlights

| Supplier Code | Supplier Name | Response Format | Quoted Items | BRC Certified? | Key Commercial Nuance Extracted |
|---|---|---|---|---|---|
| **PKI** | PackIndia Ltd | **Excel (.xlsx)** | 28 / 30 | **YES (Grade A)** | Items 12 & 13 quoted per sqm; Item 18 quoted "On Request"; Freight included >₹50k |
| **EBS** | EcoBox Solutions | **PDF Document** | 30 / 30 | **NO (Pending Q1'27)** | **8% trade discount buried in footnote 1**; claims 12% GST (requires review) |
| **IPI** | IndoPack Industries | **Word (.docx)** | 29 / 30 | **YES** | Quoted FOR Chennai + ₹2.50/kg freight; Item 29 is **SUBSTITUTE** proposal |
| **PCO** | PremiumCorrugated | **Photo (.jpg)** | 30 / 30 | **YES (Grade AA)** | Photographed rate card (1.8° tilt, noise); 7% volume discount tier applied |
| **RPC** | RegionalPacks Co | **Email Text** | 17 / 30 | **NO** | States *"rest same as last year"*; flagged **UNRESOLVED** (confidence 0.10) |

---

## Verification & Interactive Walkthrough

1. **Dashboard:** View active RFx statistics, supplier submission counts, and live audit ledger.
2. **RFx Events:** Inspect all 30 corrugated packaging SKUs and 10 technical questionnaire items. Click **"📧 Send Invitations"** to preview simulated dispatch.
3. **Supplier Submissions:** Click **"⚡ Extract Data"** on any supplier row to trigger AI parsing. Click **"Inspect Quotes ▾"** to review line-level extractions and questionnaire evaluations.
4. **Comparison Workspace:** 
   - View the 30×5 price comparison grid.
   - Click the **"BRC Qualified Only"** toggle to disqualify EBS and RPC.
   - Click any price cell to slide out the **Quote Detail Panel** (shows original rates, normalized per-piece landed cost, discount, and document source reference).
   - Click **"✏️ Correct This Value"** to execute a manual audit override.
5. **Procurement Analyst Copilot:** Click any sample chip or type questions:
   - *"Cheapest supplier per line item (BRC qualified only)"*
   - *"Single supplier vs split award financial comparison"*
   - *"Quotes requiring manual review or verification"*
6. **Award & Export:** Review the single-supplier vs. split-award savings comparison and click **"📊 Export Comparison CSV"** or **"📄 Download Award Summary"**.

---

## Submission Documentation Index

- **[Product Decision Note](docs/product-decision-note.md):** 1-page Senior PM brief detailing the core problem, product thesis, trade-offs, and deliberate exclusions.
- **[Implementation Documentation](docs/implementation-documentation.md):** Full technical architecture, AI loop mechanics, database schema, normalization formulas, and trust safeguards.
- **[Live Demonstration Runbook](docs/demo-runbook.md):** Step-by-step 15-minute interview demonstration script with anticipated executive questions.
