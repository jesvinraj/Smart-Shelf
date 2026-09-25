"""Build the SmartShelf project explanation + working-flow PDF.

Output: docs/SmartShelf_Project_Explanation_and_Working_Flow.pdf
Reference images: docs/assets/architecture.png, screenshot_login.png, screenshot_register.png
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "docs", "assets")
OUT = os.path.join(ROOT, "docs", "SmartShelf_Project_Explanation_and_Working_Flow.pdf")

NAVY = colors.HexColor("#0B2447")
BLUE = colors.HexColor("#0B5FA5")
TEAL = colors.HexColor("#0E8388")
GREY = colors.HexColor("#5B6472")
LIGHT_LINE = colors.HexColor("#C9D6E8")
HEAD_BG = colors.HexColor("#0B2447")
GREEN = colors.HexColor("#0E8388")

ss = getSampleStyleSheet()

S_TITLE = ParagraphStyle("TITLE", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=30,
                         leading=36, textColor=NAVY, alignment=TA_LEFT, spaceAfter=6)
S_SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica", fontSize=13,
                       leading=18, textColor=BLUE, spaceAfter=18)
S_H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17,
                      leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=8)
S_H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
                      leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=5)
S_H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=10.5,
                      leading=14, textColor=TEAL, spaceBefore=6, spaceAfter=4)
S_BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5,
                        leading=13.5, textColor=colors.HexColor("#222B3A"), alignment=TA_LEFT, spaceAfter=5)
S_SMALL = ParagraphStyle("SMALL", parent=ss["Normal"], fontName="Helvetica", fontSize=8,
                         leading=11, textColor=GREY, spaceAfter=2)
S_CELL = ParagraphStyle("CELL", parent=ss["Normal"], fontName="Helvetica", fontSize=7.7,
                        leading=9.6, textColor=colors.HexColor("#222B3A"))
S_CELL_B = ParagraphStyle("CELLB", parent=S_CELL, fontName="Helvetica-Bold", textColor=colors.white)
S_MONO = ParagraphStyle("MONO", parent=S_CELL, fontName="Courier", fontSize=7.3, leading=9.4)
S_BULLET = ParagraphStyle("BULL", parent=S_BODY, fontSize=9.2, leading=13, leftIndent=14,
                          bulletIndent=2, spaceAfter=3)


def P(text, style=S_BODY):
    return Paragraph(text, style)


def bullet(text):
    return Paragraph("<bullet>\u2022</bullet>" + text, S_BULLET)


def _page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(18 * mm, 12 * mm, "SmartShelf - Project Explanation & Working Flow")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, "Page %d" % doc.page)
    canvas.restoreState()


def h1(t):
    return [P(t, S_H1), HRFlowable(width="100%", thickness=1.1, color=NAVY, spaceAfter=8)]


def ep_table(rows):
    head = [P("<b>METHOD</b>", S_CELL_B), P("<b>PATH</b>", S_CELL_B),
            P("<b>ACCESS</b>", S_CELL_B), P("<b>PURPOSE</b>", S_CELL_B)]
    body = []
    for meth, path, acc, purpose in rows:
        body.append([P(meth, S_MONO), P(path, S_MONO), P(acc, S_CELL), P(purpose, S_CELL)])
    data = [head] + body
    t = Table(data, colWidths=[40, 118, 66, 291], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
        ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


story = []

# ============ PAGE 1 : COVER ============
story.append(Spacer(1, 8 * mm))
story.append(P("SmartShelf", S_TITLE))
story.append(P("Smart Retail Inventory & First-Expiry-First-Out (FEFO) Management System", S_SUB))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=14))
story.append(P("<b>Document title:</b> Full Project Explanation & Working Flow - Module-by-Module Reference"))
story.append(P("<b>Version:</b> 1.0 &nbsp;|&nbsp; <b>Date:</b> September 2026 &nbsp;|&nbsp; <b>Stack:</b> Python Flask + SQLAlchemy"))
story.append(P("<b>Scope:</b> architecture overview, request lifecycle, every module's purpose, endpoints and "
               "working process, role-based access, data model, business workflows, tests and deployment."))
story.append(Spacer(1, 6 * mm))

cover_facts = Table([
    [P("<b>Core value</b>", S_CELL), P("Stop losing money to expired stock. Systematically sell or discount "
       "soon-to-expire goods before they become waste.", S_CELL)],
    [P("<b>Signature engine</b>", S_CELL), P("FEFO picking - every sale deducts from the earliest-expiring "
       "batch first, guarded by an atomic UPDATE so parallel cashiers can never oversell.", S_CELL)],
    [P("<b>Role model</b>", S_CELL), P("ADMIN / MANAGER / BILLER / CASHIER / STAFF / USER with @at_least() enforcement and a "
       "promotion approval chain (Manager submits -> Admin approves).", S_CELL)],
    [P("<b>Demo logins</b>", S_CELL), P("admin / admin123  \u00b7  manager / manager123  \u00b7  cashier / cashier123", S_CELL)],
], colWidths=[28 * mm, 148 * mm])
cover_facts.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, BLUE),
    ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
    ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EAF2FB")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F9FD")]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(cover_facts)
story.append(Spacer(1, 8 * mm))
story.append(P("<b>What is inside this document</b>", S_H3))
for item in [
    "Section 1  - Project overview, goals and capabilities.",
    "Section 2  - How the system is assembled (app factory, request lifecycle, security).",
    "Section 3  - Reference images: architecture & working-flow diagram + live UI screenshots.",
    "Section 4  - Every module, one by one: purpose, working process, endpoints, data written.",
    "Section 5  - Role & permission matrix.",
    "Section 6  - Data model at a glance (tables you can query).",
    "Section 7  - Golden-path business workflows walked end to end.",
    "Section 8  - Quality: test suites, coverage, CI and Docker deployment.",
    "Section 9  - Running, testing and deploying (commands).",
    "Section 10 - Design decisions and the roadmap.",
]:
    story.append(bullet(item))
story.append(PageBreak())

# ============ 1. PROJECT OVERVIEW ============
story += h1("1. Project Overview")
story.append(P("SmartShelf is a web-based inventory management system built for retail stores that sell "
               "perishable, dated goods. Its central idea: <b>every unit of stock belongs to a dated batch, "
               "and every system decision - which batch to pick, how aggressively to price it, whether to "
               "alert, how much was saved - follows from comparing expiry dates against how fast items sell.</b>"))
story.append(P("<b>Business goals it solves</b>", S_H3))
for b in [
    "Eliminate overselling and negative stock with atomic, guarded stock deductions.",
    "Reduce expiry waste by always selling the oldest stock first (FEFO).",
    "Quantify spoilage risk per batch and turn risk into a recommended discount with a plain-language reason.",
    "Force a human approval chain so discounts are deliberate, not automatic.",
    "Give staff a real-time dashboard, alerts and reports instead of spreadsheet archaeology.",
]:
    story.append(bullet(b))
story.append(P("<b>Capabilities</b>", S_H3))
story.append(bullet("Authentication & security: bcrypt, 2FA (TOTP), rate limiting/lockout, session protection, "
                    "login history, audit trail, six role levels."))
story.append(bullet("Master data: categories, brands, products (SKU, price, reorder level), suppliers, customers."))
story.append(bullet("Inventory: purchase orders, receiving, stock batches with expiry, locations, transfers, "
                    "adjustments and a full movement ledger."))
story.append(bullet("Sales: FEFO-first checkout with exact-batch traceability, payments and invoice numbers."))
story.append(bullet("Intelligence: spoilage risk 0-100, dynamic pricing advice, sales velocity, demand analysis, "
                    "7-day forecast."))
story.append(bullet("Operations: expiry scans, low-stock / high-risk / expired alerts, notifications with an "
                    "unread badge, waste and recovery tracking."))
story.append(bullet("Management: dashboard KPIs, named reports (sales, inventory, expiry, discounts, waste, "
                    "performance, audit), health endpoint."))
story.append(PageBreak())

# ============ 2. HOW THE SYSTEM IS ASSEMBLED ============
story += h1("2. How the System Is Assembled")
story.append(P("<b>Application factory (app.py)</b>", S_H3))
story.append(P("Flask is created through create_app(): the SQLAlchemy db object and Flask-Login login_manager are "
               "initialised, migrations are wired with Flask-Migrate, login_view points at the HTML pages.login "
               "page, and strong session protection is enabled (sessions are re-validated against IP and "
               "user-agent). The user_loader and every model are imported so metadata is complete, then all 12 "
               "action blueprints plus the pages blueprint are registered and the CLI commands (init-db, seed, "
               "create-admin) are attached."))
story.append(P("<b>Unauthenticated behaviour</b>", S_H3))
story.append(bullet("Page requests (non-/api) are redirected to /login?next=<path> and return to that page after login."))
story.append(bullet("API requests under /api receive a clean <font face='Courier'>401 {'error': 'Authentication required'}</font> JSON - "
                    "no accidental HTML 405s."))
story.append(P("<b>Request lifecycle (one click on a page)</b>", S_H3))
for b in [
    "Browser loads a Jinja page (e.g. /sales or /analytics); the pages blueprint renders the shell.",
    "The page's JavaScript calls the matching JSON API (e.g. GET /api/sales, GET /api/dashboard).",
    "The route runs through Flask-Login; if a role is required, @at_least(Role.X) compares the current user's role.",
    "The route calls a service-layer function (stock_service, risk_engine, pricing_engine, ...) - never raw queries in routes for business logic.",
    "Services read/write rows through SQLAlchemy ORM models; a single commit makes each transaction atomic.",
    "Mutations also write an AuditLog row; the JSON response returns to the page and updates the UI.",
]:
    story.append(bullet(b))
story.append(PageBreak())

# ============ 3. REFERENCE IMAGES ============
story += h1("3. Reference Images")
story.append(P("<b>Figure 1 - Reference architecture & end-to-end working flow</b>", S_H3))
arch = Image(os.path.join(ASSETS, "architecture.png"))
arch.drawWidth = 515
arch.drawHeight = 515 * 1500 / 2500
story.append(arch)
story.append(P("Figure 1 is split in two: the left panel is the layered architecture (client, API, services, data, "
               "plus security and engines); the right panel walks the business from login to reporting in eight steps.",
               S_SMALL))
story.append(Spacer(1, 3 * mm))
story.append(P("<b>Figures 2 & 3 - Live application screenshots (login & register pages)</b>", S_H3))
shot_row = Table([
    [Image(os.path.join(ASSETS, "screenshot_login.png"), width=250, height=250 * 900 / 1440),
     Image(os.path.join(ASSETS, "screenshot_register.png"), width=250, height=250 * 900 / 1440)],
], colWidths=[255, 260])
shot_row.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
story.append(shot_row)
story.append(P("Login page (left) requires credentials shown to each role; register (right) self-services an "
               "account before an admin raises its role.", S_SMALL))
story.append(PageBreak())

# ============ 4. MODULES ============
story.append(P("4. Module-by-Module Working Process", S_H1))
story.append(P("This section is the core of the document. For each module you get: a purpose, the exact working "
               "process, every API endpoint with required access, and the data written or touched.", S_BODY))
story.append(PageBreak())

MODULES = [
    ("4.1", "Authentication & Security (identity lifecycle)",
     "Owns the complete identity flow: register, login, session, logout, password change, password reset, "
     "TOTP two-factor authentication, user administration and login-history auditing.",
     [
        "A user registers (POST /api/register) and receives a bcrypt-hashed password and default role.",
        "Login validates credentials, applies rate limiting and lockout after repeated failures, verifies the "
        "TOTP code when 2FA is enabled, opens a Flask-Login session bound to IP + user-agent, and appends a "
        "login-history row.",
        "Every protected route requires the session; API callers without one get 401 JSON, page users are sent "
        "to /login?next=...",
        "@at_least(Role.X) enforces the minimum role before any privileged mutation.",
        "MANAGER+ can create and edit users (including roles); only ADMIN can delete a user.",
        "Users can enable/disable TOTP 2FA themselves via the setup/enable/disable endpoints.",
        "forgot-password issues a reset token; reset-password applies it."
     ],
     [
        ("POST", "/api/login", "Public", "Authenticate and open session"),
        ("POST", "/api/register", "Public", "Create account"),
        ("GET", "/api/me", "Any user", "Return current profile"),
        ("POST", "/api/logout", "Any user", "Destroy session"),
        ("POST", "/api/change-password", "Any user", "Rotate own password"),
        ("GET", "/api/2fa/setup", "Any user", "TOTP secret / provisioning data"),
        ("POST", "/api/2fa/enable", "Any user", "Turn on two-factor auth"),
        ("POST", "/api/2fa/disable", "Any user", "Turn off two-factor auth"),
        ("POST", "/api/forgot-password", "Public", "Request reset token"),
        ("POST", "/api/reset-password", "Public", "Set new password via token"),
        ("GET", "/api/login-history", "Any user", "Audit trail of own logins"),
        ("GET", "/api/users", "MANAGER+", "List users"),
        ("POST", "/api/users", "MANAGER+", "Create user / assign role"),
        ("PUT", "/api/users/<id>", "MANAGER+", "Update user or role"),
        ("DELETE", "/api/users/<id>", "ADMIN", "Remove a user account"),
     ],
     "User, LoginLog, AuditLog (bcrypt hashes, TOTP secret, session protection)"),

    ("4.2", "Master Data - Products, Categories, Brands",
     "Defines what the store sells. A product carries SKU, name, unit price, reorder level, category and brand; "
     "its live stock is always derived from the sum of its dated batches.",
     [
        "Create categories and brands first so products can be organised and filtered.",
        "Create the product with SKU, price and reorder thresholds. A product is not sellable until stock exists "
        "in a batch (Section 4.5).",
        "Update the price, rename, or deactivate a product - is_active gates it from lists and sales.",
        "The /products page uses low-stock and out-of-stock filters backed by dedicated endpoints.",
     ],
     [
        ("GET", "/api/categories", "Any user", "List categories"),
        ("POST", "/api/categories", "MANAGER+", "Create category"),
        ("GET", "/api/brands", "Any user", "List brands"),
        ("POST", "/api/brands", "MANAGER+", "Create brand"),
        ("GET", "/api/products", "Any user", "List products (with live stock)"),
        ("GET", "/api/products/low-stock", "Any user", "Products at or below reorder level"),
        ("GET", "/api/products/out-of-stock", "Any user", "Products with zero stock"),
        ("GET", "/api/products/<pid>", "Any user", "Product detail"),
        ("POST", "/api/products", "MANAGER+", "Create product"),
        ("PUT", "/api/products/<pid>", "MANAGER+", "Update product"),
        ("DELETE", "/api/products/<pid>", "MANAGER+", "Remove product"),
        ("GET", "/api/products/<pid>/batches", "Any user", "Batches belonging to a product"),
     ],
     "Product, Category, Brand"),

    ("4.3", "Suppliers",
     "Registers the trading partners goods are bought from; suppliers are referenced by stock batches and "
     "purchase orders.",
     [
        "MANAGER+ registers a supplier (name, contact, phone/email, address).",
        "A received batch remembers its supplier_id, and each purchase order is raised against one supplier.",
        "Viewing a supplier's batches shows everything bought from them - the input for ordering decisions.",
     ],
     [
        ("GET", "/api/suppliers", "Any user", "List suppliers"),
        ("GET", "/api/suppliers/<sid>", "Any user", "Supplier detail"),
        ("POST", "/api/suppliers", "MANAGER+", "Create supplier"),
        ("PUT", "/api/suppliers/<sid>", "MANAGER+", "Update supplier"),
        ("DELETE", "/api/suppliers/<sid>", "MANAGER+", "Remove supplier"),
        ("GET", "/api/suppliers/<sid>/batches", "Any user", "All batches bought from this supplier"),
     ],
     "Supplier"),

    ("4.4", "Purchase Orders & Stock Receiving",
     "Brings goods into the business. A purchase order lists what is expected; receiving turns ordered lines "
     "into dated stock batches and movements.",
     [
        "MANAGER+ creates a PO against a supplier: each line item carries product, quantity, unit cost, batch "
        "code and optional expiry date; the PO starts ORDERED and its total is summed.",
        "When the goods arrive, receive the PO: add_stock creates or tops up a StockBatch keyed by product + "
        "batch code (cost price, expiry, supplier), raises the product's stock, and appends an IN "
        "InventoryMovement referencing the PO.",
        "received_quantity supports partial receipts; when all lines are complete the PO becomes RECEIVED.",
        "Because stock lives in batches, every unit on the shelf is traceable to a supplier, a cost and an expiry.",
     ],
     [
        ("GET", "/api/purchases", "Any user", "List purchase orders"),
        ("POST", "/api/purchases", "MANAGER+", "Create a purchase order"),
        ("POST", "/api/purchases/<po_id>/receive", "MANAGER+", "Receive stock into batches"),
        ("POST", "/api/inventory/receive", "MANAGER+", "Direct receive shortcut (no PO)"),
     ],
     "PurchaseOrder, PurchaseOrderItem, StockBatch, InventoryMovement (IN)"),

    ("4.5", "Stock Batches & FEFO (First-Expiry-First-Out)",
     "The heart of expiry control. Every good is held in dated batches and sales must consume the "
     "earliest-expiring units first, never the most recent.",
     [
        "Receiving creates StockBatch rows keyed by product + batch_code with quantity, cost price, expiry "
        "date and supplier.",
        "GET /api/fefo returns, per product, the batch list ordered by expiry date ascending - exactly the "
        "order the sale engine will pick from.",
        "When stock is sold, deduct_stock walks batches earliest-expiry first and performs a guarded atomic "
        "UPDATE (WHERE quantity >= needed) so two parallel sales can never oversell the same batch.",
        "Quantity is derived from batches; a zeroed batch is removed from sellable stock while the ledger keeps "
        "its history.",
     ],
     [
        ("GET", "/api/batches", "Any user", "All batches with quantities, cost and expiry"),
        ("GET", "/api/fefo", "Any user", "Per-product FEFO-priority batch order"),
     ],
     "StockBatch; FEFO order used by sales (Section 4.7)"),

    ("4.6", "Inventory Control - Locations, Transfers, Adjustments, Movements",
     "Keeps the ledger truthful. Locations model the shop floor, transfers move goods, adjustments fix counts "
     "after stocktakes, and movements are the immutable audit trail.",
     [
        "A location names a place (aisle/shelf/back-room) and batches can be attached to it.",
        "A transfer moves units between locations; it records a TRANSFER InventoryMovement and switches the "
        "batch location.",
        "An adjustment corrects a physical count: the difference becomes an ADJUST movement and the batch "
        "quantity updates atomically.",
        "Movement history (IN / OUT / ADJUST / TRANSFER / WASTAGE) is the single source of truth for what "
        "happened to every unit.",
     ],
     [
        ("GET", "/api/inventory", "Any user", "Live stock view (products, batches, locations)"),
        ("POST", "/api/inventory/adjust", "MANAGER+", "Correct a counted quantity"),
        ("GET", "/api/inventory/movements", "Any user", "Movement ledger"),
        ("GET", "/api/locations", "Any user", "List locations"),
        ("POST", "/api/locations", "MANAGER+", "Create a location"),
        ("POST", "/api/locations/transfer", "Any user", "Transfer stock between locations"),
        ("GET", "/api/locations/transfers", "Any user", "Transfer history"),
     ],
     "InventoryMovement, Location, LocationTransfer, StockBatch"),

    ("4.7", "Sales & Payment",
     "Converts stock into revenue while quietly keeping the expiry promise: the sale deducts FEFO-first and "
     "records exactly which batch was sold on every invoice line.",
     [
        "A staff member (STAFF+) POSTs a sale: items (product_id + quantity), payment method, optional customer "
        "and notes.",
        "For each line, deduct_stock allocates FEFO-first. A SaleItem row is created per allocated batch, so "
        "every unit on the invoice points at a physical, dated batch.",
        "Totals are computed: subtotal, discounts, tax (0% configured), total; a Payment row persists the "
        "transaction.",
        "If any line cannot be fully satisfied the entire sale is rolled back with a 400 error - no partial "
        "sales and never negative stock (this is the concurrency guarantee).",
        "On success the sale commits once, an invoice number (INV-XXXX) is generated, the action is audited "
        "and the sale is returned.",
     ],
     [
        ("GET", "/api/sales", "Any user", "Recent sales (max 300, newest first)"),
        ("GET", "/api/sales/<id>", "Any user", "Sale detail incl. per-batch items"),
        ("POST", "/api/sales", "STAFF+", "Record sale (FEFO deduction + payment)"),
        ("GET", "/api/customers", "Any user", "List customers"),
        ("POST", "/api/customers", "STAFF+", "Create customer"),
     ],
     "Sale, SaleItem, Payment, StockBatch, InventoryMovement (OUT), AuditLog"),

    ("4.8", "Spoilage Risk Engine",
     "Puts a number on every batch's risk of going to waste so staff know what to move first. Score 0-100 with "
     "levels LOW / MEDIUM / HIGH (CRITICAL at >=80), blends days-to-expiry with sales velocity.",
     [
        "GET /api/ai/risk computes a 30-day sales velocity per product, then runs batch_risk over every live "
        "batch.",
        "batch_risk combines how soon the batch expires versus how fast the product sells into a single score; "
        "the same score feeds pricing, the dashboard and alerts.",
        "GET /api/ai/risk/<batch_id> returns the breakdown for one batch to justify the recommendation on "
        "screen.",
     ],
     [
        ("GET", "/api/ai/risk", "Any user", "Every live batch scored, sorted by risk desc"),
        ("GET", "/api/ai/risk/<batch_id>", "Any user", "Single-batch score breakdown"),
     ],
     "Read-only: StockBatch + velocity; no writes the risk engine itself does not need"),

    ("4.9", "Dynamic Pricing & Promotion Approval",
     "Turns risk into action with a recommendation and a human-checked promotion. The system advises; a "
     "manager proposes; an admin approves.",
     [
        "The pricing engine converts a risk score into a recommended discount % plus a plain-language reason "
        "('expiring soon', 'high velocity at risk', ...).",
        "GET /api/ai/pricing lists every at-risk batch with unit price, recommended discount, discounted price "
        "and reason, sorted by discount size.",
        "A MANAGER creates a Promotion as DRAFT (discount type PERCENTAGE/FIXED, value, optional product, "
        "category, min quantity, date window).",
        "Manager picks SUBMIT with the suggested discount -> PENDING_APPROVAL.",
        "Only ADMIN can APPROVE (to ACTIVE) or REJECT. A manager can later toggle ACTIVE/INACTIVE.",
     ],
     [
        ("GET", "/api/ai/pricing", "Any user", "Recommended discounts per at-risk batch"),
        ("GET", "/api/promotions", "Any user", "List promotions"),
        ("POST", "/api/promotions", "MANAGER+", "Create promotion (DRAFT)"),
        ("PUT", "/api/promotions/<pid>", "MANAGER+", "Edit promotion details"),
        ("POST", "/api/promotions/<pid>/submit", "MANAGER+", "Submit for approval"),
        ("POST", "/api/promotions/<pid>/approve", "ADMIN", "Approve -> ACTIVE"),
        ("POST", "/api/promotions/<pid>/reject", "ADMIN", "Reject -> REJECTED"),
        ("POST", "/api/promotions/<pid>/toggle", "MANAGER+", "Activate / deactivate"),
     ],
     "Promotion (status lifecycle DRAFT -> PENDING_APPROVAL -> ACTIVE/REJECTED/INACTIVE), AuditLog"),

    ("4.10", "Analytics & Forecasting",
     "Turns transactional data into decisions: KPIs, movement classification, demand analysis and a "
     "per-product forecast.",
     [
        "The dashboard endpoint aggregates KPIs (products, stock units/batches, inventory value, revenue, sales "
        "count, waste value, at-risk items, expiring/expired), expiry summary, risk distribution, daily sales "
        "trend, top-10 risk list and low-stock list.",
        "Velocity classifies every product by how fast it sells (30-day units/day).",
        "Demand analysis returns the per-product velocity records as JSON.",
        "Forecast projects a product's next N days (default 7) from ~60 days of sales history with a simple "
        "model.",
     ],
     [
        ("GET", "/api/dashboard", "Any user", "All KPIs, trends, top risk, low stock"),
        ("GET", "/api/ai/velocity", "Any user", "Fast/slow movers list"),
        ("GET", "/api/ai/demand-analysis", "Any user", "Per-product demand records"),
        ("GET", "/api/ai/forecast/<product_id>", "Any user", "Future demand projection"),
     ],
     "Read-only aggregates over Sale, SaleItem, StockBatch, Wastage, Product"),

    ("4.11", "Alerts & Notifications",
     "Proactive monitoring. Scans classify batches, generators raise the three classic alerts, and per-user "
     "notifications surface them with a badge on every page.",
     [
        "POST /api/alerts/scan runs scan_expiry over live batches for a window (days, default 30) classifying "
        "OK / EXPIRING_SOON / EXPIRED; with notify=True it also writes notifications.",
        "POST /api/alerts/generate runs three generators together: low stock (product qty <= reorder level), "
        "expiry (soon/expired), and high risk (risk score above threshold) and returns counts.",
        "GET /api/notifications returns the current user's notifications; unread-count drives the navbar badge; "
        "read / read-all manage state (global notifications are readable by everyone).",
     ],
     [
        ("POST", "/api/alerts/scan", "MANAGER+", "Expiry scan (optionally notify)"),
        ("POST", "/api/alerts/generate", "MANAGER+", "Run all three alert generators"),
        ("GET", "/api/notifications", "Any user", "My notifications"),
        ("GET", "/api/notifications/unread-count", "Any user", "Badge count"),
        ("POST", "/api/notifications/<nid>/read", "Any user", "Mark one notification read"),
        ("POST", "/api/notifications/read-all", "Any user", "Mark all mine read"),
        ("GET", "/api/expiry/scan", "Any user", "Expiry classification (no notify)"),
        ("GET", "/api/expiry/alerts", "Any user", "Only non-OK batches"),
     ],
     "Notification, AuditLog; read-only over StockBatch, Product"),

    ("4.12", "Waste & Revenue Recovery",
     "Formalises the moment stock is lost so the business learns the true cost and the savings from recovery.",
     [
        "STAFF+ records spoilage (product, quantity, reason EXPIRED/DAMAGED/SPOILED/OTHER, optional batch and "
        "location, notes).",
        "record_wastage deducts the exact batch, stores unit cost and potential loss, and records a recovery/ "
        "savings estimate for reporting.",
        "The summary aggregates waste by reason over an optional period (days).",
     ],
     [
        ("GET", "/api/wastage", "Any user", "Recent waste records"),
        ("POST", "/api/wastage", "STAFF+", "Record wastage (deducts batch)"),
        ("GET", "/api/wastage/summary", "Any user", "Aggregated losses & recovery"),
     ],
     "Wastage, StockBatch, InventoryMovement (WASTAGE)"),

    ("4.13", "Reports & Health",
     "Exportable, named reports for management plus a liveness endpoint for monitoring and containers.",
     [
        "GET /api/health is a heartbeat used by Docker healthchecks and uptime monitors.",
        "Each named report aggregates live data on demand: sales, inventory, expiry, discounts, waste, "
        "performance (MANAGER+) and the audit log.",
     ],
     [
        ("GET", "/api/health", "Any user", "Service + database status"),
        ("GET", "/api/reports/sales", "Any user", "Sales aggregation"),
        ("GET", "/api/reports/inventory", "Any user", "Stock on hand / value"),
        ("GET", "/api/reports/expiry", "Any user", "Expiry exposure"),
        ("GET", "/api/reports/discounts", "Any user", "Discount spend"),
        ("GET", "/api/reports/waste", "Any user", "Waste & recovery"),
        ("GET", "/api/reports/performance", "MANAGER+", "Performance metrics"),
        ("GET", "/api/reports/audit", "Any user", "Audit log"),
     ],
     "Read-only aggregations over sales/inventory/expiry/discounts/waste"),

    ("4.14", "Pages & Navigation (front-end shell)",
     "The server-rendered UI. Each page renders its shell from a Jinja template, then fills data from the JSON "
     "API in the browser.",
     [
        "/login and /register are public; every other page requires a valid session (redirected to "
        "/login?next=... when missing).",
        "The sidebar groups the workspace: Products, Suppliers, Inventory, Batches, Expiry, FEFO, Pricing, "
        "Risk, Sales, Analytics, Alerts, Waste, Reports, Settings, with the dashboard at /.",
        "Static assets: static/css/style.css (layout, cards, badges, centred buttons) and vanilla JS modules "
        "under static/js.",
     ],
     [
        ("GET", "/login", "Public", "Login page"),
        ("GET", "/register", "Public", "Registration page"),
        ("GET", "/", "Session", "Dashboard"),
        ("GET", "/products", "Session", "Products page"),
        ("GET", "/suppliers", "Session", "Suppliers page"),
        ("GET", "/inventory", "Session", "Inventory page"),
        ("GET", "/batches", "Session", "Batches page"),
        ("GET", "/expiry", "Session", "Expiry page"),
        ("GET", "/fefo", "Session", "FEFO order page"),
        ("GET", "/pricing", "Session", "Pricing recommendations"),
        ("GET", "/risk", "Session", "Risk page"),
        ("GET", "/sales", "Session", "Sales / POS page"),
        ("GET", "/analytics", "Session", "Analytics dashboard"),
        ("GET", "/alerts", "Session", "Alerts & notifications"),
        ("GET", "/waste", "Session", "Waste recording"),
        ("GET", "/reports", "Session", "Reports"),
        ("GET", "/settings", "Session", "Settings & profile"),
     ],
     "templates/*.html, static/css/style.css, static/js/*"),
]

for num, title, purpose, flow, endpoints, data in MODULES:
    story += h1("Module %s - %s" % (num, title))
    story.append(P(purpose))
    story.append(P("<b>Working process</b>", S_H3))
    for i, step in enumerate(flow, 1):
        story.append(bullet("<b>Step %d.</b> %s" % (i, step)))
    story.append(Spacer(1, 2 * mm))
    story.append(P("<b>API endpoints</b>", S_H3))
    keep = [ep_table(endpoints)]
    if len(endpoints) <= 8:
        story += [KeepTogether(keep), Spacer(1, 2 * mm)]
    else:
        story.append(ep_table(endpoints))
        story.append(Spacer(1, 2 * mm))
    story.append(P("<b>Data written / touched:</b> %s" % data, S_SMALL))
    story.append(PageBreak())

# ============ 5. ROLE MATRIX ============
story += h1("5. Role & Permission Matrix")
story.append(P("Access uses a minimum-role rule: <font face='Courier'>@at_least(Role.X)</font> grants anything "
               "at or above the rank (USER < STAFF < CASHIER < BILLER < MANAGER < ADMIN). 'Any user' means any "
               "authenticated session.", S_BODY))
matrix = [
    ["Capability", "USER", "STAFF", "CASHIER", "BILLER", "MANAGER", "ADMIN"],
    ["Browse pages, lists and dashboard", "Yes", "Yes", "Yes", "Yes", "Yes", "Yes"],
    ["Record a sale (POS)", "", "Yes", "Yes", "Yes", "Yes", "Yes"],
    ["Create customers", "", "Yes", "", "Yes", "Yes", "Yes"],
    ["Record wastage", "", "Yes", "", "Yes", "Yes", "Yes"],
    ["Manage products / brands / categories / suppliers", "", "", "", "", "Yes", "Yes"],
    ["Purchase orders, receiving, inventory adjust", "", "", "", "", "Yes", "Yes"],
    ["Create / edit / submit / toggle promotions", "", "", "", "", "Yes", "Yes"],
    ["User management (create / edit)", "", "", "", "", "Yes", "Yes"],
    ["Approve / reject promotions", "", "", "", "", "", "Yes"],
    ["Delete users", "", "", "", "", "", "Yes"],
]
matrix_rows = []
for i, row in enumerate(matrix):
    cells = []
    for j, c in enumerate(row):
        if i == 0:
            cells.append(Paragraph("<b>%s</b>" % c, S_CELL_B))
        else:
            cells.append(Paragraph("<b>%s</b>" % c if j == 0 else c, S_CELL))
    matrix_rows.append(cells)
mt = Table(matrix_rows, colWidths=[215, 50, 50, 50, 50, 50, 50])
mt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
    ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(mt)
story.append(Spacer(1, 5 * mm))
story.append(P("The user_loader provides current_user across every request; the security module tests lockout, "
               "rate limiting, 2FA and session protection (35 security tests pass).", S_SMALL))
story.append(PageBreak())

# ============ 6. DATA MODEL ============
story += h1("6. Data Model at a Glance")
story.append(P("Models live in models/ split by domain and are imported through models/__init__.py before "
               "create_all() or migrations run. Shared value lists are enums in models/enums.py.", S_BODY))
dm = [
    ["File", "Tables / values", "Role"],
    ["models/user.py", "users (username, password_hash, role, 2fa_secret, is_active)", "Identity & roles"],
    ["models/login.py", "login_logs (user, ip, user_agent, whether it succeeded)", "Security auditing"],
    ["models/product.py", "categories, brands, products (sku, price, reorder_level)", "Master data"],
    ["models/supplier.py", "suppliers", "Master data"],
    ["models/batch.py", "stock_batches (batch_code, quantity, cost_price, expiry_date, supplier_id)",
     "FEFO core"],
    ["models/inventory.py", "locations, location_transfers, inventory_movements (IN/OUT/ADJUST/TRANSFER/WASTAGE)",
     "Ledger"],
    ["models/sales.py", "purchase_orders, purchase_order_items, customers, sales, sale_items (batch_id!), payments",
     "Purchasing & sales"],
    ["models/discount.py", "promotions (status lifecycle, discount type/value, date window)", "Pricing"],
    ["models/alert.py", "notifications, audit_logs", "Operations"],
    ["models/waste.py", "wastage (unit_cost, potential_loss, recovered_revenue, savings)", "Loss/recovery"],
    ["models/enums.py", "Role, PurchaseStatus, SaleStatus, PaymentMethod, MovementType, DiscountType, "
     "WastageReason, NotificationType, ExpiryStatus, PromoStatus", "Shared rules"],
]
dm_cells = []
for i, row in enumerate(dm):
    cells = []
    for j, c in enumerate(row):
        st = S_CELL_B if i == 0 else (S_MONO if j == 2 else S_CELL)
        txt = c if j != 0 else ("<font face='Courier' size='7.4'>%s</font>" % c)
        cells.append(Paragraph(txt, st))
    dm_cells.append(cells)
mt2 = Table(dm_cells, colWidths=[70, 240, 205])
mt2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
    ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(mt2)
story.append(PageBreak())

# ============ 7. GOLDEN PATH ============
story += h1("7. Golden-Path Business Workflows (end to end)")
story.append(P("<b>Workflow A - Receive goods into stock</b>", S_H3))
for b in [
    "MANAGER opens Purchase Orders and creates a PO against a supplier (quantity, cost, batch code, expiry).",
    "Goods arrive; the manager taps Receive. add_stock upserts StockBatch (product + batch code), sets cost and "
    "expiry, raises product stock, writes an IN movement.",
    "The batch immediately appears in Batches, FEFO, Expiry, Risk and Pricing views - no extra steps.",
]:
    story.append(bullet(b))
story.append(P("<b>Workflow B - Ring up a sale (FEFO in action)</b>", S_H3))
for b in [
    "Cashier opens Sales and enters items. The browser POSTs /api/sales.",
    "deduct_stock walks that product's batches earliest-expiry first and performs a guarded atomic UPDATE per batch.",
    "SaleItem rows attach to each allocated batch so the invoice proves which date was sold; stock, movements and "
    "value update in the same commit.",
    "If any line can't be covered the whole sale returns 400 and nothing is written (concurrency-safe).",
]:
    story.append(bullet(b))
story.append(P("<b>Workflow C - Discount a risky batch</b>", S_H3))
for b in [
    "The risk engine flags a slow-moving batch HIGH risk (Section 4.8).",
    "Pricing suggests a discount % and reason; the manager creates a promotion and clicks SUBMIT.",
    "An admin approves it ACTIVE; the batch now sells faster and waste that would have occurred is avoided.",
]:
    story.append(bullet(b))
story.append(P("<b>Workflow D - Daily close</b>", S_H3))
for b in [
    "Alerts page: run Expiry scan and Generate alerts; unread badge cleared.",
    "Dashboard and Analytics show what moved and what is at risk; Reports export sales/expiry/waste.",
    "Any loss is logged via Waste with a recovery estimate and the audit log records every action taken all day.",
]:
    story.append(bullet(b))
story.append(PageBreak())

# ============ 8. QUALITY ============
story += h1("8. Quality, Tests, CI & Deployment")
story.append(P("<b>Automated test suites (all green)</b>", S_H3))
qa = [
    ["Suite", "Covers", "Result"],
    ["tests/test_engines.py", "FEFO allocation order, expiry classification, risk scoring, pricing advice",
     "6 tests pass"],
    ["tests/test_security.py", "Lockout, rate limiting, 2FA flow, session protection, RBAC, brute force",
     "30 tests pass"],
    ["tests/test_smoke.py", "Login, dashboard, receive, sale (FEFO), alerts, reports, pages",
     "pass"],
    ["tests/test_concurrency.py", "20 parallel 1-unit sales -> 20 succeed, stock ends at 0, no oversell; "
     "oversized sale refused", "20 tests pass"],
]
qa_t = Table([[Paragraph("<b>%s</b>" % c if i == 0 else c, S_CELL_B if i == 0 else (S_MONO if i == 1 and j == 0 else S_CELL))
              for j, c in enumerate(row)] for i, row in enumerate(qa)], colWidths=[120, 300, 95])
qa_t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
    ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(qa_t)
story.append(Spacer(1, 4 * mm))
story.append(P("<b>Coverage & CI</b>", S_H3))
for b in [
    "Combined coverage ~72%; GitHub Actions workflow (.github/workflows/ci.yml) runs all four suites on Python "
    "3.11 and 3.12 and enforces a 50% coverage floor.",
    "The concurrency suite specifically proves two cashiers cannot oversell the same batch.",
]:
    story.append(bullet(b))
story.append(P("<b>Deployment (one command)</b>", S_H3))
for b in [
    "docker compose up starts MySQL 8.4 (healthchecked), the Flask app (gunicorn on :8000) and an nginx "
    "TLS proxy that redirects :80 to :443 and serves the app over HTTPS.",
    "An entrypoint waits for the DB, runs init-db, optionally seeds demo data, then launches gunicorn.",
]:
    story.append(bullet(b))
story.append(PageBreak())

# ============ 9. RUN / TEST / DEPLOY ============
story += h1("9. Running, Testing, Deploying")
story.append(P("<b>Local development</b>", S_H3))
cmds = [
    (".venv\\Scripts\\python.exe -m flask --app app run", "Start the app on http://localhost:5000"),
    (".venv\\Scripts\\python.exe -m flask --app app init-db", "Create the database schema"),
    (".venv\\Scripts\\python.exe -m flask --app app seed", "Load demo data"),
    (".venv\\Scripts\\python.exe -m flask --app app create-admin", "Create an admin account"),
    (".venv\\Scripts\\python.exe tests\\test_engines.py", "Engine tests"),
    (".venv\\Scripts\\python.exe tests\\test_security.py", "Security tests"),
    (".venv\\Scripts\\python.exe tests\\test_smoke.py", "Smoke tests"),
    (".venv\\Scripts\\python.exe tests\\test_concurrency.py", "Concurrency tests"),
    ("coverage run -m pytest; coverage report --fail-under=50", "Coverage gate"),
]
c_t = Table([[Paragraph("<font face='Courier' size='7.4'>%s</font>" % a, S_CELL), Paragraph(b, S_CELL)]
             for a, b in cmds], colWidths=[290, 225])
c_t.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#EFF4FA")]),
    ("GRID", (0, 0), (-1, -1), 0.4, LIGHT_LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(c_t)
story.append(Spacer(1, 4 * mm))
story.append(P("<b>Docker</b>", S_H3))
story.append(bullet("docker compose up --build  -> MySQL 8.4 + Flask/gunicorn + nginx TLS on 443 (self-signed cert "
                    "generated at startup for demos; mount a real cert volume in production)."))
story.append(P("Demo credentials: <b>admin/admin123</b>, <b>manager/manager123</b>, <b>cashier/cashier123</b>.", S_BODY))
story.append(PageBreak())

# ============ 10. DESIGN NOTES ============
story += h1("10. Design Decisions & Roadmap")
story.append(P("<b>Deliberate decisions</b>", S_H3))
for b in [
    "FEFO-first picking with an atomic guarded UPDATE (WHERE quantity >= needed) is the load-bearing feature: "
    "it both enforces expiry discipline and prevents overselling.",
    "Risk and pricing engines are transparent, rule-based and fully testable - easier to audit for a food "
    "retailer than a black-box model.",
    "Promotions require a manager-to-admin approval chain because automatic discounting is a business decision.",
    "Batch-level traceability on every SaleItem means an invoice can always be reconciled to physical, dated "
    "stock.",
]:
    story.append(bullet(b))
story.append(P("<b>Built-in growth opportunities</b>", S_H3))
for b in [
    "The risk/pricing/forecast engines are transparent rule-based systems that are easy to audit for a food "
    "retailer; ML forecasting can be layered on top later as a drop-in upgrade.",
    "Notifications are lightweight polling with an unread badge; push or websocket delivery plugs in cleanly "
    "without touching the rest of the stack.",
    "Development runs on zero-setup SQLite; production scales cleanly to managed MySQL/PostgreSQL with "
    "multiple gunicorn workers behind the TLS proxy.",
]:
    story.append(bullet(b))
story.append(P("<b>Roadmap</b>", S_H3))
for b in [
    "Receipt / invoice PDF printing from Sales.",
    "Reorder suggestion module (auto-PO drafts from velocity + reorder level + supplier lead time).",
    "Charts rendered server-side to PNG so analytics images can be embedded in reports.",
    "Barcode scanning on receive and at the POS.",
]:
    story.append(bullet(b))
story.append(Spacer(1, 6 * mm))
story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceBefore=6, spaceAfter=6))
story.append(P("End of document. SmartShelf - from dated batch to waste-free shelf.", S_SMALL))

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=16 * mm, bottomMargin=18 * mm,
                        title="SmartShelf - Project Explanation & Working Flow",
                        author="SmartShelf")
doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
print("wrote", OUT)