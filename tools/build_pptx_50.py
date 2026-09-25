"""Generate the 54-slide SmartShelf team deck on the existing project template.

Reuses every drawing helper and slide builder from tools/build_pptx.py (the
"template"), auto-renumbers footers to the exact slide position, and adds the
team-member, module deep-dive, engineering and operations slides needed for a
4-member team to answer anything they are asked.

Includes: Languages & Technologies (slide 3), Top Advantages, Real-Time Usages,
and the Architecture & Working-Flow diagram slide.

Output: Presentations/SmartShelf_Team_Presentation_Final.pptx
"""
import os

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

import build_pptx as bp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Auto-numbering: patch bp.title_bar only. Each content slide calls title_bar
# exactly once. s_title (slide 1) and s_close (slide 54) draw the footer via
# footer() with literal numbers, so the counter starts at 1.
# ---------------------------------------------------------------------------
_orig_title_bar = bp.title_bar
_state = {"n": 1, "total": 56}


def _auto_title_bar(slide, text, kicker=None, num=0, total=0):
    _state["n"] += 1
    return _orig_title_bar(slide, text, kicker, _state["n"], _state["total"])


bp.title_bar = _auto_title_bar


class Deck50(bp.Deck):
    TOTAL = 56


# ---------------------------------------------------------------------------
# Reusable "module sheet" layout: left = purpose + working process,
# right = endpoint list.
# ---------------------------------------------------------------------------
def module_slide(title, kicker, purpose, steps, endpoints):
    def build(dk):
        s = dk.blank()
        dk.background(s, bp.LIGHT)
        bp.title_bar(s, title, kicker=kicker)
        # left: purpose card
        bp.box(s, Inches(0.85), Inches(1.6), Inches(6.35), Inches(1.65),
               fill=bp.WHITE, line=bp.BORDER, radius=0.1)
        bp.box(s, Inches(0.85), Inches(1.6), Inches(0.12), Inches(1.65), fill=bp.INDIGO, radius=0.6)
        bp.txt(s, Inches(1.15), Inches(1.74), Inches(5.7), Inches(0.3), "PURPOSE",
               size=11, bold=True, color=bp.INDIGO)
        bp.txt(s, Inches(1.15), Inches(2.08), Inches(5.75), Inches(1.1), purpose,
               size=12.5, color=bp.TEXT, line_spacing=1.18)
        # left: working process card
        bp.box(s, Inches(0.85), Inches(3.4), Inches(6.35), Inches(3.4), fill=bp.WHITE,
               line=bp.BORDER, radius=0.1)
        bp.txt(s, Inches(1.1), Inches(3.54), Inches(5.7), Inches(0.3), "WORKING PROCESS",
               size=11, bold=True, color=bp.INDIGO)
        bp.para_box(s, Inches(1.1), Inches(3.92), Inches(5.85), Inches(2.8), steps,
                    size=12, gap=8, color=bp.TEXT, line_spacing=1.14)
        # right: endpoints card
        bp.box(s, Inches(7.5), Inches(1.6), Inches(4.95), Inches(5.2), fill=bp.WHITE,
               line=bp.BORDER, radius=0.1)
        bp.box(s, Inches(7.5), Inches(1.6), Inches(4.95), Inches(0.5), fill=bp.NAVY, radius=0.1)
        bp.txt(s, Inches(7.7), Inches(1.68), Inches(4.4), Inches(0.34), "API ENDPOINTS",
               size=12, bold=True, color=bp.WHITE)
        bp.para_box(s, Inches(7.72), Inches(2.28), Inches(4.55), Inches(4.4), endpoints,
                    size=10.5, gap=7, color=bp.TEXT, bullet=False, line_spacing=1.12)
        return s

    return build


def chips_row(s, x, y, items):
    xp = x
    for label, col in items:
        w = Inches(0.26 + 0.115 * len(label))
        bp.chip(s, xp, y, w, Inches(0.4), label, col, size=11.5, radius=0.5)
        xp += w + Inches(0.12)
    return xp


def _table(s, x, y, w, h, rows, widths, header, first_col_bold=True, size=11.5):
    tbl = s.shapes.add_table(len(rows) + 1, len(widths), x, y, w, h).table
    for i, wv in enumerate(widths):
        tbl.columns[i].width = wv
    tbl.first_row = False
    tbl.horz_banding = False
    for c, hv in enumerate(header):
        cell = tbl.cell(0, c)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = bp.rgb(bp.NAVY)
        cell.margin_left = Pt(8)
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = hv
        r.font.bold = True
        r.font.size = Pt(size)
        r.font.color.rgb = bp.rgb(bp.WHITE)
        r.font.name = bp.FONT
    for r_i, row in enumerate(rows, start=1):
        for c_i, val in enumerate(row):
            cell = tbl.cell(r_i, c_i)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = bp.rgb(bp.WHITE if r_i % 2 else bp.LIGHT)
            cell.margin_left = Pt(8)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(size - 0.5)
            run.font.bold = (first_col_bold and c_i == 0) or (c_i == 1 and r_i > 0)
            run.font.name = bp.FONT
            run.font.color.rgb = bp.rgb(bp.NAVY if (first_col_bold and c_i == 0) else bp.TEXT)
    return tbl


# ---------------------------------------------------------------------------
# New slides
# ---------------------------------------------------------------------------
def s50_team(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Meet the SmartShelf Team", kicker="TEAM OF FOUR")
    members = [
        ("MEMBER 1", "[Name]", "Lead & Architecture",
         "Intro, problem, solution, lifecycle, system architecture, data model", bp.INDIGO),
        ("MEMBER 2", "[Name]", "Core Engine",
         "FEFO engine, batches, inventory, sales flow, concurrency & oversell prevention", bp.SKY),
        ("MEMBER 3", "[Name]", "Intelligence",
         "Risk scoring, dynamic pricing, analytics, alerts, waste & recovery", bp.VIOLET),
        ("MEMBER 4", "[Name]", "Engineering & Ops",
         "Security, RBAC, testing, CI, Docker deployment, roadmap", bp.GREEN),
    ]
    x0, y0 = Inches(0.85), Inches(1.7)
    cw, ch = Inches(5.85), Inches(2.5)
    gx, gy = Inches(0.25), Inches(0.35)
    for i, (num, name, role, scope, col) in enumerate(members):
        r, c = i // 2, i % 2
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        bp.box(s, x, y, cw, ch, fill=bp.WHITE, line=bp.BORDER, radius=0.1)
        bp.box(s, x, y, cw, Inches(0.12), fill=col, radius=0.6)
        bp.icon_badge(s, x + Inches(0.3), y + Inches(0.3), Inches(0.95), str(i + 1), col, size=30)
        bp.txt(s, x + Inches(1.5), y + Inches(0.32), cw - Inches(1.8), Inches(0.4), num,
               size=11, bold=True, color=bp.MUTED)
        bp.txt(s, x + Inches(1.5), y + Inches(0.62), cw - Inches(1.8), Inches(0.5), name,
               size=20, bold=True, color=bp.NAVY)
        bp.chip(s, x + Inches(0.3), y + Inches(1.42), Inches(2.5), Inches(0.4), role,
                col, size=12, radius=0.5)
        bp.txt(s, x + Inches(0.3), y + Inches(1.95), cw - Inches(0.6), Inches(0.5), scope,
               size=11, color=bp.MUTED, line_spacing=1.1)
    bp.txt(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.4),
           "Each member owns a clear slice of the build and the talking points that go with it.",
           size=13, bold=True, color=bp.INDIGO)


