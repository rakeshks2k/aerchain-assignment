"""
Supplier document generator for corrugated packaging procurement prototype.
Generates 5 supplier response files + 1 ground truth JSON.
"""

import os
import json
import random
import math

# Output directory = same folder as this script
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# SHARED ITEM MASTER (30 items)
# ─────────────────────────────────────────────────────────────────────────────
ITEMS = [
    # (num, short_desc, size, ply, flute, gsm_spec, category)
    (1,  "3-Ply RSC Small",          "300x200x150 mm", "3-Ply", "B-flute", "120+90+120 GSM",  "RSC"),
    (2,  "3-Ply RSC Medium",         "400x300x250 mm", "3-Ply", "B-flute", "120+90+120 GSM",  "RSC"),
    (3,  "3-Ply RSC Large",          "600x400x400 mm", "3-Ply", "C-flute", "150+90+150 GSM",  "RSC"),
    (4,  "5-Ply RSC Medium 2-Color", "350x250x300 mm", "5-Ply", "BC-flute","150+90+150+90+150 GSM", "RSC"),
    (5,  "5-Ply RSC Large Plain",    "500x350x400 mm", "5-Ply", "BC-flute","150+90+150+90+150 GSM", "RSC"),
    (6,  "Die-Cut Shelf-Ready Tray E-flute 1-Color","450x300x80 mm",  "3-Ply", "E-flute", "150+90+150 GSM",  "Die-Cut"),
    (7,  "Packing Tray B-flute Plain","600x400x100 mm","3-Ply", "B-flute", "120+90+120 GSM",  "Die-Cut"),
    (8,  "Consumer Outer 1-Color",   "250x200x200 mm", "3-Ply", "B-flute", "120+90+120 GSM",  "RSC"),
    (9,  "5-Ply Bulk Export Plain",  "700x500x500 mm", "5-Ply", "BC-flute","175+90+175+90+175 GSM","RSC"),
    (10, "4-Color Premium RSC",      "380x280x250 mm", "3-Ply", "B-flute", "150+90+150 GSM",  "RSC"),
    (11, "3-Ply Mid-Range 2-Color",  "350x250x200 mm", "3-Ply", "B-flute", "120+90+120 GSM",  "RSC"),
    (12, "Plain Corrugated Sheet B-flute","Sheets",    "3-Ply", "B-flute", "120+90+120 GSM",  "Sheet"),
    (13, "Laminated Layer Pad",      "Sheets",         "3-Ply", "B-flute", "150+90+150 GSM",  "Sheet"),
    (14, "Corner Protector 50mm",    "50x50x200 mm",   "Solid", "N/A",     "Solid Board",     "Accessory"),
    (15, "Export Carton C-flute",    "450x350x300 mm", "3-Ply", "C-flute", "150+90+150 GSM",  "RSC"),
    (16, "5-Ply Lid 4-Color",        "420x320x80 mm",  "5-Ply", "BC-flute","150+90+150+90+150 GSM","Die-Cut"),
    (17, "Large Consumer 2-Color",   "550x400x350 mm", "3-Ply", "C-flute", "150+90+150 GSM",  "RSC"),
    (18, "Heavy-Duty Bulk Bin 7-Ply","1200x800x900 mm","7-Ply", "BC-flute","200+90+200+90+200+90+200 GSM","Bulk"),
    (19, "Corrugated Divider Insert","Custom",         "3-Ply", "B-flute", "120+90+120 GSM",  "Insert"),
    (20, "5-Ply Heavy Retail 1-Color","600x450x500 mm","5-Ply", "BC-flute","175+90+175+90+175 GSM","RSC"),
    (21, "Auto-Lock 4-Color",        "300x200x250 mm", "3-Ply", "E-flute", "150+90+150 GSM",  "Die-Cut"),
    (22, "Oversized RSC C-flute",    "800x600x600 mm", "3-Ply", "C-flute", "175+90+175 GSM",  "RSC"),
    (23, "Void Fill Corrugated Sheet","Custom",        "3-Ply", "B-flute", "90+70+90 GSM",    "Sheet"),
    (24, "5-Ply Industrial 2-Color", "450x350x400 mm", "5-Ply", "BC-flute","175+90+175+90+175 GSM","RSC"),
    (25, "Telescope Top Box",        "400x300x150 mm", "3-Ply", "C-flute", "150+90+150 GSM",  "Telescope"),
    (26, "Telescope Base Box",       "400x300x200 mm", "3-Ply", "C-flute", "150+90+150 GSM",  "Telescope"),
    (27, "Honeycomb Panel 20mm",     "1200x800 mm",    "Honeycomb","N/A",  "Honeycomb Paper", "Specialty"),
    (28, "Pharma Carton 1-Color",    "300x250x250 mm", "3-Ply", "B-flute", "150+90+150 GSM",  "RSC"),
    (29, "Cold Chain 5-Ply",         "350x300x350 mm", "5-Ply", "BC-flute","175+90+175+90+175 GSM","RSC"),
    (30, "Heavy-Duty Pallet",        "1200x1000x150 mm","7-Ply","BC-flute","200+90+200+90+200+90+200 GSM","Pallet"),
]


