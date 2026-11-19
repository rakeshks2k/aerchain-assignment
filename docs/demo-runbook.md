# Aerchain RFx Intelligence — Live Demonstration Runbook
**Document Type:** 15-Minute Live Product Demonstration Runbook  
**Target Audience:** Enterprise Category Buyers, Procurement Leadership & Technical Reviewers  
**Scenario:** FMCG Corrugated Packaging Annual Contract (RFX-2026-001)  
**Live Production URL:** [https://aerchain-dashboard.vercel.app](https://aerchain-dashboard.vercel.app)  
**Local Fallback URL:** `http://localhost:8000`  
**Duration:** 15 Minutes  

---

## 1. Pre-Demo Preparation Checklist

Before initiating the live demonstration:
1. **Cloud Environment (Recommended):** Open Chrome or Edge and navigate directly to:  
   **`https://aerchain-dashboard.vercel.app`**
2. **Local Environment (Optional Fallback):**
   ```powershell
   cd backend
   py -3 -m uvicorn main:app --reload --port 8000
   ```
   Navigate to `http://localhost:8000`.
3. **Screen Setup:** Maximize the browser window (1080p or 1440p) so the 30×5 sticky table displays comfortably with zero horizontal scroll clipping.
4. **Terminal / Verification Tab:** Have a second tab open to `/api/health` or terminal running `py -m pytest tests/` (65/65 tests passing) if technical reviewers request architectural validation.

---

## 2. 15-Minute Live Demonstration Timeline

| Time | Phase | Focus Screen | Key Talking Point |
|---|---|---|---|
| **00:00 – 02:00** | Introduction & Problem | Executive Dashboard | *"The quote spreadsheet is a symptom of supplier format mismatch."* |
| **02:00 – 04:30** | Sourcing Setup & Scope | RFx Events & Builder | 30 FEFCO packaging SKUs and 10 mandatory technical questions. |
| **04:30 – 07:30** | Multiformat Extraction | Supplier Submissions | Real extraction across Excel, PDF, Word, Photographed Rate Card, and Email. |
| **07:30 – 10:30** | Comparison Workspace | 30×5 Matrix | Normalized landed costs, BRC qualification toggle, cell drill-down, and audit override. |
| **10:30 – 13:00** | Analyst Copilot | Procurement Analyst | Plain English scenario modeling: split vs. single award and risk exceptions. |
| **13:00 – 15:00** | Strategic Decision & Export | Award & Export | Defensible allocation matrix, verified savings (₹45.05L), and CSV audit download. |

---

## 3. Step-by-Step Demonstration Script

### Act 1: The Enterprise Problem & Executive Dashboard (0:00 – 2:00)
- **Action:** Open `https://aerchain-dashboard.vercel.app` (or `localhost:8000`) to the **Procurement Dashboard**.
- **Voiceover / Talking Point:**
  > *"Enterprise category managers spend up to nine days per sourcing event manually compiling quotes. Suppliers don't fill out standardized buyer templates because they have unique cost structures, volume rebates, and logistics terms. In our scenario, Priya Krishnamurthy is sourcing 30 line items of corrugated packaging across 5 suppliers. Instead of spending her week copying and pasting rates into Excel, Aerchain RFx Intelligence provides an autonomous, auditable sourcing workflow."*
- **UI Highlights:**
  - Executive stat cards: 1 Active Event, 5 Submissions Received, 30 Line Items.
  - **Audit Ledger & Event Stream:** Live immutable ledger with colored icon circles showing real-time event logs (Copilot queries, extractions, overrides, dispatches).
  - Supplier portfolio progress bars showing allocation readiness.

---

### Act 2: RFx Specification & Qualification Setup (2:00 – 4:30)
- **Action:** Click **"RFx Events"** in the sidebar. Click **"Open Workspace →"** on `RFX-2026-001`.
- **Walkthrough:**
  1. **Line Items Tab:** Point out the 30 corrugated packaging items (RSC cartons, die-cut trays, honeycomb panels, 7-ply bulk bins) with realistic FEFCO codes, GSM liner specifications, and dimensions.
  2. **Questionnaire Tab:** Show the 10 qualification questions, emphasizing **Q1 (ISO 9001)** and **Q2 (BRC/IoP Packaging)** as mandatory disqualifying gates.
  3. **Invitations Tab:** Click **"📧 Send Invitations"**. Show the modal previewing the simulated RFx dispatch to all 5 vendor contacts, then click **"Confirm & Send"**.
- **Voiceover / Talking Point:**
  > *"Notice that we don't just ask for price. In packaging, an unqualified supplier with a 1.5% defect rate will shut down an FMCG bottling line. Technical qualification is built into the workflow from day one."*

---

### Act 3: Multiformat Document Intelligence & Extraction (4:30 – 7:30)
- **Action:** Click **"Supplier Submissions"** in the sidebar.
- **Walkthrough:**
  1. Highlight the 5 distinct submission formats:
     - **PackIndia (PKI):** Multi-sheet Excel workbook (`.xlsx`).
     - **EcoBox Solutions (EBS):** PDF quotation (`.pdf`).
     - **IndoPack Industries (IPI):** Microsoft Word (`.docx`).
     - **PremiumCorrugated (PCO):** Photographed physical rate card (`.jpg` taken at an angle on a mobile phone).
     - **RegionalPacks (RPC):** Informal plain email text (`.txt`).
  2. Click **"⚡ Extract Data"** on **EcoBox Solutions (EBS)**.
     - Show the real-time extraction progress.
     - Click **"Inspect Quotes ▾"**.
     - **Point out the critical finding:** EBS has an **8% trade discount buried in Footnote 1** and claims an incorrect 12% GST rate. The system automatically parsed the footnote, applied the discount, and flagged the tax discrepancy for human review!
  3. Click **"⚡ Extract Data"** on **RegionalPacks (RPC)**.
     - Click **"Inspect Quotes ▾"**.
     - **Point out the 'Same as Last Year' test:** Highlight how the 13 unquoted items are marked as **UNRESOLVED** (confidence 0.10) with the note: *"Historical pricing reference - no baseline available"*.
- **Voiceover / Talking Point:**
  > *"This is the difference between a prototype and an enterprise product. A naive AI would hallucinate a price. Aerchain flags the ambiguity, alerting the buyer that RegionalPacks gave an informal estimate without a baseline contract."*

---

### Act 4: The Comparison Workspace (7:30 – 10:30)
- **Action:** Click **"Comparison Workspace"** in the sidebar.
- **Walkthrough:**
  1. **The 30×5 Grid:** Point out the sticky first column and sticky header. Every cell displays normalized landed cost in INR per piece.
  2. **Color Legend:**
     - 🟢 **Green:** Lowest price among qualified vendors.
     - ⚪ **White:** Quoted rate (not lowest).
     - ⚪ **Dash (—):** SKU not quoted (e.g., PKI missing honeycomb item 27).
  3. **The BRC Filter Toggle:** Click the **"BRC Qualified Only"** toggle.
     - Watch EcoBox (EBS) and RegionalPacks (RPC) automatically gray out and receive disqualified strikethrough styling!
     - Explain why: EBS is pending certification in Q1'27, and RPC has no BRC certification.
  4. **Cell Drill-Down:** Click any price cell (e.g., PKI Item 1).
     - The **Quote Detail Panel** slides in from the right.
     - Show the exact document source reference: `Sheet: Quotation, Row 6`.
     - Show normalized rate, discount percentage, and landed cost.
  5. **Manual Audit Override:** Click **"✏️ Correct or Override This Value"**.
     - Change the normalized rate from `₹20.50` to `₹20.00`.
     - Reason: *"Supplier agreed to 50 paise volume rebate over phone"*.
     - Click **"Apply Correction"**.
     - Notice the cell now displays a ✏️ icon, the landed cost recalculates instantly, and the action is permanently written to the audit log!

---

### Act 5: Natural Language Procurement Analyst Copilot (10:30 – 13:00)
- **Action:** Click **"Procurement Analyst"** in the sidebar.
- **Walkthrough (Ask Core Acceptance Query):**
  1. Type or paste the critical Requirement F acceptance query into the chat input:
     > *"What if we split the award, choosing the cheapest supplier per line, but only among suppliers who cleared the mandatory quality questionnaire?"*
  2. **Review the Copilot Output:**
     - **Executive Answer:** Highlights that only **PKI**, **IPI**, and **PCO** are qualified, while **EBS** and **RPC** are strictly excluded.
     - **Financial Contrast:**
       - Best Single Supplier (PCO): **₹3,11,67,090.00** (covering 30/30 items).
       - Optimized Split Award: **₹26,661,540.00** (100% item coverage).
       - Verified Direct Savings: **₹4,505,550.00 (14.5%)** vs. single sourcing!
     - **Allocation Breakdown:** IndoPack (IPI) wins 26 items; PackIndia (PKI) wins 3 items; PremiumCorrugated (PCO) wins 1 specialized heavy bin.
     - **Interactive Chart:** A Chart.js bar chart comparing Single Source vs. Split Award vs. Net Savings.
     - **Structured Table & Export:** Full 30-item table with an inline **"Export Table (CSV)"** button for instant offline validation.
  3. Click a secondary suggestion chip:
     > *"Quotes requiring manual review or verification"*
     - Show how the analyst flags the RPC "same as last year" email, the EBS 12% GST claim, and the IPI Item 29 substitute proposal.
- **Voiceover / Talking Point:**
  > *"Notice that the copilot is not doing arithmetic in the LLM. It detects the buyer's intent, runs deterministic Python calculations against the SQLite database, and uses the LLM solely to synthesize the findings into executive prose."*

---

### Act 6: Award Recommendation & Audit Export (13:00 – 15:00)
- **Action:** Click **"Award & Export"** in the sidebar.
- **Walkthrough:**
  1. Review the two side-by-side decision cards:
     - **Scenario A (Single Supplier):** PremiumCorrugated Pvt Ltd at ₹3,11,67,090.00 (30/30 items covered).
     - **Scenario B (Split Award):** Optimized 3-way split at ₹2,66,61,540.00 (**saving ₹45,05,550.00**).
  2. Click **"📊 Export Comparison CSV"**.
     - Show the downloaded CSV containing all 30 line items, normalized rates, confidence levels, and lead times across all 5 suppliers.
  3. Click **"📄 Download Award Summary"**.
     - Show the generated executive memorandum with the complete allocation breakdown.
  4. Click **"✓ Approve Award Recommendation"**.
     - Confirm the executive approval modal. The button transitions to *"✓ Award Approved & Signed"*, permanently recording the buyer signature in the audit ledger.
- **Closing Statement:**
  > *"In 15 minutes, we took 5 completely chaotic supplier response documents, extracted all commercial nuances without manual data entry, filtered out non-compliant suppliers, interrogated the data in plain English, and generated an audit-defensible award decision. That is how we kill the quote spreadsheet."*

---

## 4. Anticipated Technical & Commercial Questions with Defensible Answers

### Q1: Why did you build a full workspace instead of a pure conversational chatbot?
> *"Enterprise buyers do not make ₹30M+ packaging awards based on a chatbot's conversational assertion. Sourcing requires visual scanability, row-level scrutiny, and instant comparison. The chat copilot complements the visual workspace; it does not replace it."*

### Q2: How do you prevent LLM arithmetic hallucinations?
> *"LLMs are strictly forbidden from performing mathematical calculations in this architecture. Gemini extracts the structured parameters (base price, discount percentage, freight adder). A deterministic Python normalization engine computes the landed cost. All math is mathematically verified."*

### Q3: Why did you exclude GST from the landed cost comparison?
> *"In B2B enterprise procurement, GST on corrugated packaging (HSN 4819) is an eligible Input Tax Credit (ITC) under GST Section 16. Comparing gross prices would artificially penalize suppliers quoting the correct 18% rate against suppliers claiming an incorrect 12% concession."*

### Q4: How does this scale to 500 line items or 20 suppliers?
> *"FastAPI and SQLite easily process 10,000 quote cells in under 80 milliseconds. On the frontend, virtualized rendering (such as TanStack Virtual or Clusterize.js) handles tables exceeding 500 rows with zero frame drops."*