def s50_agenda(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Contents - 56 Slides", kicker="AGENDA")
    items = [
        ("1-2", "Title & Team"),
        ("3-4", "Languages & Tools, Agenda"),
        ("5-8", "About, Problem, Solution, Features"),
        ("9-10", "Top Advantages, Real-Time Usage"),
        ("11-16", "Lifecycle, FEFO concept, FEFO demo, FIFO vs FEFO, concurrency"),
        ("17-19", "Module map + auth deep-dive (auth, security, authflow)"),
        ("20-23", "Roles & access: roles matrix, RBAC, role-based do's & don'ts"),
        ("24-29", "Deep-dive: products, suppliers, PO, batches, inventory, sales"),
        ("30-33", "Risk engine, risk levels, dynamic pricing, approval flow"),
        ("34-37", "Analytics, alerts, waste, reports modules"),
        ("38-40", "Architecture, diagrams, request lifecycle"),
        ("41-44", "Data model, deep dive, tech stack, API map"),
        ("45-46", "Scalability, Docker deployment"),
        ("47-50", "Live demo, demo accounts, quality, test coverage"),
        ("51-54", "CI pipeline, security testing, threat model, decisions"),
        ("55-56", "Roadmap, Thank you"),
    ]
    x0, y0 = Inches(0.85), Inches(1.7)
    pitch_y = Inches(0.48)
    w = Inches(5.8)
    for i, (rng, label) in enumerate(items):
        r, c = i // 2, i % 2
        x = x0 + c * Inches(6.0)
        y = y0 + (r % 8) * pitch_y
        fill = bp.INDIGO if (i % 2 == 0) else bp.SKY
        bp.icon_badge(s, x, y, Inches(0.42), rng, fill, size=11)
        bp.txt(s, x + Inches(0.56), y - Inches(0.04), w - Inches(0.6), Inches(0.42), label,
               size=12, color=bp.TEXT, anchor=MSO_ANCHOR.MIDDLE)
    bp.txt(s, Inches(0.85), Inches(6.7), Inches(11.6), Inches(0.35),
           "Ordered so any question can be answered with two or three adjacent slides.",
           size=12.5, color=bp.MUTED)


def s50_about(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "About SmartShelf", kicker="MISSION")
    bp.txt(s, Inches(0.85), Inches(1.7), Inches(11.6), Inches(0.9),
           "\"A single platform that receives, stores, sells and clears perishable stock by expiry "
           "date - so the store never loses money to forgotten inventory.\"",
           size=17, bold=True, color=bp.NAVY, line_spacing=1.25)
    bp.txt(s, Inches(0.85), Inches(2.85), Inches(11.6), Inches(0.6),
           "A retail inventory intelligence system built around a First-Expired-First-Out engine.",
           size=16, color=bp.INDIGO)
    bp.box(s, Inches(0.85), Inches(3.65), Inches(5.7), Inches(2.7), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(1.1), Inches(3.8), Inches(5.2), Inches(0.3), "WHY WE BUILT IT",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(1.1), Inches(4.2), Inches(5.25), Inches(2.0), [
        "Manual expiry checks miss most of the risk.",
        "Discounts were gut-feel, not data.",
        "Stock-outs and waste lost money silently.",
        "No one could prove which batch was sold.",
    ], size=13, gap=9, color=bp.TEXT)
    bp.box(s, Inches(6.85), Inches(3.65), Inches(5.6), Inches(2.7), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(7.1), Inches(3.8), Inches(5.1), Inches(0.3), "WHAT IT PROMISES",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(7.1), Inches(4.2), Inches(5.15), Inches(2.0), [
        "Know exactly what is on the shelf and when it expires.",
        "Always sell the oldest stock first - automatically.",
        "Quantify spoilage risk and act before the loss.",
        "Keep a full, auditable record of every action.",
    ], size=13, gap=9, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.52), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.62), Inches(10.9), Inches(0.4),
           "Six roles, one hierarchy: Admin, Manager, Biller, Cashier, Staff, User - all on the same data.",
           size=13.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_fefo_concept(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "FEFO - The Core Idea", kicker="FIRST EXPIRED, FIRST OUT")
    bp.box(s, Inches(0.85), Inches(1.65), Inches(5.7), Inches(4.4), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(0.85), Inches(1.65), Inches(5.7), Inches(0.12), fill=bp.SKY, radius=0.6)
    bp.txt(s, Inches(1.1), Inches(1.9), Inches(5.1), Inches(0.4), "THE RULE",
           size=11, bold=True, color=bp.INDIGO)
    bp.txt(s, Inches(1.1), Inches(2.35), Inches(5.2), Inches(0.8),
           "When stock runs low, always take units from the batch that expires first.",
           size=17, bold=True, color=bp.NAVY, line_spacing=1.2)
    bp.para_box(s, Inches(1.1), Inches(3.35), Inches(5.2), Inches(2.6), [
        "The system sorts batches by expiry date.",
        "Expired stock is quarantined to waste, never sold.",
        "Sales, transfers and promotions all follow the same rule.",
        ("Result: nothing rots on the shelf while fresh stock is sold first.", "b"),
    ], size=13.5, gap=10, color=bp.TEXT)
    bp.box(s, Inches(6.85), Inches(1.65), Inches(5.6), Inches(4.4), fill=bp.NAVY, radius=0.12)
    bp.txt(s, Inches(7.15), Inches(1.9), Inches(5.0), Inches(0.4), "WHY IT MATTERS TO A RETAILER",
           size=11, bold=True, color=bp.SLATE)
    bp.para_box(s, Inches(7.15), Inches(2.4), Inches(5.0), Inches(3.5), [
        "Sell-through before expiry  -  margin protected",
        "No manual first-out judgement  -  one rule everywhere",
        "Traceability  -  every sale knows its batch",
        "Less waste  -  fewer write-offs, less value lost",
    ], size=14, gap=12, bullet=False, color=bp.SLATE)
    bp.txt(s, Inches(0.85), Inches(6.25), Inches(11.6), Inches(0.4),
           "FEFO is not FIFO: it is priority by expiry date and sell-by date, not arrival order.",
           size=15, bold=True, color=bp.INDIGO)


