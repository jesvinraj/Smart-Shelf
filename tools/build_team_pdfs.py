"""Build 4 team-report PDFs - one per team member - into docs/Team_Reporting/.

The SmartShelf project report is split so each of the 4 members gets a
standalone PDF explaining "their" part of the system, ending with likely
viva / Q&A cues. Files:
  Part1..Part4 (member1..member4)
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, Image, KeepTogether, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")
OUTDIR = os.path.join(ROOT, "docs", "Team_Reporting")
os.makedirs(OUTDIR, exist_ok=True)

NAVY = colors.HexColor("#0B2447")
BLUE = colors.HexColor("#0B5FA5")
TEAL = colors.HexColor("#0E8388")
GREY = colors.HexColor("#5B6472")
LINE = colors.HexColor("#C9D6E8")
HEAD_BG = colors.HexColor("#0B2447")

ss = getSampleStyleSheet()
S_TITLE = ParagraphStyle("T", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=26,
                         leading=32, textColor=NAVY, spaceAfter=6)
S_SUB = ParagraphStyle("S", parent=ss["Normal"], fontName="Helvetica", fontSize=12,
                       leading=16, textColor=BLUE, spaceAfter=14)
S_H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15,
                      leading=20, textColor=NAVY, spaceBefore=2, spaceAfter=7)
S_H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                      leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=4)
S_BODY = ParagraphStyle("B", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5,
                        leading=13.5, textColor=colors.HexColor("#222B3A"), spaceAfter=5)
S_SMALL = ParagraphStyle("M", parent=ss["Normal"], fontName="Helvetica", fontSize=8,
                         leading=11, textColor=GREY, spaceAfter=2)
S_BULL = ParagraphStyle("U", parent=S_BODY, fontSize=9.2, leading=13,
                        leftIndent=14, bulletIndent=2, spaceAfter=3)
S_CELL = ParagraphStyle("C", parent=ss["Normal"], fontName="Helvetica", fontSize=7.7,
                        leading=9.6, textColor=colors.HexColor("#222B3A"))
S_CELLB = ParagraphStyle("CB", parent=S_CELL, fontName="Helvetica-Bold", textColor=colors.white)
S_MONO = ParagraphStyle("MO", parent=S_CELL, fontName="Courier", fontSize=7.3, leading=9.4)
S_QA = ParagraphStyle("QA", parent=S_BODY, spaceBefore=2, spaceAfter=5)


def P(text, style=S_BODY):
    return Paragraph(text, style)


def bullet(text):
    return Paragraph("<bullet>\u2022</bullet>" + text, S_BULL)


def h1(t):
    return [P(t, S_H1), HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=7)]


def ep_table(rows):
    head = [P("<b>METHOD</b>", S_CELLB), P("<b>PATH</b>", S_CELLB),
            P("<b>ACCESS</b>", S_CELLB), P("<b>PURPOSE</b>", S_CELLB)]
    body = [[P(m, S_MONO), P(p, S_MONO), P(a, S_CELL), P(u, S_CELL)] for m, p, a, u in rows]
    t = Table([head] + body, colWidths=[40, 118, 62, 295], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def qa(items):
    """items: list of (question, answer)."""
    out = []
    for q, a in items:
        out.append(P("<b>Q. %s</b>" % q, S_QA))
        out.append(P("A. %s" % a))
        out.append(Spacer(1, 2 * mm))
    return out


def footer_txt(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(18 * mm, 12 * mm, doc.__dict__.get("_title", "SmartShelf - Team Report"))
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, "Page %d" % doc.page)
    canvas.restoreState()


def build_pdf(path, title, story):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=18 * mm, title=title, author="SmartShelf")
    doc.__dict__["_title"] = title
    doc.build(story, onFirstPage=footer_txt, onLaterPages=footer_txt)
    print("wrote", path)


def cover(part, role, scope, member_checklist):
    story = []
    story.append(Spacer(1, 6 * mm))
    story.append(P("SmartShelf", S_TITLE))
    story.append(P("Smart Retail Inventory & First-Expiry-First-Out (FEFO) Management System", S_SUB))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))
    story.append(P("<b>TEAM REPORT - PART %d of 4</b>   |   Team Member %d: <font color='#0B5FA5'>%s</font>"
                   % (part, part, "[Your Name]"), S_BODY))
    story.append(P("<b>Your role on the project:</b> %s" % role, S_BODY))
    story.append(P("<b>What YOU present and defend:</b> %s" % scope, S_BODY))
    story.append(Spacer(1, 4 * mm))
    box = Table([[P("<b>How to use this part</b><br/><font size='8.5'>Read your sections below until you can "
                    "walk someone through them without notes. Then practise the Q&amp;A cues at the end - "
                    "they mirror what a panel typically asks. If you do not know a detail outside your part, "
                    "say so and hand it to the right teammate.</font>", S_CELL)]],
                colWidths=[176 * mm])
    box.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, BLUE),
                             ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2FB")),
                             ("TOPPADDING", (0, 0), (-1, -1), 8),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                             ("LEFTPADDING", (0, 0), (-1, -1), 8),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    story.append(box)
    story.append(Spacer(1, 5 * mm))
    story.append(P("<b>You must be able to explain</b>", S_H2))
    for c in member_checklist:
        story.append(bullet(c))
    story.append(PageBreak())
    return story


# ============================================================================
# PART 1 - Member 1: Introduction, Problem, Big Picture & Architecture
# ============================================================================
def part1():
    story = cover(1, "Project Lead & opening presenter",
                  "The 'what and why' of SmartShelf, the problem it solves, the product idea, the "
                  "architecture, the tech stack and how to run the demo.",
                  ["The one-sentence description of the project.",
                   "The retail-shrink problem and why FEFO is the answer.",
                   "The layered architecture and each layer's job.",
                   "The technology stack and the databases supported.",
                   "How to run the app and the demo logins."])
    story += h1("1. The project in one sentence")
    story.append(P("SmartShelf is a web-based inventory management system for retail stores selling "
                   "perishable, dated products. Every unit of stock belongs to a dated batch, and the "
                   "system sells, discounts and alerts based on expiry dates compared against how fast "
                   "items sell."))
    story += h1("2. The problem it solves")
    for b in [
        "Roughly 20-30% of perishable stock is lost to expiry before it can be sold.",
        "Without FEFO, staff sell the newest stock they grab and the oldest stock rots.",
        "Discounts were gut-feel; nobody could prove which batch was sold or how much waste cost.",
    ]:
        story.append(bullet(b))
    story.append(P("The business outcome SmartShelf targets: <b>sell the oldest stock first automatically, "
                   "quantify spoilage risk, and approve discounts deliberately</b> - so waste falls and "
                   "margin holds."))
    story += h1("3. Solution overview and capabilities")
    for b in [
        "Real-time batch-level stock with cost, value, expiry and location.",
        "Automatic FEFO picking at every sale (never a manual first-out decision).",
        "Risk-scored batches and recommended discount percent with a clear reason.",
        "30-day expiry alerts, low-stock and high-risk notifications.",
        "Role-based access for Admin, Manager, Biller, Cashier, Staff and User.",
        "Full audit trail: every sale, promotion, adjustment and waste event is logged.",
    ]:
        story.append(bullet(b))
    story += h1("4. The product lifecycle")
    story.append(P("5 stages: <b>Receive</b> (purchase receipts create dated batches), <b>Store</b> "
                   "(locations, value, alerts), <b>Monitor</b> (expiry + risk scoring), <b>Sell</b> "
                   "(FEFO-first checkout), <b>Analyze</b> (velocity, waste, margin) - then the cycle "
                   "repeats with better data."))
    story += h1("5. Reference architecture")
    arch = Image(os.path.join(ASSETS, "architecture.png"))
    arch.drawWidth = 515
    arch.drawHeight = 515 * 1500 / 2500
    story.append(arch)
    story.append(P("Figure: layered architecture (client -> API -> services/engines -> data) plus the "
                   "8-step end-to-end working flow.", S_SMALL))
    story += h1("6. Technology stack")
    stack = Table([
        [P("<b>Layer</b>", S_CELLB), P("<b>Technology</b>", S_CELLB), P("<b>Why</b>", S_CELLB)],
        [P("Backend", S_CELL), P("Python 3 + Flask + SQLAlchemy", S_CELL),
         P("Lightweight blueprints, clean REST JSON API", S_CELL)],
        [P("Frontend", S_CELL), P("HTML/CSS/JS + Chart.js", S_CELL),
         P("Server-rendered pages, live dashboard charts", S_CELL)],
        [P("Database", S_CELL), P("SQLite (dev) / MySQL / PostgreSQL (prod)", S_CELL),
         P("DATABASE_URL switch, ORM everywhere", S_CELL)],
        [P("Security", S_CELL), P("Flask-Login, bcrypt, itsdangerous", S_CELL),
         P("Sessions, TOTP 2FA, signed reset tokens", S_CELL)],
        [P("Deploy", S_CELL), P("Docker + gunicorn + nginx TLS", S_CELL),
         P("One-command compose, healthchecks", S_CELL)],
    ], colWidths=[22 * mm, 74 * mm, 80 * mm])
    stack.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                                [colors.white, colors.HexColor("#EFF4FA")]),
                               ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("TOPPADDING", (0, 0), (-1, -1), 4),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(stack)
    story += h1("7. How to run the demo")
    for b in [
        ".venv\\Scripts\\python.exe -m flask --app app init-db  (create schema)",
        ".venv\\Scripts\\python.exe -m flask --app app seed  (demo data)",
        ".venv\\Scripts\\python.exe -m flask --app app run  (http://localhost:5000)",
        "Demo logins:  admin/admin123   manager/manager123   cashier/cashier123",
    ]:
        story.append(P("<bullet>\u2022</bullet><font face='Courier' size='8.5'>%s</font>" % b, S_BULL))
    story += h1("8. Likely questions and answer cues")
    story += qa([
        ("Describe the project in one sentence.",
         "A retail inventory system that dates every batch and uses FEFO so the store sells the oldest "
         "stock first, scores spoilage risk and approves discounts before loss."),
        ("Who is the user, and what is the main pain point?",
         "A store owner/manager losing money to expired stock. They need to know what is about to expire, "
         "sell it first and discount it deliberately."),
        ("Walk me through the architecture.",
         "Browser pages call a Flask REST API. Routes delegate to service/engine modules that do FEFO, risk "
         "and pricing math, then ORM writes to SQLite/MySQL/PostgreSQL. Sessions use Flask-Login, mutations "
         "are audited."),
        ("Why is FEFO better than FIFO for perishables?",
         "FIFO orders by arrival; FEFO orders by expiry date. A newer batch can expire sooner, so expiry "
         "priority is the only safe rule for food."),
        ("Which databases do you support and how do you switch?",
         "SQLite for development, MySQL and PostgreSQL for production, selected through the DATABASE_URL "
         "environment variable - the ORM hides the difference."),
        ("How do I verify the app works?",
         "Log in with admin/admin123, receive stock into a batch, sell and watch the FEFO pick, open "
         "Pricing and Analytics; the whole journey is covered by automated tests too."),
    ])
    return story


# ============================================================================
# PART 2 - Member 2: Core Engine - FEFO, Batches, Inventory, Sales
# ============================================================================
def part2():
    story = cover(2, "Core engine owner",
                  "FEFO picking, stock batches, purchase receiving, inventory ledger and the sales flow - "
                  "including how we guarantee no overselling.",
                  ["What FEFO is and how it is implemented per sale.",
                   "Why the stock update must be atomic (concurrency).",
                   "What a batch is and how expiry classification works.",
                   "The purchase/PO receiving flow into batches.",
                   "The movement ledger types (IN/OUT/ADJUST/TRANSFER/WASTAGE).",
                   "How a sale keeps batch-accurate traceability."])
    story += h1("1. FEFO - the core idea")
    story.append(P("First-Expired-First-Out: when stock is taken, always take from the batch that expires "
                   "first. SmartShelf sorts live batches by expiry date ascending, skips expired ones "
                   "(they go to waste), allocates from the oldest, and tops up from the next when a batch "
                   "runs out."))
    story += h1("2. How a sale deducts stock (implementation)")
    for b in [
        "POST /api/sales receives items and payment details.",
        "For each product the engine walks its batches earliest-expiry first.",
        "Each deduction is one guarded atomic statement: UPDATE stock_batches SET quantity = quantity - n "
        "WHERE id = ? AND quantity >= n.",
        "If the UPDATE changes zero rows the batch is empty - the whole sale rolls back and returns 400.",
        "Sales and PostgreSQL additionally lock rows (SELECT ... FOR UPDATE) during allocation.",
    ]:
        story.append(bullet(b))
    story += h1("3. Concurrency: the no-oversell guarantee")
    story.append(P("Two cashiers could read quantity=1 and both sell the last unit. The guarded UPDATE "
                   "makes that impossible: only one transaction changes the row, the other matches zero "
                   "rows and is refused."))
    story.append(P("<b>Proof test</b> - tests/test_concurrency.py fires 20 parallel 1-unit sales: all 20 "
                   "succeed, stock ends at 0 (never negative), 20 OUT movements are written, and an "
                   "oversized sale is cleanly refused."))
    story += h1("4. Batches and expiry classification")
    for b in [
        "A batch is one lot: product + batch code + quantity, cost price, expiry date, supplier.",
        "Expiry scan labels each batch OK / EXPIRING_SOON / EXPIRED within a 30-day window.",
        "Zeroed batches leave sellable stock but their history stays in the ledger.",
    ]:
        story.append(bullet(b))
    story += h1("5. Purchase orders and receiving (stock in)")
    for b in [
        "A manager creates a PO with line items (product, qty, unit cost, batch code, expiry).",
        "Receiving calls add_stock: create or top up the batch, raise product stock, append an IN movement.",
        "Partial receipts are tracked (received_quantity); a full receipt marks the PO RECEIVED.",
    ]:
        story.append(bullet(b))
    story += h1("6. Inventory control and the movement ledger")
    story.append(P("Locations model the shop floor; transfers move stock between them; adjustments fix "
                   "counts after stocktakes. Every change writes a ledger line of type "
                   "IN / OUT / ADJUST / TRANSFER / WASTAGE - the immutable audit trail of every unit."))
    story += h1("7. Sales flow and traceability")
    for b in [
        "Each sale line becomes one SaleItem per allocated batch - the invoice shows exactly which "
        "expiry-dated batch was sold.",
        "Totals: subtotal - discount + tax = total; a Payment row records the method.",
        "An invoice number (INV-XXXX) is generated and the sale is audited in one commit.",
    ]:
        story.append(bullet(b))
    story += h1("8. Endpoints you should be able to quote")
    story.append(KeepTogether([ep_table([
        ("POST", "/api/sales", "STAFF+", "Record sale with FEFO deduction + payment"),
        ("POST", "/api/purchases/<po_id>/receive", "MANAGER+", "Turn ordered lines into batches"),
        ("POST", "/api/inventory/receive", "MANAGER+", "Direct stock receipt"),
        ("POST", "/api/inventory/adjust", "MANAGER+", "Correct a physical count"),
        ("GET", "/api/batches", "Any user", "All batches with expiry"),
        ("GET", "/api/fefo", "Any user", "FEFO pick order per product"),
        ("GET", "/api/inventory/movements", "Any user", "Movement ledger"),
    ]), Spacer(1, 3 * mm)]))
    story += h1("9. Likely questions and answer cues")
    story += qa([
        ("What does FEFO mean and where do you apply it?",
         "First-Expired-First-Out - sell the earliest-expiring batch first. Applied at every sale and "
         "transfer; expired batches are excluded to waste."),
        ("How does the engine choose batches?",
         "It sorts live batches by expiry date ascending, then allocates the requested quantity from the "
         "oldest batch, topping up from the next whenever one is exhausted."),
        ("What happens if there is not enough stock?",
         "The guarded UPDATE matches fewer rows than needed; the route rolls back the entire sale and "
         "returns a 400 error - there is never a partial or negative deduction."),
        ("How do you prevent two cashiers overselling the last unit?",
         "A single atomic UPDATE .. WHERE quantity >= n. Only one concurrent transaction wins each row; the "
         "other sees zero rows and is refused."),
        ("What is a 'batch' exactly?",
         "One dated lot of one product, identified by product + batch code, with quantity, landed cost, "
         "expiry date and the supplier who sent it."),
        ("What movement types exist?",
         "IN (received), OUT (sold), ADJUST (stocktake correction), TRANSFER (between locations), WASTAGE "
         "(written off) - all recorded in inventory_movements."),
        ("How is traceability guaranteed on an invoice?",
         "Each SaleItem stores batch_id and quantity, so any invoice line can be reconciled to the actual "
         "expiry-dated unit sold."),
        ("How do purchase orders turn into stock?",
         "The PO lists expected lines; receiving walks them, calling add_stock per line to create/top up "
         "the batch and write an IN movement; a fully received PO becomes RECEIVED."),
    ])
    return story


# ============================================================================
# PART 3 - Member 3: Intelligence - Risk, Pricing, Analytics, Alerts, Waste
# ============================================================================
def part3():
    story = cover(3, "Intelligence & analytics owner",
                  "Spoilage risk scoring, dynamic pricing advice, the promotion approval flow, analytics "
                  "and forecasting, alerts/notifications and waste recovery.",
                  ["How the 0-100 risk score is computed (inputs, levels).",
                   "How risk maps to a recommended discount percent.",
                   "The promotion lifecycle and who approves what.",
                   "The dashboard KPIs, velocity, demand and forecast.",
                   "How alerts and the unread badge work.",
                   "What waste recording measures (loss vs recovery)."])
    story += h1("1. Spoilage risk engine")
    for b in [
        "Every live batch is scored 0-100 from: days to expiry, product types, sales velocity (units/day "
        "over 30 days) and stock on hand.",
        "Levels: LOW (0-20), MEDIUM (21-45), HIGH (46-70), CRITICAL (71-100); CRITICAL means imminent loss.",
        "The same score feeds pricing, the dashboard's risk distribution and the top-risk list.",
        "Read it via GET /api/ai/risk (all batches, sorted) or /api/ai/risk/<batch_id> (one batch).",
    ]:
        story.append(bullet(b))
    story += h1("2. Dynamic pricing advice")
    story.append(P("The pricing engine converts a risk score into a recommended discount percent "
                   "(LOW 0-10%, MEDIUM 10-20%, HIGH 20-40%, CRITICAL 40-60%) and explains it in plain "
                   "language - e.g. 'expires in 5 days'. GET /api/ai/pricing lists every at-risk batch "
                   "with unit price, the recommended percent, the discounted price and the reason."))
    story += h1("3. Promotion approval workflow")
    for b in [
        "Manager creates a promotion as DRAFT (discount type PERCENTAGE/FIXED, value, optional product, "
        "category or minimum quantity).",
        "Manager clicks SUBMIT -> PENDING_APPROVAL.",
        "Only ADMIN can APPROVE (to ACTIVE) or REJECT.",
        "Manager can later toggle ACTIVE/INACTIVE; the state machine is enforced at the API level.",
        "The system advises, the manager proposes, the admin disposes - a deliberate control step.",
    ]:
        story.append(bullet(b))
    story += h1("4. Analytics and forecasting")
    for b in [
        "Dashboard KPIs: product/stock/batch counts, inventory value, revenue, sales count, waste value, "
        "at-risk items, expiring/expired counts.",
        "Also shown: expiry summary, risk distribution (LOW/MEDIUM/HIGH/CRITICAL), daily sales trend, "
        "top-10 risk list and low-stock list.",
        "Velocity classifies products by 30-day sales rate; demand-analysis returns per-product units/day.",
        "Forecast projects the next N days (default 7) from ~60 days of history with a simple model.",
    ]:
        story.append(bullet(b))
    story += h1("5. Alerts and notifications")
    for b in [
        "Expiry scan classifies batches (OK / EXPIRING_SOON / EXPIRED) within a 30-day window.",
        "Three generators: low stock (qty <= reorder level), expiry, and high risk.",
        "Notifications are per-user; unread-count drives the navbar badge; read-all clears them.",
    ]:
        story.append(bullet(b))
    story += h1("6. Waste and revenue recovery")
    for b in [
        "Staff record spoilage/damage: product, quantity, reason (EXPIRED/DAMAGED/SPOILED/OTHER), optional "
        "batch/location.",
        "The engine deducts the exact batch and stores unit cost, potential loss and a recovery estimate.",
        "Summary aggregates losses and recovery by reason and period.",
    ]:
        story.append(bullet(b))
    story += h1("7. Endpoints you should be able to quote")
    story.append(KeepTogether([ep_table([
        ("GET", "/api/ai/risk", "Any user", "Risk score for every live batch"),
        ("GET", "/api/ai/risk/<batch_id>", "Any user", "Single batch score"),
        ("GET", "/api/ai/pricing", "Any user", "Recommended discounts + reasons"),
        ("POST", "/api/promotions/<pid>/submit", "MANAGER+", "Submit for approval"),
        ("POST", "/api/promotions/<pid>/approve", "ADMIN", "Approve -> ACTIVE"),
        ("GET", "/api/dashboard", "Any user", "KPI suite + trends + risk"),
        ("POST", "/api/alerts/generate", "MANAGER+", "Low stock / expiry / high risk"),
        ("POST", "/api/wastage", "STAFF+", "Record loss + recovery"),
    ]), Spacer(1, 3 * mm)]))
    story += h1("8. Likely questions and answer cues")
    story += qa([
        ("How is the 0-100 risk score computed?",
         "From batch-specific inputs - days to expiry, product perishability, sales velocity over 30 days "
         "and stock on hand - blended into one score with levels LOW/MEDIUM/HIGH/CRITICAL."),
        ("What does CRITICAL mean and what happens then?",
         "71-100: expiry within days. The app flags the batch, suggests a strong discount (40-60%) and "
         "surfaces it in the risk list and dashboard."),
        ("Why does a discount need approval?",
         "Discounting is a business decision, not a math one. Managers propose (DRAFT -> SUBMIT) and "
         "admins approve/reject so money is never auto-discounted without a human."),
        ("How does the forecast work?",
         "It builds a per-product demand trend from roughly 60 days of sales and projects the next N days; "
         "the model is deliberately simple and honest."),
        ("What KPIs are on the dashboard?",
         "Stock units and value, batch count, revenue and sales count, waste value, at-risk items, "
         "expiring/expired counts plus a daily sales trend and low-stock list."),
        ("How do alerts get to staff?",
         "Scans/generators write per-user notifications; the navbar unread badge shows the count and each "
         "notification can be marked read."),
        ("What does waste recording measure?",
         "Quantity, reason, unit cost and potential loss, plus an estimated recovered revenue/savings so "
         "the business sees the true cost of expiry."),
    ])
    return story


# ============================================================================
# PART 4 - Member 4: Security, Data, Testing, Deployment
# ============================================================================
def part4():
    story = cover(4, "Engineering, security & deployment owner",
                  "Authentication and security controls, the role-based access model, the data model, the "
                  "test strategy, CI and the Docker deployment - plus the roadmap and growth opportunities.",
                  ["How passwords, sessions, 2FA, lockout and resets work.",
                   "The RBAC model and the @at_least rule.",
                   "The database schema and the enums that drive the rules.",
                   "The four test suites and what each proves.",
                   "The CI pipeline and the Docker/TLS deployment.",
                   "Design decisions, growth opportunities and the roadmap."])
    story += h1("1. Authentication & security controls")
    for b in [
        "Passwords stored with bcrypt (adaptive, salted) - never plain text.",
        "TOTP two-factor authentication (GET /api/2fa/setup, enable/disable).",
        "Account lockout after 5 failed logins (15 minutes).",
        "IP rate limiting on login (10 attempts / 5 minutes).",
        "Strong session protection: sessions re-validated against IP and user-agent.",
        "Signed, single-use password-reset tokens (30-minute expiry).",
        "Full login history and an immutable audit log for every mutation.",
    ]:
        story.append(bullet(b))
    story += h1("2. Role-based access control")
    story.append(P("Roles are ordered USER < STAFF < CASHIER < BILLER < MANAGER < ADMIN. Endpoints declare "
                   "@at_least(Role.X) and grant anything at or above that rank. Only ADMIN can approve "
                   "promotions or delete users; only MANAGER+ can touch master data, POs and stock "
                   "adjustments."))
    story += h1("3. Data model at a glance")
    dm = Table([
        [P("<b>Domain</b>", S_CELLB), P("<b>Tables / values</b>", S_CELLB)],
        [P("Identity", S_CELL), P("users, login_logs (roles, bcrypt hash, 2FA secret)", S_CELL)],
        [P("Master data", S_CELL), P("categories, brands, products, suppliers", S_CELL)],
        [P("Stock", S_CELL), P("stock_batches, locations, location_transfers, inventory_movements", S_CELL)],
        [P("Commerce", S_CELL), P("purchase_orders(+items), customers, sales, sale_items, payments", S_CELL)],
        [P("Pricing", S_CELL), P("promotions (status lifecycle, discount type/value)", S_CELL)],
        [P("Ops", S_CELL), P("notifications, audit_logs, wastage", S_CELL)],
        [P("Enums", S_CELL), P("Role, PurchaseStatus, SaleStatus, PaymentMethod, MovementType, DiscountType, "
                               "WastageReason, NotificationType, ExpiryStatus, PromoStatus", S_CELL)],
    ], colWidths=[30 * mm, 146 * mm])
    dm.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                             [colors.white, colors.HexColor("#EFF4FA")]),
                            ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(dm)
    story += h1("4. Test strategy (4 suites, all green)")
    t = Table([
        [P("<b>Suite</b>", S_CELLB), P("<b>Proves</b>", S_CELLB)],
        [P("test_engines.py", S_CELL), P("FEFO order, cross-batch allocation, risk thresholds, pricing advice", S_CELL)],
        [P("test_security.py", S_CELL), P("lockout, rate limiting, password policy, 2FA, reset tokens, session protection", S_CELL)],
        [P("test_smoke.py", S_CELL), P("login, dashboard, receive, FEFO sale, alerts, reports, all pages", S_CELL)],
        [P("test_concurrency.py", S_CELL), P("20 parallel sales -> no oversell, exact stock end state", S_CELL)],
    ], colWidths=[42 * mm, 134 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                            [colors.white, colors.HexColor("#EFF4FA")]),
                           ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)
    story.append(P("Combined coverage is about 72%; the CI workflow enforces a 50% floor and runs the whole "
                   "matrix on Python 3.11 and 3.12."))
    story += h1("5. Deployment (Docker, one command)")
    for b in [
        "docker compose up starts MySQL 8.4 (healthchecked), the Flask app on gunicorn :8000 and an nginx "
        "TLS proxy (:80 -> :443).",
        "The entrypoint waits for the DB, runs init-db, optionally seeds demo data, then launches gunicorn.",
        "Self-signed certificates are generated for demos; production mounts a real cert volume.",
        "Scaling: move to managed MySQL/PostgreSQL and more gunicorn workers behind the proxy; the schema "
        "and API are already database-agnostic.",
    ]:
        story.append(bullet(b))
    story += h1("6. Design decisions, growth path, roadmap")
    story.append(P("<b>Decisions:</b> FEFO with an atomic guard is the load-bearing invariant; engines are "
                   "rule-based and auditable; discounts require human approval; every invoice line is batch-"
                   "accurate; new accounts are inactive until an admin verifies them."))
    story.append(P("<b>Growth path:</b> engines stay transparent and easy to audit - ML forecasting drops in "
                   "later; notifications are lightweight polling today, push/websocket delivery later; dev "
                   "runs on zero-setup SQLite and production scales to managed MySQL/PostgreSQL behind the "
                   "TLS proxy."))
    story.append(P("<b>Roadmap:</b> receipt/invoice PDF printing, auto reorder drafts, server-side chart "
                   "rendering for reports, barcode scanning at the POS, and a mobile manager view."))
    story += h1("7. Likely questions and answer cues")
    story += qa([
        ("How do you store passwords?",
         "bcrypt with an adaptive cost and a per-user salt - never plain text or a reversible encoding."),
        ("How does 2FA work here?",
         "The user requests /api/2fa/setup to get a TOTP secret, scans it into an authenticator app, then "
         "enables 2FA; logins then require the six-digit code."),
        ("How do you stop brute-force login attacks?",
         "Account lockout after 5 failed attempts (15 minutes) plus IP rate limiting of 10 attempts per 5 "
         "minutes; both are covered by automated tests."),
        ("What is the concurrency guarantee and how is it tested?",
         "Stock is deducted with one guarded atomic UPDATE (WHERE quantity >= n). The concurrency suite "
         "fires 20 parallel sales against one unit and proves stock never goes negative."),
        ("How would you deploy this for real?",
         "docker compose up: MySQL + gunicorn + nginx TLS. For scale, managed databases and more workers; "
         "the ORM abstracts the DB choice."),
        ("Which endpoint protects the API from anonymous calls?",
         "Flask-Login protects every route; API callers without a session get 401 JSON, page visitors are "
         "redirected to /login?next=..."),
        ("How do you ensure data integrity?",
         "One commit per transaction, guarded updates, foreign keys via the ORM, and an audit log written "
         "on every mutation."),
        ("What would you improve next?",
         "Real chart exports, reorder automation, barcode support and multi-store / managed-DB scale - all "
         "already flagged on the roadmap."),
    ])
    return story


def main():
    build_pdf(os.path.join(OUTDIR, "SmartShelf_Report_Part1_Introduction_and_Architecture.pdf"),
              "SmartShelf - Team Report Part 1 (Member 1)", part1())
    build_pdf(os.path.join(OUTDIR, "SmartShelf_Report_Part2_Core_Engine_FEFO_and_Sales.pdf"),
              "SmartShelf - Team Report Part 2 (Member 2)", part2())
    build_pdf(os.path.join(OUTDIR, "SmartShelf_Report_Part3_Intelligence_Analytics.pdf"),
              "SmartShelf - Team Report Part 3 (Member 3)", part3())
    build_pdf(os.path.join(OUTDIR, "SmartShelf_Report_Part4_Security_Quality_Deployment.pdf"),
              "SmartShelf - Team Report Part 4 (Member 4)", part4())


if __name__ == "__main__":
    main()