# ─────────────────────────────────────────────────────────────────────────────
# 1. PKI_PackIndia_Quote.xlsx
# ─────────────────────────────────────────────────────────────────────────────
def create_pki_xlsx():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()

    # ---- Quotation Sheet ----
    ws = wb.active
    ws.title = "Quotation"

    # Company header
    ws.merge_cells("A1:K1")
    ws["A1"] = "PackIndia Ltd — Quotation"
    ws["A1"].font = Font(name="Arial", bold=True, size=16, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="1F4E79")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:K2")
    ws["A2"] = "Plot 55, Bhosari Industrial Area, Pune - 411026 | CIN: U21090MH2008PTC187654 | GST: 27AABCP1234E1Z3"
    ws["A2"].font = Font(name="Arial", size=9, color="FFFFFF")
    ws["A2"].fill = PatternFill("solid", fgColor="2E75B6")
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:K3")
    ws["A3"] = "Quotation Ref: PKI/Q/2026/1082 | Date: October 18, 2026 | To: Procurement Team, FMCGCo | Re: RFQ No. RFX-2026-001"
    ws["A3"].font = Font(name="Arial", size=9, italic=True)
    ws["A3"].fill = PatternFill("solid", fgColor="DEEAF1")
    ws["A3"].alignment = Alignment(horizontal="center")
    ws.row_dimensions[3].height = 16

    # Column headers row 5
    headers = ["Sr.No.", "Our Code", "Product Description", "Size (L x W x H)", "Ply",
               "Flute", "GSM Specification", "MOQ (Pcs)", "Unit Rate (₹)", "Lead Time (Days)", "Validity (Days)"]
    hdr_fill = PatternFill("solid", fgColor="203864")
    hdr_font = Font(name="Arial", bold=True, size=10, color="FFFFFF")
    thin = Side(style="thin", color="BBBBBB")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=5, column=col, value=h)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        c.border = border
    ws.row_dimensions[5].height = 28

    # PKI prices: items 1-30 except 27 and 30
    pki_prices = {
        1: 20.50, 2: 32.00, 3: 58.00, 4: 48.00, 5: 72.00,
        6: 28.00, 7: 24.00, 8: 18.00, 9: 120.00, 10: 35.00,
        11: 26.00, 12: "12.50/sqm", 13: "18.00/sqm", 14: 8.50, 15: 45.00,
        16: 52.00, 17: 55.00, 18: "On Request - Engineering Approval Required",
        19: 4.20, 20: 88.00, 21: 32.00, 22: 85.00, 23: 3.80,
        24: 68.00, 25: 65.00, 26: 68.00,
        28: 28.00, 29: 72.00,
    }
    # Custom die-cut items needing MOQ 2000
    custom_diecut = {6, 7, 10, 16, 19, 21}
    skipped = {27, 30}

    codes = {
        1: "PKI-RSC-3B-S", 2: "PKI-RSC-3B-M", 3: "PKI-RSC-3C-L", 4: "PKI-RSC-5BC-M",
        5: "PKI-RSC-5BC-L", 6: "PKI-DCT-3E-S", 7: "PKI-DCT-3B-P", 8: "PKI-RSC-3B-CO",
        9: "PKI-RSC-5BC-BX", 10: "PKI-RSC-3B-4C", 11: "PKI-RSC-3B-2C", 12: "PKI-SHT-3B-PL",
        13: "PKI-SHT-3B-LM", 14: "PKI-ACS-CP50", 15: "PKI-RSC-3C-EX", 16: "PKI-DCT-5BC-LID",
        17: "PKI-RSC-3C-LC", 18: "PKI-BLK-7BC-BIN", 19: "PKI-INS-3B-DIV", 20: "PKI-RSC-5BC-HR",
        21: "PKI-DCT-3E-AL", 22: "PKI-RSC-3C-OS", 23: "PKI-SHT-3B-VF", 24: "PKI-RSC-5BC-IND",
        25: "PKI-TEL-3C-TOP", 26: "PKI-TEL-3C-BASE", 28: "PKI-RSC-3B-PH", 29: "PKI-RSC-5BC-CC",
    }

    row = 6
    sr = 1
    alt_fill = PatternFill("solid", fgColor="EBF3FA")
    for item in ITEMS:
        num = item[0]
        if num in skipped:
            continue
        price = pki_prices.get(num, "N/A")
        moq = 2000 if num in custom_diecut else 1000
        lt = 21 if num in custom_diecut else 14
        fill = alt_fill if sr % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")
        vals = [sr, codes.get(num, f"PKI-{num:03d}"), item[1], item[3], item[4], item[5], item[6],
                moq, price, lt, 90]
        for col, v in enumerate(vals, start=1):
            c = ws.cell(row=row, column=col, value=v)
            c.font = Font(name="Arial", size=9)
            c.fill = fill
            c.border = border
            c.alignment = Alignment(horizontal="center" if col not in (3, 4, 7) else "left", wrap_text=True)
        row += 1
        sr += 1

    # Column widths
    col_widths = [7, 18, 32, 18, 7, 9, 22, 10, 28, 15, 12]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Freeze panes
    ws.freeze_panes = "A6"

    # ---- Terms & Conditions Sheet ----
    ws2 = wb.create_sheet("Terms & Conditions")
    ws2.merge_cells("A1:C1")
    ws2["A1"] = "TERMS & CONDITIONS"
    ws2["A1"].font = Font(name="Arial", bold=True, size=14, color="FFFFFF")
    ws2["A1"].fill = PatternFill("solid", fgColor="1F4E79")
    ws2["A1"].alignment = Alignment(horizontal="center")
    ws2.row_dimensions[1].height = 25

    tc_data = [
        ("Volume Discount", "2.5% applicable for monthly orders exceeding ₹5,00,000 per SKU"),
        ("GST", "GST @ 18% applicable on all items as per applicable HSN codes"),
        ("Freight", "Included for order value above ₹50,000 per delivery. For orders below ₹50,000 - actuals at cost"),
        ("Payment Terms", "30 days credit from invoice date"),
        ("Quote Validity", "90 days from date of quotation"),
        ("Bank Details", "Account Name: PackIndia Ltd | Bank: HDFC Bank | A/C: 50200012345678 | IFSC: HDFC0001234"),
        ("Jurisdiction", "All disputes subject to Pune jurisdiction"),
        ("Force Majeure", "Standard force majeure clause applies"),
        ("Quality", "All material supplied as per IS 2771 / IS 1397 standards unless otherwise specified"),
        ("Returns", "Returns accepted within 30 days for manufacturing defects only"),
    ]
    hdr2_fill = PatternFill("solid", fgColor="2E75B6")
    for col_let, hdr in [("A", "Clause"), ("B", "Detail")]:
        c = ws2[f"{col_let}2"]
        c.value = hdr
        c.font = Font(bold=True, color="FFFFFF", name="Arial")
        c.fill = hdr2_fill
        c.alignment = Alignment(horizontal="center")

    for i, (clause, detail) in enumerate(tc_data, start=3):
        f = PatternFill("solid", fgColor="EBF3FA" if i % 2 == 0 else "FFFFFF")
        ws2.cell(row=i, column=1, value=clause).font = Font(bold=True, name="Arial", size=10)
        ws2.cell(row=i, column=1).fill = f
        ws2.cell(row=i, column=2, value=detail).font = Font(name="Arial", size=10)
        ws2.cell(row=i, column=2).fill = f
        ws2.cell(row=i, column=2).alignment = Alignment(wrap_text=True)
        ws2.row_dimensions[i].height = 22

    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 70

    # ---- Company Profile Sheet ----
    ws3 = wb.create_sheet("Company Profile")
    ws3.merge_cells("A1:B1")
    ws3["A1"] = "COMPANY PROFILE — PackIndia Ltd"
    ws3["A1"].font = Font(name="Arial", bold=True, size=14, color="FFFFFF")
    ws3["A1"].fill = PatternFill("solid", fgColor="1F4E79")
    ws3["A1"].alignment = Alignment(horizontal="center")
    ws3.row_dimensions[1].height = 25

    profile = [
        ("Company Name", "PackIndia Ltd"),
        ("Registered Address", "Plot 55, Bhosari Industrial Area, Pune - 411026, Maharashtra"),
        ("CIN", "U21090MH2008PTC187654"),
        ("GST Number", "27AABCP1234E1Z3"),
        ("Year Established", "2008"),
        ("Production Capacity", "1500 MT/month"),
        ("ISO 9001:2015 Cert No.", "PKI/ISO/2021/0847"),
        ("ISO Validity", "Valid till March 2027"),
        ("BRC/IoP Cert No.", "BRC-PKI-2024-089"),
        ("BRC Grade", "A"),
        ("BRC Validity", "Valid till September 2027"),
        ("FSC Certified", "No"),
        ("No. of Employees", "~320"),
        ("Key Machinery", "BHS Corrugator, Bobst Die-cutters, Flexo printers (up to 4 color)"),
        ("Key Clients", "Available on request"),
        ("Contact Person", "Mr. Rajesh Pawar, Head - Sales"),
        ("Phone", "+91 020 2712 3456"),
        ("Email", "sales@packindia.in"),
    ]
    for col_let, hdr in [("A", "Attribute"), ("B", "Value")]:
        c = ws3[f"{col_let}2"]
        c.value = hdr
        c.font = Font(bold=True, color="FFFFFF", name="Arial")
        c.fill = PatternFill("solid", fgColor="2E75B6")
        c.alignment = Alignment(horizontal="center")

    for i, (attr, val) in enumerate(profile, start=3):
        f = PatternFill("solid", fgColor="EBF3FA" if i % 2 == 0 else "FFFFFF")
        ws3.cell(row=i, column=1, value=attr).font = Font(bold=True, name="Arial", size=10)
        ws3.cell(row=i, column=1).fill = f
        ws3.cell(row=i, column=2, value=val).font = Font(name="Arial", size=10)
        ws3.cell(row=i, column=2).fill = f
        ws3.row_dimensions[i].height = 18

    ws3.column_dimensions["A"].width = 25
    ws3.column_dimensions["B"].width = 60

    out_path = os.path.join(OUT_DIR, "PKI_PackIndia_Quote.xlsx")
    wb.save(out_path)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# 2. EBS_EcoBox_Quote.pdf