def s50_fefo_fifo(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "FEFO vs FIFO vs LIFO", kicker="PICKING STRATEGIES")
    rows = [
        ("Strategy", "Priority", "Best use", "Shelf-loss risk"),
        ("FEFO - First Expired, First Out", "Earliest expiry date", "Perishables, dated goods", "Lowest"),
        ("FIFO - First In, First Out", "Arrival order", "Non-perishables, cosmetics", "Medium"),
        ("LIFO - Last In, First Out", "Newest arrivals", "Accounting fiction, rarely retail", "Highest"),
    ]
    _table(s, Inches(0.85), Inches(1.7), Inches(11.6), Inches(2.6), rows,
           [Inches(3.6), Inches(2.6), Inches(3.3), Inches(2.1)],
           ["Strategy", "Priority", "Best use", "Shelf-loss risk"])
    bp.box(s, Inches(0.85), Inches(4.7), Inches(11.6), Inches(1.9), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(1.15), Inches(4.88), Inches(10.9), Inches(0.35), "WHY FIFO FAILS FOR FOOD",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(1.15), Inches(5.28), Inches(11.0), Inches(1.25), [
        "Two batches, same product: the newer one may expire sooner (short-shelf-life production run).",
        "FIFO assumes order equals freshness - which is false with dairy, bakery and cold-chain goods.",
        "SmartShelf therefore ranks by expiry date: FEFO keeps it correct even when arrival order lies.",
    ], size=13.5, gap=8, color=bp.TEXT)
    bp.txt(s, Inches(0.85), Inches(6.75), Inches(11.6), Inches(0.35),
           "FEFO = FIFO with an expiry-date tiebreaker, applied everywhere automatically.",
           size=13.5, bold=True, color=bp.INDIGO)


def s50_concurrency(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Concurrency: No Overselling", kicker="ATOMIC STOCK")
    bp.txt(s, Inches(0.85), Inches(1.6), Inches(6.2), Inches(0.5),
           "The hard problem", size=20, bold=True, color=bp.NAVY)
    bp.para_box(s, Inches(0.85), Inches(2.15), Inches(6.1), Inches(1.6), [
        "Two cashiers scan the same last unit at the same moment.",
        "Each reads quantity = 1, each decrements, both sell the same unit.",
        ("Result: negative stock, a bad invoice, and an angry customer.", "b"),
    ], size=14.5, gap=10, color=bp.TEXT)
    bp.txt(s, Inches(0.85), Inches(3.95), Inches(6.2), Inches(0.5),
           "The fix", size=20, bold=True, color=bp.NAVY)
    bp.para_box(s, Inches(0.85), Inches(4.5), Inches(6.1), Inches(1.9), [
        "Deduct with a single guarded atomic UPDATE:",
        "\"UPDATE stock_batches SET quantity = quantity - n WHERE id = ? AND quantity >= n\".",
        "If zero rows change, the batch is gone - roll back and tell the cashier.",
        "MySQL/PostgreSQL also lock the row (SELECT ... FOR UPDATE) during FEFO allocation.",
    ], size=13, gap=8, color=bp.TEXT)
    bp.box(s, Inches(7.45), Inches(1.7), Inches(5.0), Inches(4.9), fill=bp.NAVY, radius=0.12)
    bp.txt(s, Inches(7.75), Inches(1.95), Inches(4.4), Inches(0.4),
           "PROOF: THE TEST", size=12, bold=True, color=bp.SKY)
    bp.para_box(s, Inches(7.75), Inches(2.45), Inches(4.4), Inches(3.9), [
        "20 parallel cashiers sell 1 unit from the same batch",
        "20 of 20 succeed - no lost updates",
        "Stock ends at exactly 0 - never negative",
        "20 OUT movements keep the ledger exact",
        "Oversized sale refused cleanly with 400",
    ], size=13, gap=10, bullet=False, color=bp.WHITE)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.52), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.62), Inches(10.9), Inches(0.4),
           "Stock is never negative. That single invariant holds under parallel load.",
           size=13.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_requestlifecycle(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Request Lifecycle", kicker="ONE CLICK, EARTH TO DATA")
    steps = [
        ("1. Browser", "Jinja page renders the shell", bp.SKY),
        ("2. API call", "Page JS calls the JSON API", bp.INDIGO),
        ("3. Guard", "Login check + role check", bp.VIOLET),
        ("4. Engine", "Service layer does the math", bp.AMBER),
        ("5. Database", "ORM + one atomic commit", bp.GREEN),
        ("6. Response", "JSON returns, UI updates", bp.RED),
    ]
    x = Inches(0.85)
    w = Inches(1.62)
    y = Inches(1.9)
    for i, (t, desc, col) in enumerate(steps):
        bp.box(s, x, y, w, Inches(2.0), fill=bp.WHITE, line=bp.BORDER, radius=0.12)
        bp.box(s, x, y, w, Inches(0.1), fill=col, radius=0.6)
        bp.txt(s, x + Inches(0.1), y + Inches(0.22), w - Inches(0.2), Inches(0.5), t,
               size=13, bold=True, color=bp.NAVY, align=PP_ALIGN.CENTER, line_spacing=1.0)
        bp.txt(s, x + Inches(0.1), y + Inches(0.82), w - Inches(0.2), Inches(1.1), desc,
               size=9.5, color=bp.MUTED, align=PP_ALIGN.CENTER, line_spacing=1.12)
        if i < 5:
            bp.box(s, x + w + Inches(0.03), y + Inches(0.7), Inches(0.26), Inches(0.6),
                   fill=bp.MUTED, shape=bp.MSO_SHAPE.RIGHT_ARROW)
        x += w + Inches(0.32)
    bp.box(s, Inches(0.85), Inches(4.25), Inches(11.6), Inches(2.25), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(1.15), Inches(4.42), Inches(10.9), Inches(0.35),
           "WHAT MAKES IT RELIABLE", size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(1.15), Inches(4.82), Inches(11.0), Inches(1.55), [
        "Business logic lives in services (engines), never inside routes - testable and repeatable.",
        "A mutation commits once; every commit also writes an audit log row.",
        "Auth: Flask-Login session; role: @at_least(Role.X); API: clean 401 JSON; pages: redirect to login?next=",
    ], size=13.5, gap=8, color=bp.TEXT)
    bp.txt(s, Inches(0.85), Inches(6.7), Inches(11.6), Inches(0.35),
           "Fast, auditable and uniform - every read or write takes the same path.",
           size=13.5, bold=True, color=bp.INDIGO)


def s50_datamodel_deep(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Database Tables (Deep Dive)", kicker="NORMALIZED SCHEMA")
    rows = [
        ("users / login_logs", "credentials, roles, 2FA secret, login audit"),
        ("categories / brands / products", "catalogue, SKU, price, reorder level"),
        ("suppliers", "sourcing master"),
        ("stock_batches", "batch code, quantity, cost, expiry, supplier link"),
        ("locations / location_transfers", "shop-floor placement + movements"),
        ("inventory_movements", "IN / OUT / ADJUST / TRANSFER / WASTAGE ledger"),
        ("purchase_orders (+items)", "what was ordered, cost, expected/actual dates"),
        ("customers / sales / sale_items / payments", "commerce with batch-accurate lines"),
        ("promotions", "discount type, value, status lifecycle, approver"),
        ("notifications / audit_logs", "alerts to users + immutable action history"),
        ("wastage", "reason, quantity, loss value, recovery estimate"),
    ]
    _table(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(5.35), rows,
           [Inches(4.1), Inches(7.5)],
           ["Tables", "What they hold"], size=12)
    bp.txt(s, Inches(0.85), Inches(6.75), Inches(11.6), Inches(0.35),
           "Every unit of stock is traceable to a batch, a supplier, a cost and an expiry.",
           size=13.5, bold=True, color=bp.INDIGO)


def s50_api_map(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "API Map", kicker="84 ENDPOINTS, 12 BLUEPRINTS")
    rows = [
        ("/api/auth", "login, register, me, 2FA, passwords, users", "Identity"),
        ("/api/products", "catalogue, categories, brands, batches", "Master data"),
        ("/api/suppliers", "supplier CRUD + supplier batches", "Master data"),
        ("/api/inventory", "stock view, adjust, movements, locations, transfers", "Stock"),
        ("/api/batches", "batch list + FEFO order", "Engine"),
        ("/api/sales", "sales, customers, purchase orders + receive", "Commerce"),
        ("/api/ai/risk", "batch risk scores", "Engine"),
        ("/api/ai/pricing", "discount recommendations", "Engine"),
        ("/api/promotions", "promotion lifecycle + approval", "Pricing"),
        ("/api/analytics|dashboard", "KPIs, velocity, demand, forecast", "Analytics"),
        ("/api/alerts + /api/expiry", "scans, generate, notifications", "Ops"),
        ("/api/wastage + /api/reports", "waste, report aggregation, health", "Ops"),
    ]
    _table(s, Inches(0.85), Inches(1.7), Inches(11.6), Inches(5.4), rows,
           [Inches(3.1), Inches(6.0), Inches(2.5)],
           ["Base path", "Endpoints", "Family"], size=12)
    bp.box(s, Inches(0.85), Inches(6.6), Inches(11.6), Inches(0.5), fill=bp.NAVY, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.68), Inches(10.9), Inches(0.38),
           "All JSON under /api; page routes under /; /api/health powers uptime monitors.",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_scalability(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Performance & Scale", kicker="SINGLE STORE TO CHAIN")
    bp.txt(s, Inches(0.85), Inches(1.6), Inches(5.5), Inches(0.5), "Built for today",
           size=19, bold=True, color=bp.NAVY)
    bp.para_box(s, Inches(0.85), Inches(2.15), Inches(5.5), Inches(3.0), [
        "Atomic stock updates keep correctness under load.",
        "Batch/FEFO queries use indexed columns (product_id, expiry_date).",
        "Movement ledger designed to grow without losing history.",
        "Logic engines are pure Python - trivially cacheable.",
    ], size=14, gap=10, color=bp.TEXT)
    bp.txt(s, Inches(6.85), Inches(1.6), Inches(5.6), Inches(0.5), "Growth path",
           size=19, bold=True, color=bp.NAVY)
    bp.para_box(s, Inches(6.85), Inches(2.15), Inches(5.6), Inches(3.0), [
        "SQLite (dev) -> MySQL / PostgreSQL (prod) via DATABASE_URL.",
        "Gunicorn workers behind an nginx TLS proxy.",
        "Row locks (SELECT ... FOR UPDATE) already in the FEFO path.",
        "Swap engines / buses without touching routes.",
    ], size=14, gap=10, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(5.5), Inches(11.6), Inches(1.05), fill=bp.INDIGO, radius=0.12)
    bp.txt(s, Inches(1.15), Inches(5.68), Inches(11), Inches(0.7),
           "Multi-store scale: run one instance per store sharing a managed database - the schema and "
           "API are already DB-agnostic.",
           size=13.5, color=bp.WHITE, line_spacing=1.2)


def s50_deploy(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Deployment - One Command", kicker="DOCKER + TLS")
    comps = [
        ("MySQL 8.4", "Persistent product database, healthchecked", bp.SKY),
        ("Flask + gunicorn", "App server on :8000, entrypoint waits for DB", bp.INDIGO),
        ("nginx TLS", ":80 -> :443 redirect, HTTPS, gzip", bp.GREEN),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for i, (t, desc, col) in enumerate(comps):
        bp.box(s, x, Inches(1.75), w, Inches(1.9), fill=bp.WHITE, line=bp.BORDER, radius=0.1)
        bp.box(s, x, Inches(1.75), w, Inches(0.12), fill=col, radius=0.6)
        bp.txt(s, x + Inches(0.3), Inches(2.05), w - Inches(0.6), Inches(0.5), t,
               size=17, bold=True, color=bp.NAVY)
        bp.txt(s, x + Inches(0.3), Inches(2.6), w - Inches(0.6), Inches(0.9), desc,
               size=12, color=bp.MUTED, line_spacing=1.15)
        x += w + Inches(0.42)
    bp.box(s, Inches(0.85), Inches(4.0), Inches(11.6), Inches(2.35), fill=bp.NAVY, radius=0.12)
    bp.txt(s, Inches(1.15), Inches(4.2), Inches(10.9), Inches(0.4),
           "docker compose up  -  what happens", size=13, bold=True, color=bp.SKY)
    bp.para_box(s, Inches(1.15), Inches(4.68), Inches(11.0), Inches(1.55), [
        "MySQL starts and passes its healthcheck.",
        "App container waits for the DB, runs init-db, optionally seeds demo data.",
        "Gunicorn binds :8000; nginx terminates TLS, serves the app, redirects :80.",
        "Self-signed cert generated at startup for demos - mount a real certificate for production.",
    ], size=13, gap=7, color=bp.SLATE)
    bp.txt(s, Inches(0.85), Inches(6.6), Inches(11.6), Inches(0.4),
           "Every piece is in the repo: Dockerfile, docker-compose.yml, docker/entrypoint.sh, nginx config.",
           size=13.5, bold=True, color=bp.INDIGO)


def s50_ci(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "CI Pipeline", kicker="GITHUB ACTIONS")
    bp.txt(s, Inches(0.85), Inches(1.6), Inches(5.5), Inches(0.5), "On every push & PR",
           size=19, bold=True, color=bp.NAVY)
    bp.para_box(s, Inches(0.85), Inches(2.15), Inches(5.5), Inches(2.9), [
        "Matrix: Python 3.11 and 3.12.",
        "Runs all four test suites independently.",
        "Coverage measured with --fail-under=50 gate.",
        "Fails loudly, never silently skips.",
    ], size=14, gap=10, color=bp.TEXT)
    bp.box(s, Inches(6.85), Inches(1.7), Inches(5.6), Inches(4.3), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(7.1), Inches(1.85), Inches(5.0), Inches(0.3), "WORKFLOW",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(7.1), Inches(2.3), Inches(5.1), Inches(3.6), [
        "lint / check  -  formatting and import sanity",
        "test engines  -  FEFO order, risk, pricing units",
        "test security  -  33 auth & anti-abuse scenarios",
        "test smoke  -  full HTTP journey on Flask",
        "test concurrency  -  20-parallel no-oversell proof",
        "coverage report  -  quality floor enforced",
    ], size=13, gap=9, bullet=False, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.5), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.62), Inches(10.9), Inches(0.38),
           "Merging only happens when every matrix job is green.",
           size=13, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_security_testing(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Security Testing", kicker="33 VERIFIED SCENARIOS")
    bp.box(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75), fill=bp.NAVY, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(1.78), Inches(10.9), Inches(0.5),
           "The claim \"secure by default\" is automated, not decorative.",
           size=16, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)
    groups = [
        ("Lockout", ["5 failed passwords lock 15 min", "reset clears the counter"]),
        ("Rate limiting", ["10 login attempts / 5 min / IP", "429 when exceeded"]),
        ("Passwords", ["policy 8+ & complexity", "common passwords blocked"]),
        ("2FA", ["enable with secret", "verify code", "disable path"]),
        ("Tokens", ["signed reset tokens", "30-min expiry", "single use"]),
        ("Sessions", ["strong protection (IP+UA)", "logout invalidates", "httpOnly cookies"]),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for i, (t, desc) in enumerate(groups):
        r, c = i // 3, i % 3
        xx = x + c * (w + Inches(0.42))
        yy = Inches(2.65) + r * Inches(1.85)
        bp.box(s, xx, yy, w, Inches(1.6), fill=bp.WHITE, line=bp.BORDER, radius=0.1)
        bp.chip(s, xx + Inches(0.3), yy + Inches(0.25), Inches(1.6), Inches(0.42), t,
                bp.INDIGO, size=12, radius=0.4)
        bp.para_box(s, xx + Inches(0.3), yy + Inches(0.85), w - Inches(0.6), Inches(0.7), desc,
                    size=11.5, gap=5, color=bp.TEXT)
    bp.txt(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.5),
           "The security suite runs first in CI - a regression in any control blocks the merge.",
           size=14, bold=True, color=bp.INDIGO)


def s50_threatmodel(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Threat Model", kicker="WHAT ARE WE PROTECTING AGAINST?")
    rows = [
        ("Attack", "Impact if ignored", "SmartShelf countermeasure"),
        ("Credential stuffing / brute force", "Account takeover", "bcrypt + lockout + IP rate limit"),
        ("Session hijacking", "Impersonation", "strong protection, IP+UA binding"),
        ("Stolen password (phishing)", "Data access", "2FA TOTP mandatory path"),
        ("Unprivileged discount approval", "Revenue leak", "RBAC: only Admin approves promos"),
        ("Concurrent oversell", "Negative stock / bad invoices", "atomic guarded UPDATE + row locks"),
        ("Data tampering", "Unreliable records", "immutable audit log on every mutation"),
        ("Forged resets", "Password takeover", "signed, single-use 30-min tokens"),
    ]
    _table(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(3.3), rows,
           [Inches(3.2), Inches(3.3), Inches(5.1)],
           ["Attack", "Impact", "Countermeasure"], size=11.5)
    bp.box(s, Inches(0.85), Inches(4.65), Inches(11.6), Inches(1.7), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(1.15), Inches(4.82), Inches(10.9), Inches(0.35), "ASSUMPTIONS & SCOPE",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(1.15), Inches(5.22), Inches(11.0), Inches(1.05), [
        "Threats in scope: web sessions, auth, authorization, data integrity at the API layer.",
        "Out of scope today: physical device compromise, supply-chain attacks on third-party libs (mitigated by pinned deps).",
    ], size=12.5, gap=7, color=bp.TEXT)
    bp.txt(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.35),
           "Every control above has at least one automated test behind it.",
           size=13.5, bold=True, color=bp.INDIGO)


def s50_rbac(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Role-Based Access Control", kicker="SIX ROLES, ONE HIERARCHY")
    bp.box(s, Inches(0.85), Inches(1.55), Inches(11.6), Inches(0.62), fill=bp.NAVY, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(1.63), Inches(10.9), Inches(0.46),
           "Least privilege by default: every new account is read-only until an admin verifies it and assigns a role.",
           size=13.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)
    bp.box(s, Inches(0.85), Inches(2.4), Inches(6.1), Inches(4.15), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(0.85), Inches(2.4), Inches(6.1), Inches(0.12), fill=bp.INDIGO, radius=0.6)
    bp.txt(s, Inches(1.1), Inches(2.62), Inches(5.6), Inches(0.3), "THE ROLE LADDER  (LEAST → MOST)",
           size=10.5, bold=True, color=bp.INDIGO)
    ladder = [
        ("USER", "Read-only", "Dashboard & stock status only", bp.MUTED),
        ("STAFF", "Support", "+ wastage records and customers", bp.SKY),
        ("CASHIER", "Checkout", "+ sales and invoices (FEFO pick)", bp.VIOLET),
        ("BILLER", "Billing", "+ invoice history and payments", bp.AMBER),
        ("MANAGER", "Operations", "+ products, suppliers, stock, promotions", bp.GREEN),
        ("ADMIN", "Owner", "+ users, role assignment, system config", bp.RED),
    ]
    for i, (role, tag, scope, col) in enumerate(ladder):
        y = Inches(3.02) + i * Inches(0.575)
        bp.chip(s, Inches(1.12), y, Inches(1.35), Inches(0.4), role, col, size=12, radius=0.4)
        bp.txt(s, Inches(2.62), y + Inches(0.005), Inches(4.1), Inches(0.27), tag,
               size=11.5, bold=True, color=bp.NAVY)
        bp.txt(s, Inches(2.62), y + Inches(0.255), Inches(4.1), Inches(0.25), scope,
               size=9.5, color=bp.MUTED)
    bp.box(s, Inches(7.2), Inches(2.4), Inches(5.25), Inches(4.15), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(7.2), Inches(2.4), Inches(5.25), Inches(0.12), fill=bp.SKY, radius=0.6)
    bp.txt(s, Inches(7.45), Inches(2.62), Inches(4.8), Inches(0.3), "WHAT A ROLE DECIDES",
           size=10.5, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(7.45), Inches(3.15), Inches(4.8), Inches(3.3), [
        "Which screens an account can open",
        "Which API calls are allowed (@at_least guards)",
        "What the user may create, edit or approve",
        "Which discounts and promotions need approval",
        "Every action is audited against the account",
        ("Role changes are logged and reversible.", "b"),
    ], size=12.5, gap=9, bullet=False, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(6.72), Inches(11.6), Inches(0.5), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.79), Inches(10.9), Inches(0.38),
           "A cashier never sees admin tools, and an admin never needs the POS - access is exactly the assigned role.",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_rbac_dos_donts(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Role-Based Do's & Don'ts", kicker="ACCESS DISCIPLINE")
    bp.box(s, Inches(0.85), Inches(1.6), Inches(5.7), Inches(5.0), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(0.85), Inches(1.6), Inches(5.7), Inches(0.14), fill=bp.GREEN, radius=0.6)
    bp.chip(s, Inches(1.15), Inches(1.96), Inches(1.35), Inches(0.44), "DO", bp.GREEN,
            size=15, radius=0.4)
    bp.para_box(s, Inches(1.15), Inches(2.65), Inches(5.1), Inches(3.8), [
        ("Verify every new account before its first login - the approval gate.", "b"),
        "Assign the least privilege a job actually needs.",
        "Climb the ladder only when the role demands it: USER → STAFF → CASHIER → BILLER → MANAGER → ADMIN.",
        "Let managers raise promotions; keep the final approval with an admin.",
        "Re-verify or revoke access when staff leave or change desk.",
        ("Review the audit log regularly for \"who did what\".", "b"),
    ], size=12.5, gap=9, bullet=False, color=bp.TEXT)
    bp.box(s, Inches(6.85), Inches(1.6), Inches(5.7), Inches(5.0), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(6.85), Inches(1.6), Inches(5.7), Inches(0.14), fill=bp.RED, radius=0.6)
    bp.chip(s, Inches(7.15), Inches(1.96), Inches(1.35), Inches(0.44), "DON'T", bp.RED,
            size=15, radius=0.4)
    bp.para_box(s, Inches(7.15), Inches(2.65), Inches(5.1), Inches(3.8), [
        ("Don't grant MANAGER or ADMIN to every new user \"to save time\".", "b"),
        "Don't share one login between cashiers or managers - it breaks the audit trail.",
        "Don't let a cashier apply a discount only a manager may own.",
        "Don't let staff deactivate or delete accounts.",
        "Don't let 2FA lapse on admin and manager accounts.",
        ("Don't leave dormant accounts with live access.", "b"),
    ], size=12.5, gap=9, bullet=False, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(6.78), Inches(11.6), Inches(0.5), fill=bp.NAVY, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.85), Inches(10.9), Inches(0.38),
           "Access follows the assigned role - verified, least-privilege, and always audited.",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_notes(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Design Decisions & Growth Path", kicker="ENGINEERING CHOICES")
    bp.txt(s, Inches(0.85), Inches(1.6), Inches(5.5), Inches(0.5), "Deliberate choices",
           size=19, bold=True, color=bp.NAVY)
    bp.box(s, Inches(0.85), Inches(2.2), Inches(5.5), Inches(3.9), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.para_box(s, Inches(1.1), Inches(2.4), Inches(5.05), Inches(3.5), [
        ("FEFO + atomic guard  -  the invariant everything leans on", "b"),
        "Rule-based engines  -  transparent beats black-box",
        "Approval chain  -  discounting is a business decision",
        "Batch-accurate sale lines  -  reconcile to physical stock",
        "Inactive-by-default accounts  -  admin verifies every new user",
    ], size=13, gap=11, bullet=False, color=bp.TEXT)
    bp.txt(s, Inches(6.85), Inches(1.6), Inches(5.6), Inches(0.5), "Growth path",
           size=19, bold=True, color=bp.NAVY)
    bp.box(s, Inches(6.85), Inches(2.2), Inches(5.6), Inches(3.9), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.txt(s, Inches(7.1), Inches(2.38), Inches(5.1), Inches(0.35), "BUILT-IN EXTENSIONS",
           size=11, bold=True, color=bp.INDIGO)
    bp.para_box(s, Inches(7.1), Inches(2.8), Inches(5.15), Inches(3.2), [
        "Engines are transparent rules  -  ML forecasts add on the same way",
        "Notifications poll  -  push/websocket plugs in without a rewrite",
        "Single-node dev  -  managed MySQL/PostgreSQL + workers scale out",
        "Keyboard entry today  -  barcode scanning is a drop-in next step",
    ], size=13, gap=11, bullet=False, color=bp.TEXT)
    bp.box(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.85), fill=bp.NAVY, radius=0.12)
    bp.txt(s, Inches(1.15), Inches(6.5), Inches(11.0), Inches(0.6),
           "Smaller scope, done correctly, beats wider scope done sloppily - which is exactly why the "
           "tests pass and the demo runs.",
           size=14, color=bp.SLATE, line_spacing=1.2)


def card_grid(s, cards, rows, cols, x0=0.85, y0=1.7, w=3.75, h=2.2, gx=0.175, gy=0.3):
    for i, (num, title, tech, why, col) in enumerate(cards):
        r, c = i // cols, i % cols
        x = Inches(x0) + c * (Inches(w) + Inches(gx))
        y = Inches(y0) + r * (Inches(h) + Inches(gy))
        bp.box(s, x, y, Inches(w), Inches(h), fill=bp.WHITE, line=bp.BORDER, radius=0.1)
        bp.box(s, x, y, Inches(w), Inches(0.12), fill=col, radius=0.6)
        chw = Inches(0.26 + 0.115 * len(title))
        if num:
            bp.icon_badge(s, x + Inches(0.28), y + Inches(0.3), Inches(0.38), num, col, size=13)
            cx = x + Inches(0.8)
        else:
            cx = x + Inches(0.25)
        bp.chip(s, cx, y + Inches(0.28), chw, Inches(0.4), title, col, size=12, radius=0.4)
        bp.txt(s, x + Inches(0.25), y + Inches(0.82), Inches(w) - Inches(0.5), Inches(0.85), tech,
               size=12.5, bold=True, color=bp.NAVY, line_spacing=1.1)
        bp.txt(s, x + Inches(0.25), y + Inches(1.68), Inches(w) - Inches(0.5), Inches(0.44), why,
               size=10, color=bp.MUTED, line_spacing=1.05)


def s50_languages(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Languages & Technologies Used", kicker="BUILT WITH")
    cards = [
        (None, "Frontend", "HTML5 · CSS3 · JavaScript (ES6) · Chart.js", "Server-rendered pages with live dashboard charts", bp.SKY),
        (None, "Backend", "Python 3.11/3.12 · Flask 3 · Jinja2 · Flask-Login", "Modular blueprints exposing a REST JSON API", bp.INDIGO),
        (None, "Database", "SQLAlchemy 2 ORM · SQLite (dev) · MySQL 8 / PostgreSQL (prod)", "One schema - switch engines with DATABASE_URL", bp.GREEN),
        (None, "Security", "bcrypt · TOTP 2FA · itsdangerous signed tokens", "Password hashing, one-time codes, safe resets", bp.RED),
        (None, "Engines & Analytics", "Pure-Python FEFO / risk / pricing · pandas · numpy", "Transparent, unit-tested decision logic", bp.VIOLET),
        (None, "Ops & CI", "Gunicorn · Nginx + TLS · Docker · GitHub Actions · pytest", "One-command deployment; every push is tested", bp.AMBER),
    ]
    card_grid(s, cards, rows=2, cols=3)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.5), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.63), Inches(10.9), Inches(0.38),
           "Documentation tooling: ReportLab (PDF) · python-pptx (slides) · Pillow (architecture diagrams).",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_advantages(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Top Advantages", kicker="WHY SMARTSHELF WINS")
    cards = [
        ("1", "Zero expiry waste", "FEFO sells the oldest stock first, automatically.", "Less write-off, protected margin.", bp.GREEN),
        ("2", "No overselling, ever", "Atomic guarded update - stock never goes negative.", "Proven by a 20-way parallel test.", bp.INDIGO),
        ("3", "Every rupee auditable", "Batch-accurate invoices and an immutable audit log.", "Reconcile any invoice to physical stock.", bp.VIOLET),
        ("4", "Secure by default", "bcrypt, TOTP 2FA, lockout, rate limits, RBAC.", "35 automated security scenarios pass.", bp.RED),
        ("5", "Fast to adopt", "Zero-setup SQLite dev; one-command Docker deploy.", "CI runs on every push.", bp.SKY),
        ("6", "Insight built in", "Risk scores, pricing advice, forecasts and alerts.", "84 API endpoints, all dashboards live.", bp.AMBER),
    ]
    card_grid(s, cards, rows=2, cols=3)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.5), fill=bp.NAVY, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.63), Inches(10.9), Inches(0.38),
           "Proof: 20/20 concurrency test · 35 security scenarios · 84 API endpoints · 6 roles.",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_usages(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Real-Time Usages", kicker="WHERE SMARTSHELF RUNS")
    cards = [
        ("1", "Groceries & markets", "Dairy, bakery and fresh aisles rotate by expiry at the POS.", "Every sale picks the oldest batch.", bp.GREEN),
        ("2", "Pharmacies", "Expiry-led picking for medicines and consumables.", "Never dispense stock past its date.", bp.SKY),
        ("3", "Cold chain & FMCG", "Batch-traceable transfers between back room and floor.", "A ledger tracks every unit moved.", bp.INDIGO),
        ("4", "E-commerce picking", "FEFO pick order for every fulfillment row.", "Orders never draw fresh stock first.", bp.VIOLET),
        ("5", "Multi-branch chains", "One instance per store on a shared managed DB.", "Central KPIs, per-store operations.", bp.AMBER),
        ("6", "Back office & audit", "Managers approve promotions; every action is logged.", "Named reports for every decision.", bp.RED),
    ]
    card_grid(s, cards, rows=2, cols=3)
    bp.box(s, Inches(0.85), Inches(6.55), Inches(11.6), Inches(0.5), fill=bp.INDIGO, radius=0.5)
    bp.txt(s, Inches(1.2), Inches(6.63), Inches(10.9), Inches(0.38),
           "One engine, six roles - every scenario follows the same FEFO promise.",
           size=12.5, bold=True, color=bp.WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s50_diagrams(dk):
    s = dk.blank()
    dk.background(s, bp.LIGHT)
    bp.title_bar(s, "Architecture & Working-Flow Diagram", kicker="THE PICTURE BEHIND THE FEATURES")
    img = os.path.join(BASE, "docs", "assets", "architecture.png")
    if os.path.exists(img):
        s.shapes.add_picture(img, Inches(0.85), Inches(1.6), width=Inches(7.7))
        bp.txt(s, Inches(0.85), Inches(6.25), Inches(7.7), Inches(0.35),
               "Full-resolution: docs/assets/architecture.png - also embedded in the project PDF.",
               size=11, color=bp.MUTED)
    else:
        bp.box(s, Inches(0.85), Inches(1.6), Inches(7.7), Inches(4.3), fill=bp.WHITE, line=bp.BORDER)
        bp.txt(s, Inches(1.3), Inches(3.3), Inches(6.9), Inches(0.5),
               "architecture.png not found - run tools/make_diagram.py first.",
               size=13, color=bp.MUTED, align=PP_ALIGN.CENTER)
    bp.box(s, Inches(8.9), Inches(1.6), Inches(4.4), Inches(4.45), fill=bp.WHITE,
           line=bp.BORDER, radius=0.1)
    bp.box(s, Inches(8.9), Inches(1.6), Inches(4.4), Inches(0.5), fill=bp.NAVY, radius=0.1)
    bp.txt(s, Inches(9.1), Inches(1.68), Inches(4.0), Inches(0.34), "WHAT THE DIAGRAM SHOWS",
           size=12, bold=True, color=bp.WHITE)
    bp.txt(s, Inches(9.15), Inches(2.25), Inches(3.95), Inches(3.7), [
        ("Layered build: HTML pages -> JSON API -> service engines -> models -> database.", 13, True, bp.NAVY),
        ("Auth + role guards sit at every API boundary.", 11, False, bp.MUTED),
        ("The 8-step workflow runs along the bottom of the diagram.", 13, True, bp.NAVY),
        ("Receive -> batch -> FEFO pick -> sell -> adjust -> alert -> waste -> report.", 11, False, bp.MUTED),
        ("Every arrow maps to a module and a demo screen.", 13, True, bp.NAVY),
        ("Open docs/assets/architecture.png for the crisp full-resolution version.", 11, False, bp.MUTED),
    ], size=12, color=bp.TEXT, line_spacing=1.1)
    bp.txt(s, Inches(8.9), Inches(6.25), Inches(4.4), Inches(0.35),
           "Live screens: slides 45-46 walk the working UI end to end.",
           size=11, color=bp.MUTED)


MODULES = [
    # title, kicker, purpose, steps, endpooints
    ("Module: Auth & Users", "M1 - IDENTITY",
     "Manages accounts, sessions and roles for all six staff levels.",
     [
        ("Register / login with bcrypt-verified credentials.", "b"),
        "Session bound to IP + user-agent; 2FA (TOTP) optional.",
        "Role checked at every endpoint via @at_least(Role.X).",
        "5 failed logins lock the account for 15 minutes.",
        "Every login and admin action is audited.",
     ],
     ["POST /api/register - create account (public)",
      "POST /api/login - authenticate + open session (public)",
      "GET /api/me - current profile",
      "POST /api/logout - end session",
      "GET /api/users - list (MANAGER+)",
      "PUT /api/users/<id> - edit role (MANAGER+)",
      "DELETE /api/users/<id> - remove (ADMIN)"]),
    ("Module: Master Data", "M2 - PRODUCTS",
     "Catalogue: categories, brands and products with SKU, price and reorder thresholds.",
     [
        "Create categories and brands first to organise the catalogue.",
        "Products carry SKU, name, unit price, reorder level.",
        "Stock is always derived from live batches - never a static number.",
        "is_active gates products from lists and the POS.",
     ],
     ["GET /api/products - catalogue with live stock",
      "POST /api/products - create (MANAGER+)",
      "PUT /api/products/<id> - edit (MANAGER+)",
      "DELETE /api/products/<id> - remove (MANAGER+)",
      "GET /api/products/low-stock - reorder watch",
      "POST /api/categories + /api/brands - (MANAGER+)"]),
    ("Module: Suppliers", "M3 - SOURCING",
     "The trading partners goods come from; referenced by batches and purchase orders.",
     [
        "Manager registers name, contact, phone/email, address.",
        "Every received batch remembers its supplier_id.",
        "Viewing a supplier's batches drives reorder decisions.",
     ],
     ["GET /api/suppliers - list",
      "POST /api/suppliers - create (MANAGER+)",
      "PUT /api/suppliers/<id> - edit (MANAGER+)",
      "DELETE /api/suppliers/<id> - remove (MANAGER+)",
      "GET /api/suppliers/<id>/batches - purchase history"]),
    ("Module: Purchase Orders", "M4 - STOCK IN",
     "Raises orders against suppliers and turns received goods into dated batches.",
     [
        "PO lines carry product, qty, unit cost, batch code, expiry.",
        "Receiving calls add_stock: create/top-up batch + IN movement.",
        "Partial receipts tracked via received_quantity.",
        "PO status ORDERED -> RECEIVED; batch appears in every view.",
     ],
     ["POST /api/purchases - create PO (MANAGER+)",
      "POST /api/purchases/<po_id>/receive - receive (MANAGER+)",
      "POST /api/inventory/receive - direct receive (MANAGER+)",
      "GET /api/purchases - PO list"]),
    ("Module: Batches & Expiry", "M5 - FRESHNESS CORE",
     "The unit of truth: every good is a dated batch with quantity, cost and expiry.",
     [
        "Batch key = product + batch_code, with cost_price and expiry_date.",
        "Expiry scan classifies OK / EXPIRING_SOON / EXPIRED.",
        "FEFO order generates the exact pick sequence for sales.",
        "Zeroed batches leave sellable stock but keep ledger history.",
     ],
     ["GET /api/batches - all batches with status",
      "GET /api/fefo - per-product FEFO pick order",
      "GET /api/products/<pid>/batches - product batches",
      "GET /api/expiry/alerts - non-OK batches"]),
    ("Module: Inventory Control", "M6 - LEDGER",
     "Locations, transfers, adjustments and the immutable movement ledger.",
     [
        "Locations model the shop floor (aisle / shelf / back room).",
        "Transfers move units and write a TRANSFER movement.",
        "Adjustments correct physical counts atomically.",
        "Movement history = single source of truth for every unit.",
     ],
     ["GET /api/inventory - live stock view",
      "POST /api/inventory/adjust - fix count (MANAGER+)",
      "GET /api/inventory/movements - full ledger",
      "POST /api/locations - create (MANAGER+)",
      "POST /api/locations/transfer - move stock"]),
    ("Module: Sales & Payment", "M7 - REVENUE",
     "Checkout that converts stock to revenue while keeping the FEFO promise.",
     [
        "Cashier POSTs items; each line FEFO-deducts exact batches.",
        "SaleItem links every unit to its physical batch.",
        "Totals: subtotal - discount + tax; payment row recorded.",
        "Any unsatisfiable line rolls the whole sale back (no negatives).",
        "Invoice number INV-XXXX generated and audited.",
     ],
     ["POST /api/sales - record sale (STAFF+)",
      "GET /api/sales - recent invoices",
      "GET /api/sales/<id> - per-batch item detail",
      "POST /api/customers - create (STAFF+)"]),
    ("Module: Analytics", "M8 - INSIGHT",
     "Turns transaction data into decisions: KPIs, velocity, demand, forecast.",
     [
        "Dashboard aggregates KPIs + trends + top risk + low stock.",
        "Velocity classifies every product by sell rate (30 days).",
        "Demand analysis returns per-product units/day.",
        "Forecast projects the next N days from ~60 days of history.",
     ],
     ["GET /api/dashboard - KPI suite",
      "GET /api/ai/velocity - fast / slow movers",
      "GET /api/ai/demand-analysis - unit demand records",
      "GET /api/ai/forecast/<product_id> - projection"]),
    ("Module: Alerts", "M9 - PROACTIVITY",
     "Scans, generators and per-user notifications with an unread badge.",
     [
        "Expiry scan tags batches within a 30-day window.",
        "Generators: low stock, expiry, high risk.",
        "Notifications feed a navbar unread badge.",
        "MANAGER+ can trigger scans; everyone reads their own alerts.",
     ],
     ["POST /api/alerts/scan - expiry scan (MANAGER+)",
      "POST /api/alerts/generate - all generators (MANAGER+)",
      "GET /api/notifications - my notifications",
      "GET /api/notifications/unread-count - badge",
      "POST /api/notifications/read-all - clear"]),
    ("Module: Waste", "M10 - RECOVERY",
     "Formalises loss so the business learns the true cost and savings.",
     [
        "STAFF+ records reason, qty, optional batch and location.",
        "record_wastage deducts the exact batch.",
        "Summary aggregates losses and recovery by reason.",
     ],
     ["POST /api/wastage - record (STAFF+)",
      "GET /api/wastage - recent records",
      "GET /api/wastage/summary - aggregated losses"]),
    ("Module: Reports", "M11 - EVIDENCE",
     "Named, exportable reports plus a liveness endpoint for monitoring.",
     [
        "Sales / inventory / expiry / discounts / waste / performance / audit.",
        "Performance reports are MANAGER+ only.",
        "/api/health powers Docker healthchecks and uptime monitors.",
     ],
     ["GET /api/health - service + DB status",
      "GET /api/reports/sales - revenue aggregation",
      "GET /api/reports/performance - (MANAGER+)",
      "GET /api/reports/audit - action history"]),
]
MODULE_FN = {m[0]: module_slide(*m) for m in MODULES}

_SLIDES = [
    ("title", bp.s_title),
    ("team", s50_team),
    ("languages", s50_languages),
    ("agenda", s50_agenda),
    ("about", s50_about),
    ("problem", bp.s_problem),
    ("solution", bp.s_solution),
    ("features", bp.s_features),
    ("advantages", s50_advantages),
    ("usages", s50_usages),
    ("lifecycle", bp.s_lifecycle),
    ("fefo_concept", s50_fefo_concept),
    ("fefo", bp.s_fefo),
    ("fefo_demo", bp.s_fefo_demo),
    ("fefo_fifo", s50_fefo_fifo),
    ("concurrency", s50_concurrency),
    ("modules", bp.s_modules),
    ("auth", MODULE_FN["Module: Auth & Users"]),
    ("security", bp.s_security),
    ("authflow", bp.s_authflow),
    ("roles", bp.s_roles),
    ("rbac_roles", s50_rbac),
    ("roles_dos_donts", s50_rbac_dos_donts),
    ("masterdata", MODULE_FN["Module: Master Data"]),
    ("suppliers", MODULE_FN["Module: Suppliers"]),
    ("po", MODULE_FN["Module: Purchase Orders"]),
    ("batches", MODULE_FN["Module: Batches & Expiry"]),
    ("inventory", MODULE_FN["Module: Inventory Control"]),
    ("sales", MODULE_FN["Module: Sales & Payment"]),
    ("risk", bp.s_risk),
    ("risk_levels", bp.s_risk_levels),
    ("pricing", bp.s_pricing),
    ("promo_flow", bp.s_promo_flow),
    ("analytics", MODULE_FN["Module: Analytics"]),
    ("alerts", MODULE_FN["Module: Alerts"]),
    ("waste", MODULE_FN["Module: Waste"]),
    ("reports", MODULE_FN["Module: Reports"]),
    ("architecture", bp.s_architecture),
    ("diagrams", s50_diagrams),
    ("requestlifecycle", s50_requestlifecycle),
    ("datamodel", bp.s_datamodel),
    ("datamodel_deep", s50_datamodel_deep),
    ("techstack", bp.s_techstack),
    ("api_map", s50_api_map),
    ("scalability", s50_scalability),
    ("deploy", s50_deploy),
    ("demo", bp.s_demo),
    ("logins", bp.s_logins),
    ("quality", bp.s_quality),
    ("coverage", bp.s_coverage),
    ("ci", s50_ci),
    ("security_testing", s50_security_testing),
    ("threatmodel", s50_threatmodel),
    ("notes", s50_notes),
    ("roadmap", bp.s_roadmap),
    ("close", bp.s_close),
]


def build(output_path):
    _state["n"] = 1
    dk = Deck50()
    for name, fn in _SLIDES:
        fn(dk)
    dk.prs.save(output_path)
    print("Saved %s with %d slides; last footer number %d." % (
        output_path, len(dk.prs.slides._sldIdLst), _state["n"]))


if __name__ == "__main__":
    outdir = os.path.join(BASE, "Presentations")
    os.makedirs(outdir, exist_ok=True)
    build(os.path.join(outdir, "SmartShelf_Team_Presentation_Final.pptx"))