# ─────────────────────────────────────────────────────────────────────────────
def create_ebs_pdf():
    from fpdf import FPDF

    ebs_prices = {
        1: 17.50, 2: 27.00, 3: 48.00, 4: 40.00, 5: 62.00,
        6: 23.00, 7: 20.00, 8: 15.50, 9: 105.00, 10: 30.00,
        11: 22.00, 12: 10.80, 13: 15.50, 14: 7.20, 15: 38.00,
        16: 44.00, 17: 46.00, 18: 185.00, 19: 3.60, 20: 76.00,
        21: 27.00, 22: 72.00, 23: 3.20, 24: 58.00, 25: 56.00,
        26: 58.00, 27: 85.00, 28: 24.00, 29: 62.00, 30: 220.00,
    }
    item_units = {12: "sqm", 13: "sqm"}

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── PAGE 1 ──
    pdf.add_page()

    # Header block
    pdf.set_fill_color(0, 102, 51)
    pdf.rect(0, 0, 210, 38, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(15, 7)
    pdf.cell(0, 10, "EcoBox Solutions", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(15)
    pdf.cell(0, 5, "Plot 47, GIDC Estate, Ahmedabad - 380025, Gujarat", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 5, "CIN: U21090GJ2015PTC087654 | GST: 24AAHCE1234B1Z8", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 5, "Tel: +91 079 2283 4567 | Email: sales@ecoboxsolutions.in", ln=True)
    pdf.set_text_color(0, 0, 0)

    pdf.set_y(44)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 7, "COMMERCIAL QUOTATION", ln=True, align="C")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(240, 248, 240)
    pdf.set_draw_color(0, 102, 51)
    info_y = pdf.get_y() + 2
    pdf.set_xy(15, info_y)
    pdf.set_line_width(0.3)
    pdf.rect(15, info_y, 180, 22)
    pdf.set_xy(18, info_y + 2)
    pdf.cell(85, 5, "Quotation Ref: EBS/Q/2026/0847", ln=False)
    pdf.cell(0, 5, "Date: October 15, 2026", ln=True)
    pdf.set_x(18)
    pdf.cell(85, 5, "To: Procurement Team, FMCGCo", ln=False)
    pdf.cell(0, 5, "Re: RFQ No. RFX-2026-001", ln=True)
    pdf.set_x(18)
    pdf.cell(0, 5, "Validity: 60 days from date of quotation", ln=True)

    pdf.set_y(info_y + 26)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5,
             "Dear Procurement Team, please find below our commercial offer against your RFQ. "
             "All prices are LIST prices before standard trade discount. See footnotes for applicable discounts.",
             ln=True)
    pdf.set_text_color(0, 0, 0)

    # Table header
    pdf.set_y(pdf.get_y() + 2)
    col_w = [12, 56, 36, 20, 30, 26]
    headers = ["Item\nNo.", "Description", "Size", "Ply /\nFlute", "List Price\n(Rs/pc)", "Validity\n(Days)"]
    pdf.set_fill_color(0, 102, 51)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_line_width(0.1)
    pdf.set_draw_color(150, 150, 150)
    for w, h in zip(col_w, headers):
        pdf.multi_cell(w, 4, h, border=1, align="C", fill=True, new_x="RIGHT", new_y="TOP")
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)

    def draw_item_row(item, fill_alt):
        num = item[0]
        price = ebs_prices.get(num, "N/A")
        unit = item_units.get(num, "pc")
        price_str = f"Rs {price:.2f}/{unit}" if isinstance(price, float) else str(price)
        pdf.set_fill_color(240, 248, 240) if fill_alt else pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 7.5)
        row_data = [str(num), item[1], item[3], f"{item[4]}/{item[5]}", price_str, "60"]
        for w, d in zip(col_w, row_data):
            pdf.multi_cell(w, 4.5, d, border=1, align="C" if col_w.index(w) != 1 else "L",
                           fill=True, new_x="RIGHT", new_y="TOP")
        pdf.ln(4.5)

    for i, item in enumerate(ITEMS[:15]):
        draw_item_row(item, i % 2 == 1)

    # ── PAGE 2 ──
    pdf.add_page()

    # Smaller header on page 2
    pdf.set_fill_color(0, 102, 51)
    pdf.rect(0, 0, 210, 18, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(15, 4)
    pdf.cell(0, 6, "EcoBox Solutions - Quotation EBS/Q/2026/0847 (Page 2 of 2)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(22)

    # Table header again
    pdf.set_fill_color(0, 102, 51)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    for w, h in zip(col_w, headers):
        pdf.multi_cell(w, 4, h, border=1, align="C", fill=True, new_x="RIGHT", new_y="TOP")
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)

    for i, item in enumerate(ITEMS[15:]):
        draw_item_row(item, i % 2 == 1)

    # Footnotes
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_draw_color(0, 102, 51)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.set_y(pdf.get_y() + 3)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(50, 50, 50)
    footnotes = [
        "* All list prices are subject to our standard trade discount of 8% for order quantities as per RFQ.",
        "** Additional 2% early payment discount available for payments made within 15 days of invoice.",
        "[NOTE] BRC/IoP Packaging certification: Application submitted October 2026, expected completion Q1 2027. Currently ISO 9001:2015 certified.",
        "[NOTE] GST @ 12% applicable (Corrugated Boxes classified under HSN 4819).",
        "[NOTE] Freight charges additional at actuals from Ahmedabad. Approx Rs 2.80/kg for FTL to Pune.",
        "ISO 9001:2015 Cert No: EBS/ISO/2020/0334, Valid till: December 2026 (renewal in progress)",
        "Payment Terms: 30 days credit from invoice date.",
        "For queries contact: Mr. Amit Shah, +91 98244 56789, amit.shah@ecoboxsolutions.in",
    ]
    for fn in footnotes:
        pdf.multi_cell(0, 4, fn, ln=True)
        pdf.set_y(pdf.get_y() + 0.5)

    out_path = os.path.join(OUT_DIR, "EBS_EcoBox_Quote.pdf")
    pdf.output(out_path)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# 3. IPI_IndoPack_Quote.docx
# ─────────────────────────────────────────────────────────────────────────────
def create_ipi_docx():
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    ipi_prices = {
        1: "Rs 19.00", 2: "Rs 30.00", 3: "Rs 52.00", 4: "Rs 46.00", 5: "Rs 68.00",
        6: "Rs 26.00", 7: "Rs 22.00", 8: "Rs 17.00", 9: "Rs 112.00", 10: "Rs 33.00",
        11: "Rs 24.00", 12: "Rs 11.50/sqm", 13: "Rs 16.80/sqm", 14: "Rs 7.80",
        15: "Rs 42.00", 16: "Rs 49.00", 17: "Rs 51.00", 18: "Rs 195.00", 19: "Rs 3.90",
        20: "Rs 82.00", 21: "Rs 30.00", 22: "Rs 78.00", 23: "Rs 3.50", 24: "Rs 64.00",
        25: "Rs 62.00", 26: "Rs 65.00",
        27: "NOT SUPPLIED - recommend sourcing separately",
        28: "Rs 26.00",
        29: "Rs 68.00/pc (SUBSTITUTE PROPOSED: 5-ply wax-treated BC-flute for superior cold chain performance)",
        30: "Rs 310.00",
    }
    ipi_moq = {18: 100, 27: "N/A"}
    ipi_lt = {18: "45 days", 27: "N/A"}

    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # Company letterhead
    hdr_para = doc.add_paragraph()
    hdr_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = hdr_para.add_run("IndoPack Industries Pvt. Ltd.")
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = sub_para.add_run("Plot 112, Ambattur Industrial Estate, Chennai - 600058, Tamil Nadu")
    run2.font.size = Pt(10)
    run2.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    sub_para2 = doc.add_paragraph()
    sub_para2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run3 = sub_para2.add_run("CIN: U21090TN2010PTC098765 | GST: 33AABCI9876D1Z5 | Tel: +91 044 2625 7890")
    run3.font.size = Pt(9)
    run3.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    doc.add_paragraph()

    # Title
    title = doc.add_heading("COMMERCIAL PROPOSAL", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    # Ref para
    ref_para = doc.add_paragraph()
    ref_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ref_run = ref_para.add_run(
        "Ref: IPI/CP/2026/0934 | Date: October 22, 2026\n"
        "To: Procurement Team, FMCGCo | In Response to: RFQ No. RFX-2026-001"
    )
    ref_run.font.size = Pt(9)
    ref_run.font.italic = True

    doc.add_paragraph()

    # Section 1: Introduction
    doc.add_heading("Section 1: Introduction", level=2)
    intro1 = doc.add_paragraph(
        "IndoPack Industries Pvt. Ltd. is a leading manufacturer of corrugated packaging solutions "
        "headquartered in Chennai with over 14 years of experience serving the FMCG, Pharma, "
        "Electronics, and E-commerce sectors. Our state-of-the-art manufacturing facility spans "
        "over 85,000 sq. ft. and is equipped with BHS corrugating lines, Bobst die-cutters, "
        "and 4-color flexographic printing machines. We hold ISO 9001:2015 and BRC/IoP Grade A "
        "certifications, ensuring the highest standards of quality and food safety compliance."
    )
    intro1.style.font.size = Pt(10)

    intro2 = doc.add_paragraph(
        "We have carefully reviewed your RFQ No. RFX-2026-001 for Corrugated Packaging Annual Contract "
        "FY2026-27 and are pleased to present this comprehensive commercial proposal. Our pricing is "
        "competitive, backed by in-house raw material sourcing from BILT, JK Paper, and Emami Paper Mills, "
        "ensuring supply chain resilience. We are confident that our combination of quality, certification, "
        "and service will meet FMCGCo's requirements."
    )
    intro2.style.font.size = Pt(10)

    # Section 2: Technical Compliance
    doc.add_heading("Section 2: Technical Compliance", level=2)
    tc_para = doc.add_paragraph(
        "We confirm that IndoPack Industries can supply 29 out of the 30 items specified in the RFQ. "
        "All items conform to IS 2771 (Corrugated Fibreboard Boxes) and IS 1397 (Corrugated Fibreboard "
        "Sheets) standards. Item 27 (Honeycomb Panel, 20mm, 1200x800mm) is outside our current product "
        "range, as we do not operate honeycomb panel production lines. We recommend sourcing Item 27 "
        "separately from a specialist honeycomb manufacturer. For all other 29 items, we confirm full "
        "technical compliance with the specifications provided, with individual test reports (Burst Factor, "
        "ECT, GSM) available on request."
    )
    tc_para.style.font.size = Pt(10)

    # Section 3: Commercial Pricing (Table)
    doc.add_heading("Section 3: Commercial Pricing", level=2)
    note_para = doc.add_paragraph(
        "The following table presents our unit prices on FOR Chennai basis. "
        "Freight charges to Pune are detailed in Section 4."
    )
    note_para.style.font.size = Pt(9)
    note_para.runs[0].font.italic = True

    tbl = doc.add_table(rows=1, cols=6)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr_row = tbl.rows[0]
    for i, h in enumerate(["Item #", "Specification", "Our Description", "Unit Price (Rs)", "MOQ", "Lead Time"]):
        cell = hdr_row.cells[i]
        cell.text = h
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)
        # Set cell background
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1F4E79")
        tcPr.append(shd)

    for item in ITEMS:
        num = item[0]
        price = ipi_prices.get(num, "N/A")
        moq = ipi_moq.get(num, "500 pcs" if num not in {6, 7, 10, 16, 19, 21, 23} else "1000 pcs")
        lt = ipi_lt.get(num, "21-25 working days")
        row_cells = tbl.add_row().cells
        row_cells[0].text = str(num)
        row_cells[1].text = f"{item[1]} | {item[3]} | {item[4]} | {item[5]}"
        row_cells[2].text = item[1]
        row_cells[3].text = price
        row_cells[4].text = str(moq)
        row_cells[5].text = str(lt)
        for cell in row_cells:
            for para in cell.paragraphs:
                para.style.font.size = Pt(8.5)
                for run in para.runs:
                    run.font.size = Pt(8.5)

    # Column widths
    col_widths_cm = [1.2, 4.5, 3.5, 4.0, 2.0, 2.8]
    for i, cw in enumerate(col_widths_cm):
        for row in tbl.rows:
            row.cells[i].width = Cm(cw)

    doc.add_paragraph()

    # Section 4: Commercial Terms
    doc.add_heading("Section 4: Commercial Terms", level=2)
    ct_text = (
        "Our pricing is on FOR Chennai basis. Freight charges to your Pune facility will be approximately "
        "Rs 2.50 per kg of finished goods for Full Truck Load (FTL) shipments, or Rs 3.80 per kg for Less "
        "Than Truckload (LTL) shipments. We recommend consolidating orders to maximize FTL benefits.\n\n"
        "Lead times for all items in this quotation are 21 to 25 working days from receipt of confirmed "
        "purchase order and advance payment receipt. For items with custom print requirements (Items 4, 6, "
        "8, 10, 11, 17, 20, 21, 24, 29), please add 5 working days for artwork approval.\n\n"
        "Volume pricing: For annual volumes exceeding 1,00,000 pieces per SKU, we can offer an additional "
        "3% discount on the quoted prices. For annual volumes between 50,000 and 99,999 pieces per SKU, "
        "the additional discount is 1.5%.\n\n"
        "GST @ 18% will be charged on all items as per applicable HSN codes. Our GST Number: 33AABCI9876D1Z5.\n\n"
        "Payment terms: 30% advance with purchase order, balance 70% against proof of dispatch. "
        "We also accept LC at sight for export orders."
    )
    ct_para = doc.add_paragraph(ct_text)
    ct_para.style.font.size = Pt(10)

    # Section 5: Questionnaire Responses
    doc.add_heading("Section 5: Questionnaire Responses", level=2)
    q_responses = [
        ("Q1 (ISO 9001:2015 Certification)",
         "Yes, IndoPack Industries is ISO 9001:2015 certified. Certificate No: IPI/ISO/2019/1234, "
         "valid till June 2027. Certificate is available for review upon request."),
        ("Q2 (BRC/IoP Certification)",
         "Yes, we hold BRC/IoP Packaging Materials Certification. Certificate No: BRC-IPI-2023-456, "
         "Grade A, valid till October 2027. We undergo annual surveillance audits."),
        ("Q3 (Full Supply Capability)",
         "IndoPack can supply 29 of the 30 items listed in the RFQ. Item 27 (Honeycomb Panels, 20mm) "
         "is not in our product range. For all other 29 items, we confirm full supply capability."),
        ("Q4 (Production Capacity)",
         "Our current installed production capacity is 1200 MT per month on a two-shift basis. "
         "We can scale to 1500 MT per month with extended shifts if required."),
        ("Q5 (In-House Printing)",
         "Yes, we have in-house flexographic printing capability up to 4 colors. We also have "
         "pre-print flexo for high-quality graphics on select items."),
        ("Q6 (Defect/Rejection Rate)",
         "Our average defective rate for the last 12 months (Oct 2025 - Sep 2026) was 0.3%. "
         "Detailed quality records and COA samples are available upon request."),
        ("Q7 (Payment Terms)",
         "Standard terms: 30% advance with purchase order, balance 70% against proof of dispatch. "
         "For export orders, LC at sight is also acceptable."),
        ("Q8 (Volume Discounts)",
         "Yes. For annual volumes exceeding 1,00,000 pieces per SKU: 3% additional discount. "
         "For annual volumes between 50,000 and 99,999 pieces per SKU: 1.5% additional discount. "
         "Volume commitments to be confirmed at the time of annual contract signing."),
        ("Q9 (Minimum Order Quantity)",
         "Standard RSC items: 500 pieces per SKU. Custom die-cut, printed, and specialty items: "
         "1000 pieces per SKU. For Item 18 (Bulk Bin): 100 pieces minimum."),
        ("Q10 (FSC Certification)",
         "Yes, IndoPack Industries holds FSC Chain-of-Custody Certification. "
         "Certificate No: FSC-C123456. We can supply FSC-certified packaging on request with "
         "appropriate documentation for chain-of-custody compliance."),
    ]
    for q_title, q_ans in q_responses:
        p = doc.add_paragraph()
        run_q = p.add_run(q_title + ": ")
        run_q.font.bold = True
        run_q.font.size = Pt(10)
        run_a = p.add_run(q_ans)
        run_a.font.size = Pt(10)
        p.paragraph_format.space_after = Pt(4)

    doc.add_paragraph()
    sign_para = doc.add_paragraph()
    sign_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sign_run = sign_para.add_run(
        "Yours faithfully,\n\nMr. Suresh Krishnamurthy\nVice President - Sales & Marketing\n"
        "IndoPack Industries Pvt. Ltd.\nTel: +91 044 2625 7890 | Mobile: +91 98400 12345\n"
        "Email: s.krishnamurthy@indopack.in"
    )
    sign_run.font.size = Pt(10)

    out_path = os.path.join(OUT_DIR, "IPI_IndoPack_Quote.docx")
    doc.save(out_path)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# 4. PCO_Premium_RateCard.jpg
# ─────────────────────────────────────────────────────────────────────────────
def create_pco_jpg():
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    pco_prices = {
        1: ("Rs 24.00/pc", ""), 2: ("Rs 38.00/pc", ""), 3: ("Rs 68.00/pc", ""),
        4: ("Rs 58.00/pc", ""), 5: ("Rs 88.00/pc", ""), 6: ("Rs 34.00/pc", ""),
        7: ("Rs 28.00/pc", ""), 8: ("Rs 22.00/pc", ""), 9: ("Rs 145.00/pc", ""),
        10: ("Rs 42.00/pc", ""), 11: ("Rs 32.00/pc", ""), 12: ("Rs 14.50/sqm", ""),
        13: ("Rs 21.00/sqm", ""), 14: ("Rs 10.50/pc", ""), 15: ("Rs 55.00/pc", ""),
        16: ("Rs 64.00/pc", ""), 17: ("Rs 65.00/pc", ""), 18: ("Rs 240.00/pc", ""),
        19: ("Rs 5.20/pc", ""), 20: ("Rs 105.00/pc", ""), 21: ("Rs 39.00/pc", ""),
        22: ("Rs 98.00/pc", ""), 23: ("Rs 4.60/pc", ""), 24: ("Rs 82.00/pc", ""),
        25: ("Rs 78.00/pc", ""), 26: ("Rs 82.00/pc", ""), 27: ("Rs 115.00/pc", ""),
        28: ("Rs 34.00/pc", "(GMP-grade board)"),
        29: ("Rs 88.00/pc", "(moisture-barrier treated)"),
        30: ("Rs 385.00/pc", ""),
    }

    W, H = 1600, 2300
    img = Image.new("RGB", (W, H), color=(252, 248, 240))  # cream background
    draw = ImageDraw.Draw(img)

    # Try to load a font; fall back gracefully
    def try_font(size, bold=False):
        import sys
        font_paths = []
        if sys.platform == "win32":
            font_paths = [
                "C:/Windows/Fonts/Arial.ttf",
                "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/Arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        for fp in font_paths:
            try:
                from PIL import ImageFont
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
        from PIL import ImageFont
        return ImageFont.load_default()

    font_title = try_font(52, bold=True)
    font_sub = try_font(28)
    font_hdr = try_font(32, bold=True)
    font_col_hdr = try_font(26, bold=True)
    font_item = try_font(22)
    font_note = try_font(19)

    # Dark green header bar
    draw.rectangle([0, 0, W, 160], fill=(0, 100, 50))
    draw.text((W//2, 45), "PremiumCorrugated (Pvt) Ltd", font=font_title,
              fill=(255, 255, 255), anchor="mm")
    draw.text((W//2, 105), "21, Bhavani Industrial Estate, Andheri East, Mumbai - 400093",
              font=font_sub, fill=(200, 240, 210), anchor="mm")
    draw.text((W//2, 135), "Tel: +91 022 6789 0123 | Email: rfq@premiumcorrugated.in | GST: 27AABCP9876F1Z8",
              font=font_note, fill=(180, 220, 190), anchor="mm")

    y = 180
    # Rate card title
    draw.text((W//2, y), "INDICATIVE RATE CARD — FY 2026-27", font=font_hdr,
              fill=(0, 80, 40), anchor="mm")
    y += 40
    draw.text((W//2, y), "RFQ Reference: RFX-2026-001  |  Buyer: FMCGCo Procurement",
              font=font_sub, fill=(80, 80, 80), anchor="mm")
    y += 20
    draw.text((W//2, y), "Date: October 20, 2026  |  Validity: 90 days from date of issue",
              font=font_sub, fill=(80, 80, 80), anchor="mm")
    y += 25
    # Separator line
    draw.line([(40, y), (W-40, y)], fill=(0, 100, 50), width=3)
    y += 15

    # Column headers
    col1_x = 60
    col2_x = 1050
    draw.rectangle([col1_x-5, y-5, W-col1_x+5, y+35], fill=(0, 100, 50))
    draw.text((col1_x + 10, y + 15), "Item Description", font=font_col_hdr,
              fill=(255, 255, 255), anchor="lm")
    draw.text((col2_x + 10, y + 15), "Rate (Rs/piece)", font=font_col_hdr,
              fill=(255, 255, 255), anchor="lm")
    y += 42

    # Items
    row_h = 42
    for i, item in enumerate(ITEMS):
        num = item[0]
        price_str, note = pco_prices.get(num, ("N/A", ""))
        bg = (245, 250, 245) if i % 2 == 0 else (252, 248, 240)
        draw.rectangle([col1_x-5, y, W-col1_x+5, y+row_h-2], fill=bg)
        # Item number badge
        draw.rectangle([col1_x-5, y, col1_x+45, y+row_h-2], fill=(0, 100, 50))
        draw.text((col1_x+20, y+row_h//2), str(num), font=font_item,
                  fill=(255, 255, 255), anchor="mm")
        # Description
        desc = item[1]
        if note:
            desc += f" {note}"
        draw.text((col1_x+60, y+row_h//2), desc, font=font_item, fill=(30, 30, 30), anchor="lm")
        # Price
        draw.text((col2_x, y+row_h//2), price_str, font=font_item, fill=(0, 80, 40), anchor="lm")
        y += row_h

    y += 10
    draw.line([(40, y), (W-40, y)], fill=(0, 100, 50), width=2)
    y += 15

    # Footnotes
    footnotes = [
        "VOLUME DISCOUNTS: 10% for >1,00,000 pcs/SKU/year  |  7% for 50,000-1,00,000 pcs/SKU/year  |  4% for 25,000-50,000 pcs/SKU/year",
        "All prices EXCLUSIVE of GST @18%. Freight: INCLUDED for Mumbai deliveries. Outstation freight at cost.",
        "Payment: 45 days credit (preferred customers)  |  30 days credit (standard)",
        "Certifications: ISO 9001:2015  |  BRC/IoP Grade AA  |  FSC-CoC  |  GMP+  |  SEDEX",
        "Quote Validity: 90 days from date of issue. For orders and inquiries, contact your dedicated account manager.",
    ]
    for fn in footnotes:
        draw.text((W//2, y+16), fn, font=font_note, fill=(40, 40, 40), anchor="mm")
        y += 34

    # ── Photo effects ──
    # 1. Rotate by 1.8 degrees
    img = img.rotate(1.8, resample=Image.BICUBIC, expand=False, fillcolor=(252, 248, 240))

    # 2. Gaussian noise ±5
    arr = np.array(img, dtype=np.int16)
    noise = np.random.randint(-5, 6, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    # 3. Lower contrast (multiply by 0.92)
    arr = np.array(img, dtype=np.float32)
    arr = arr * 0.92
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    out_path = os.path.join(OUT_DIR, "PCO_Premium_RateCard.jpg")
    img.save(out_path, "JPEG", quality=88)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# 5. RPC_RegionalPacks_Email.txt
# ─────────────────────────────────────────────────────────────────────────────
def create_rpc_txt():
    content = """\
From: Vikram Reddy <vikram@regionalpacks.in>
To: procurement@fmcgco.in
CC: accounts@regionalpacks.in
Subject: Re: RFQ RFX-2026-001 - Corrugated Packaging Annual Contract
Date: Sunday, October 20, 2026, 3:47 PM IST
Message-ID: <20261020154723.vikram@regionalpacks.in>

Dear Priya Ji,

Thank you for sharing the RFQ (RFX-2026-001) for Corrugated Packaging Annual Contract FY2026-27. We have reviewed your requirements in detail and are pleased to submit our quotation.

We can supply the following items from your list:

REGULAR SLOTTED CARTONS (3-PLY):
- Item 1 (300x200x150mm, B-flute, 120+90+120 GSM): Rs 15.50/pc
- Item 2 (400x300x250mm, B-flute): Rs 22.00/pc
- Item 3 (600x400x400mm, C-flute): Rs 36.00/pc
- Item 8 (250x200x200mm, B-flute, 1-color): Rs 14.80/pc
- Item 11 (350x250x200mm, B-flute, 2-color): Rs 21.50/pc
- Item 15 (450x350x300mm, C-flute): Rs 40.00/pc
- Item 17 (550x400x350mm, C-flute, 2-color): Rs 48.00/pc
- Item 22 (800x600x600mm, C-flute): Rs 68.00/pc
- Item 28 (300x250x250mm, pharma, 1-color): Rs 22.50/pc

For the 5-ply range (double wall):
Rs 42/pc for the 5-ply, Rs 38 for the 3-ply, rest same as last year, freight extra.

Actually let me give proper rates:
- Item 4 (350x250x300mm, 5-ply BC, 2-color): Rs 42.00/pc
- Item 5 (500x350x400mm, 5-ply BC, plain): Rs 60.00/pc
- Item 9 (700x500x500mm, 5-ply BC, plain): Rs 98.00/pc
- Item 20 (600x450x500mm, 5-ply BC, 1-color): Rs 80.00/pc
- Item 24 (450x350x400mm, 5-ply BC, 2-color): Rs 62.00/pc
- Item 29 (350x300x350mm, 5-ply BC, cold chain): Rs 65.00/pc -- standard 5-ply, not wax-treated

DIE-CUT ITEMS WE CAN SUPPLY:
- Item 6 (shelf-ready tray, 450x300x80mm, E-flute, 1-color): Rs 22.00/pc
- Item 7 (packing tray, 600x400x100mm, B-flute): Rs 20.00/pc

ITEMS WE CANNOT SUPPLY:
Items 10, 12, 13, 14, 16, 18, 19, 21, 23, 25, 26, 27, 30 -- either not in our product range or we don't have capability for 7-ply or specialized formats.

ALL PRICES: GST @ 18% extra. Freight additional from Hyderabad on actuals (approx Rs 3.20/kg to Pune for LTL).

PAYMENT: We prefer advance payment. For long-term relationships, we can extend 15-day credit after 3 successful orders.

QUESTIONNAIRE RESPONSES:
Q1 (ISO 9001): Yes, we are ISO 9001:2015 certified. Cert No: RPC/ISO/2022/0391, valid till August 2027.
Q2 (BRC): No, we do not currently hold BRC/IoP certification. We are evaluating it for future.
Q3 (Full supply): We can supply 17 of the 30 items listed. Items we cannot supply are listed above.
Q4 (Capacity): Approximately 800 MT per month production capacity.
Q5 (Printing): Yes, in-house flexographic printing up to 2 colors.
Q6 (Rejection rate): Less than 0.8% defective in last 12 months.
Q7 (Payment): Advance preferred; 15-day credit for established customers.
Q8 (Volume discounts): We can discuss annual commitment discounts on a case-by-case basis.
Q9 (MOQ): 500 pieces per SKU for standard items, 1000 pieces for custom die-cut.
Q10 (FSC): No, we do not hold FSC certification at this time.

Please feel free to call me on +91 98765 43210 if you need any clarification.

Looking forward to your favorable consideration.

With regards,
Vikram Reddy
Managing Director
RegionalPacks Co
Plot 23, Nacharam Industrial Estate
Hyderabad - 500076, Telangana
Mobile: +91 98765 43210
Email: vikram@regionalpacks.in
GST No: 36AAOFR5678G1Z2
"""
    out_path = os.path.join(OUT_DIR, "RPC_RegionalPacks_Email.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ground_truth.json
# ─────────────────────────────────────────────────────────────────────────────
def create_ground_truth():
    gt = {
        "_purpose": "Ground truth for testing extraction accuracy. This file is NOT loaded by the application runtime. Use only for validation testing.",
        "_generated": "2026-11-17",
        "suppliers": {
            "PKI": {
                "name": "PackIndia Ltd",
                "brc_certified": True,
                "iso_certified": True,
                "fsc_certified": False,
                "total_items_quoted": 28,
                "items_not_quoted": [27, 30],
                "items_on_request": [18],
                "gst_rate": 18,
                "freight": "Included for orders above INR 50000 per delivery",
                "payment_terms": "30 days credit",
                "volume_discount_pct": 2.5,
                "volume_discount_threshold": "INR 500000/month/SKU",
                "quote_validity_days": 90,
                "sample_prices": {
                    "item_1": {"price": 20.50, "unit": "per piece"},
                    "item_2": {"price": 32.00, "unit": "per piece"},
                    "item_3": {"price": 58.00, "unit": "per piece"},
                    "item_12": {"price": 12.50, "unit": "per sqm"},
                    "item_13": {"price": 18.00, "unit": "per sqm"}
                }
            },
            "EBS": {
                "name": "EcoBox Solutions",
                "brc_certified": False,
                "brc_note": "Application submitted October 2026, expected Q1 2027. NOT currently certified.",
                "iso_certified": True,
                "fsc_certified": False,
                "total_items_quoted": 30,
                "items_not_quoted": [],
                "gst_rate_claimed": 12,
                "gst_note": "EBS claims 12% GST - may be incorrect. Standard rate 18% for most corrugated boxes. Requires verification.",
                "trade_discount_pct": 8,
                "early_payment_discount_pct": 2,
                "freight": "Extra at actuals from Ahmedabad (~INR 2.80/kg FTL to Pune)",
                "payment_terms": "30 days or 15 days with 2% early payment discount",
                "quote_validity_days": 60,
                "sample_prices_list_before_discount": {
                    "item_1": {"list_price": 17.50, "net_after_8pct_discount": 16.10, "unit": "per piece"},
                    "item_2": {"list_price": 27.00, "net_after_8pct_discount": 24.84, "unit": "per piece"},
                    "item_12": {"list_price": 10.80, "unit": "per sqm"}
                }
            },
            "IPI": {
                "name": "IndoPack Industries",
                "brc_certified": True,
                "iso_certified": True,
                "fsc_certified": True,
                "total_items_quoted": 29,
                "items_not_quoted": [27],
                "item_29_note": "SUBSTITUTE proposed: 5-ply wax-treated BC-flute at INR 68/pc",
                "gst_rate": 18,
                "freight_basis": "FOR Chennai",
                "freight_to_pune_ftl": "INR 2.50 per kg",
                "freight_to_pune_ltl": "INR 3.80 per kg",
                "lead_time_days_min": 21,
                "lead_time_days_max": 25,
                "volume_discount_above_100k": 3.0,
                "volume_discount_50k_to_100k": 1.5,
                "payment_terms": "30% advance, 70% against dispatch",
                "quote_validity_days": 90
            },
            "PCO": {
                "name": "PremiumCorrugated Pvt Ltd",
                "brc_certified": True,
                "brc_grade": "AA",
                "iso_certified": True,
                "fsc_certified": True,
                "gmp_certified": True,
                "total_items_quoted": 30,
                "items_not_quoted": [],
                "gst_rate": 18,
                "freight": "Included for Mumbai. Outstation at cost.",
                "payment_terms": "45 days credit preferred, 30 days standard",
                "volume_discount_tiers": [
                    {"threshold_pieces_per_sku_per_year": 100000, "discount_pct": 10},
                    {"threshold_pieces_per_sku_per_year": 50000, "discount_pct": 7},
                    {"threshold_pieces_per_sku_per_year": 25000, "discount_pct": 4}
                ],
                "quote_validity_days": 90,
                "sample_prices": {
                    "item_1": {"price": 24.00, "unit": "per piece"},
                    "item_12": {"price": 14.50, "unit": "per sqm"}
                }
            },
            "RPC": {
                "name": "RegionalPacks Co",
                "brc_certified": False,
                "iso_certified": True,
                "fsc_certified": False,
                "total_items_quoted": 17,
                "items_quoted": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 15, 17, 20, 22, 24, 28, 29],
                "items_not_quoted": [10, 12, 13, 14, 16, 18, 19, 21, 23, 25, 26, 27, 30],
                "unresolved_pricing": "Line in email: 'rest same as last year, freight extra' - no historical baseline available to validate",
                "gst_rate": 18,
                "freight": "Extra at actuals from Hyderabad (~INR 3.20/kg LTL to Pune)",
                "payment_terms": "Advance preferred, 15 days credit after 3 successful orders",
                "item_29_note": "Standard 5-ply, NOT wax-treated - different spec from RFQ requirement"
            }
        },
        "mandatory_qualification": {
            "Q1_ISO_pass": ["PKI", "EBS", "IPI", "PCO", "RPC"],
            "Q2_BRC_pass": ["PKI", "IPI", "PCO"],
            "Q2_BRC_fail": ["EBS", "RPC"],
            "Q3_full_supply_pass": ["PKI", "EBS", "PCO"],
            "Q3_partial_supply": ["IPI", "RPC"],
            "qualified_all_mandatory": ["PKI", "IPI", "PCO"],
            "disqualified": ["EBS", "RPC"],
            "disqualification_reasons": {
                "EBS": "BRC certification not current (application pending Q1 2027)",
                "RPC": "No BRC certification"
            }
        }
    }
    out_path = os.path.join(OUT_DIR, "ground_truth.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(gt, f, indent=2, ensure_ascii=False)
    print(f"[OK] {out_path} ({os.path.getsize(out_path):,} bytes)")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nOutput directory: {OUT_DIR}\n")
    print("Creating PKI_PackIndia_Quote.xlsx ...")
    create_pki_xlsx()

    print("Creating EBS_EcoBox_Quote.pdf ...")
    create_ebs_pdf()

    print("Creating IPI_IndoPack_Quote.docx ...")
    create_ipi_docx()

    print("Creating PCO_Premium_RateCard.jpg ...")
    create_pco_jpg()

    print("Creating RPC_RegionalPacks_Email.txt ...")
    create_rpc_txt()

    print("Creating ground_truth.json ...")
    create_ground_truth()

    print("\n=== SUMMARY ===")
    files = [
        "PKI_PackIndia_Quote.xlsx",
        "EBS_EcoBox_Quote.pdf",
        "IPI_IndoPack_Quote.docx",
        "PCO_Premium_RateCard.jpg",
        "RPC_RegionalPacks_Email.txt",
        "ground_truth.json",
    ]
    all_ok = True
    for fname in files:
        fpath = os.path.join(OUT_DIR, fname)
        if os.path.exists(fpath):
            sz = os.path.getsize(fpath)
            status = "OK" if sz > 0 else "EMPTY!"
            print(f"  {status:6s} {fname:40s} {sz:>10,} bytes")
            if sz == 0:
                all_ok = False
        else:
            print(f"  MISSING {fname}")
            all_ok = False
    if all_ok:
        print("\nAll 6 files created successfully.")
    else:
        print("\nSome files are missing or empty!")
