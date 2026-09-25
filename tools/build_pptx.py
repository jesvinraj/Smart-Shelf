"""Generate a professional SmartShelf PowerPoint deck (16:9, 25 slides).

Usage:
    .venv\\Scripts\\python.exe tools\\build_pptx.py

Output: SmartShelf_Presentation.pptx
"""
import os

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
NAVY = (0x0F, 0x17, 0x2A)
NAVY2 = (0x10, 0x1B, 0x34)
INDIGO = (0x4F, 0x46, 0xE5)
SKY = (0x0E, 0xA5, 0xE9)
VIOLET = (0x7C, 0x3A, 0xED)
WHITE = (0xFF, 0xFF, 0xFF)
LIGHT = (0xF1, 0xF5, 0xF9)
BORDER = (0xE2, 0xE8, 0xF0)
MUTED = (0x64, 0x74, 0x8B)
TEXT = (0x1E, 0x29, 0x3B)
GREEN = (0x16, 0xA3, 0x4A)
AMBER = (0xEA, 0x7A, 0x1B)
RED = (0xDC, 0x26, 0x26)
SLATE = (0xCB, 0xD5, 0xE1)
GOLD = (0xFB, 0xBF, 0x24)

FONT = "Segoe UI"
MONO = "Consolas"


def rgb(c):
    return RGBColor(c[0], c[1], c[2])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class Deck:
    W = Inches(13.333)
    H = Inches(7.5)
    TOTAL = 25

    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = self.W
        self.prs.slide_height = self.H
        self.total = self.TOTAL
        self.prs.core_properties.title = "SmartShelf - Inventory Intelligence"
        self.prs.core_properties.author = "SmartShelf Engineering"
        self.prs.core_properties.subject = "Product & Technical Overview"

    def blank(self):
        return self.prs.slides.add_slide(self.prs.slide_layouts[6])

    def background(self, slide, color):
        r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, self.W, self.H)
        r.fill.solid()
        r.fill.fore_color.rgb = rgb(color)
        r.line.fill.background()
        r.shadow.inherit = False


def box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        radius=0.08, shadow=False):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(1)
    s.shadow.inherit = shadow
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    return s


def _zero_margins(tf):
    for name in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, name, Pt(0))


def txt(slide, x, y, w, h, text, size=16, bold=False, color=TEXT, align=PP_ALIGN.LEFT,
        anchor=MSO_ANCHOR.TOP, font=FONT, wrap=True, line_spacing=None):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    _zero_margins(tf)
    if isinstance(text, list):
        for i, (t, s, b, c) in enumerate(text):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.space_after = Pt(0)
            if line_spacing:
                p.line_spacing = line_spacing
            r = p.add_run()
            r.text = t
            r.font.size = Pt(s if s else size)
            r.font.bold = b if b is not None else bold
            r.font.color.rgb = rgb(c if c else color)
            r.font.name = font
    else:
        p = tf.paragraphs[0]
        p.alignment = align
        if line_spacing:
            p.line_spacing = line_spacing
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = rgb(color)
        r.font.name = font
    return tb


def para_box(slide, x, y, w, h, items, size=15, color=TEXT, gap=8, bullet=True,
             line_spacing=1.15):
    """items: list of (text, style) where style is str|None."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    _zero_margins(tf)
    for i, item in enumerate(items):
        text = item[0] if isinstance(item, tuple) else item
        style = item[1] if isinstance(item, tuple) else None
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = line_spacing
        run = p.add_run()
        prefix = "\u2022  " if bullet else ""
        run.text = prefix + text
        run.font.size = Pt(size)
        run.font.name = FONT
        run.font.color.rgb = rgb(color)
        if style == "b":
            run.font.bold = True
        elif style == "lead":
            run.font.bold = True
            run.font.size = Pt(size + 1)
            run.font.color.rgb = rgb(INDIGO)
    return tb


def chip(slide, x, y, w, h, text, fill, color=WHITE, size=11, bold=True,
         align=PP_ALIGN.CENTER, radius=0.5):
    c = box(slide, x, y, w, h, fill=fill, radius=radius)
    tf = c.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _zero_margins(tf)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = rgb(color)
    r.font.name = FONT
    return c


def icon_badge(slide, x, y, d, glyph, fill, size=20, glyph_color=WHITE):
    ic = box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    tf = ic.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _zero_margins(tf)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = glyph
    r.font.size = Pt(size)
    r.font.name = FONT
    r.font.color.rgb = rgb(glyph_color)
    return ic


def footer(slide, num, total, dark=False):
    c = SLATE if dark else MUTED
    txt(slide, Inches(0.55), Inches(7.1), Inches(8), Inches(0.3),
        "SmartShelf  \u2022  Inventory Intelligence", size=10, color=c)
    txt(slide, Inches(11.9), Inches(7.1), Inches(0.9), Inches(0.3),
        f"{num} / {total}", size=10, color=c, align=PP_ALIGN.RIGHT)


def title_bar(slide, text, kicker=None, num=0, total=0):
    box(slide, Inches(0.55), Inches(0.52), Inches(0.13), Inches(0.66), fill=INDIGO, radius=0.3)
    if kicker:
        txt(slide, Inches(0.85), Inches(0.42), Inches(11), Inches(0.3), kicker,
            size=11, bold=True, color=INDIGO)
        txt(slide, Inches(0.85), Inches(0.72), Inches(11.6), Inches(0.6), text,
            size=27, bold=True, color=NAVY)
    else:
        txt(slide, Inches(0.85), Inches(0.52), Inches(11.6), Inches(0.75), text,
            size=27, bold=True, color=NAVY)
    box(slide, Inches(0.85), Inches(1.34), Inches(2.2), Inches(0.045), fill=SKY)
    if num:
        footer(slide, num, total)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------
def s_title(d):
    s = d.blank()
    d.background(s, NAVY)
    box(s, Inches(-1.6), Inches(-1.5), Inches(7.6), Inches(7.0), fill=NAVY2, shape=MSO_SHAPE.OVAL)
    box(s, Inches(10.8), Inches(-1.8), Inches(4.8), Inches(4.8), fill=INDIGO, shape=MSO_SHAPE.OVAL)
    box(s, Inches(11.3), Inches(5.7), Inches(3.1), Inches(3.1), fill=SKY, shape=MSO_SHAPE.OVAL)

    logo = box(s, Inches(6.06), Inches(1.72), Inches(1.2), Inches(1.2), fill=INDIGO, radius=0.24)
    tf = logo.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _zero_margins(tf)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "S"
    r.font.size = Pt(44)
    r.font.bold = True
    r.font.color.rgb = rgb(WHITE)
    r.font.name = FONT

    txt(s, Inches(0.6), Inches(3.05), Inches(12.1), Inches(0.9),
        "SmartShelf", size=54, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, Inches(0.6), Inches(4.0), Inches(12.1), Inches(0.6),
        "Inventory Intelligence for Perishable Retail", size=21, color=SKY,
        align=PP_ALIGN.CENTER)

    box(s, Inches(6.24), Inches(4.78), Inches(0.85), Inches(0.045), fill=GOLD)
    txt(s, Inches(0.6), Inches(5.05), Inches(12.1), Inches(0.5),
        "Product & Technical Overview", size=15, bold=True, color=SLATE,
        align=PP_ALIGN.CENTER)

    txt(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.4),
        "September 2026  \u2022  Prepared by SmartShelf Engineering", size=12,
        color=MUTED, align=PP_ALIGN.CENTER)
    footer(s, 1, d.total, dark=True)


def s_agenda(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Contents", kicker="WHAT'S INSIDE", num=2, total=d.total)

    items = [
        "Problem & Impact", "The Solution", "Core Capabilities", "Product Lifecycle",
        "FEFO Picking Engine", "FEFO in Action", "Risk Scoring", "Risk Levels & Actions",
        "Dynamic Pricing", "Pricing Approval Flow", "Platform Modules",
        "System Architecture", "Data Model", "Security by Default",
        "Authentication & Sessions", "Roles & Access", "Technology Stack",
        "Live Demo & Quick Start", "Demo Accounts", "Quality & Reliability",
        "Test Coverage", "Roadmap",
    ]
    cols = 2
    rows = 11
    x0 = Inches(0.85)
    x1 = Inches(6.85)
    pitch_x = Inches(5.8)
    y0 = Inches(1.72)
    pitch_y = Inches(0.47)
    for i, label in enumerate(items):
        r = i // cols
        c = i % cols
        x = x0 if c == 0 else x1
        y = y0 + r * pitch_y
        num_txt = f"{i + 1:02d}"
        fill = INDIGO if (i % 2 == 0) else SKY
        icon_badge(s, x, y, Inches(0.36), num_txt, fill, size=12)
        txt(s, x + Inches(0.5), y - Inches(0.03), pitch_x - Inches(0.6), Inches(0.4),
            label, size=14.5, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

    txt(s, Inches(0.85), Inches(6.7), Inches(11.6), Inches(0.35),
        "22 sections \u2014 each one a buildable, demo-able story.", size=12.5,
        color=MUTED)


def s_problem(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "The Retail Shrink Problem", kicker="WHY IT MATTERS", num=3, total=d.total)

    stats = [
        ("~30%", "of perishable inventory is lost to spoilage & expiry before sale", AMBER,
         "\u23F3"),
        ("\u20B9 Crores", "tied up in dead and expiring stock every year in modern retail", RED,
         "\U0001F4C9"),
        ("Last-Mile", "losses from manually guessing what to discount and when to clear", SKY,
         "\U0001F3AF"),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for val, desc, col, ico in stats:
        card = box(s, x, Inches(1.85), w, Inches(3.0), fill=WHITE, line=BORDER, radius=0.09)
        box(s, x, Inches(1.85), w, Inches(0.14), fill=col, radius=0.5)
        icon_badge(s, x + Inches(0.35), Inches(2.25), Inches(0.8), ico, col, size=26)
        txt(s, x + Inches(1.35), Inches(2.32), w - Inches(1.7), Inches(0.7), val,
            size=30, bold=True, color=col)
        txt(s, x + Inches(0.35), Inches(3.45), w - Inches(0.7), Inches(1.2), desc,
            size=14, color=TEXT, line_spacing=1.2)
        x += w + Inches(0.42)

    txt(s, Inches(0.85), Inches(5.35), Inches(11.6), Inches(0.6),
        "Traditional shelf-life management relies on manual checks, gut-feel discounts, and static expiry reports.",
        size=17, bold=True, color=NAVY)
    txt(s, Inches(0.85), Inches(6.05), Inches(11.6), Inches(0.55),
        "SmartShelf turns that into an automated, data-driven system built around First-Expired-First-Out (FEFO).",
        size=16, color=INDIGO)


def s_solution(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "The SmartShelf Solution", kicker="WHAT IT DOES", num=4, total=d.total)

    peaks = [
        ("Know Everything",
         ["Real-time batch-level stock & expiry", "Live value, movement and alerts",
          "All locations and suppliers in one view"], "\U0001F5C3"),
        ("Sell Fresh First",
         ["Automatic FEFO picking at every sale", "Smart batch allocation by expiry",
          "No manual first-out decisions"], "\U0001F504"),
        ("Act Before Loss",
         ["Risk-scored products & batches", "Recommended discount % and clear reasons",
          "Expiry alerts 30 days ahead"], "\U0001F6E1"),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for title, lines, ico in peaks:
        card = box(s, x, Inches(1.85), w, Inches(4.1), fill=WHITE, line=BORDER, radius=0.09)
        box(s, x, Inches(1.85), Inches(0.85), Inches(4.1), fill=INDIGO, radius=0.12)
        txt(s, x + Inches(1.1), Inches(2.1), w - Inches(1.3), Inches(0.6), title,
            size=19, bold=True, color=NAVY)
        icon_badge(s, x + Inches(0.2), Inches(2.5), Inches(0.55), ico, NAVY, size=18)
        para_box(s, x + Inches(1.1), Inches(2.85), w - Inches(1.4), Inches(3.0), lines,
                 size=13.5, gap=8, bullet=False)
        x += w + Inches(0.42)

    txt(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.5),
        "One platform:  receive \u2192 store \u2192 monitor \u2192 sell \u2192 analyze \u2014 with intelligence at every step.",
        size=15, bold=True, color=INDIGO)


def s_features(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Core Capabilities", kicker="FEATURE SET", num=5, total=d.total)

    feats = [
        ("\U0001F4E6", "Products & Catalogue", "SKU, category, unit, price & shelf-life profiles"),
        ("\U0001F69A", "Suppliers", "Supplier master + purchase receipts"),
        ("\U0001F5C3", "Inventory", "Locations, stock levels, transfers"),
        ("\U0001F5C2", "Batches", "Lot control, receipt, expiry tracking"),
        ("\u23F3", "Expiry Alerts", "30-day window + per-severity notifications"),
        ("\U0001F504", "FEFO Engine", "First-Expired-First-Out picking engine"),
        ("\U0001F6E1", "Risk Scoring", "Per-batch spoilage risk scoring"),
        ("\U0001F4B0", "Pricing & Promos", "Recommended discounts + approval flow"),
        ("\U0001F6D2", "Sales", "Cart checkout with automatic FEFO"),
        ("\u267B", "Waste", "Waste recording & value tracking"),
        ("\U0001F4CA", "Analytics", "Sales trends, KPIs & velocity"),
        ("\U0001F4D1", "Reports", "Workbooks + health endpoint"),
    ]
    cols = 4
    rows = 3
    cw = Inches(2.95)
    ch = Inches(1.52)
    gx = Inches(0.22)
    gy = Inches(0.2)
    x0 = Inches(0.55)
    y0 = Inches(1.62)
    for i, (ico, t, desc) in enumerate(feats):
        r = i // cols
        c = i % cols
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        box(s, x, y, cw, ch, fill=WHITE, line=BORDER, radius=0.1)
        icon_badge(s, x + Inches(0.2), y + Inches(0.22), Inches(0.62), ico, LIGHT, size=20)
        txt(s, x + Inches(1.0), y + Inches(0.16), cw - Inches(1.15), Inches(0.4), t,
            size=14.5, bold=True, color=NAVY)
        txt(s, x + Inches(1.0), y + Inches(0.58), cw - Inches(1.15), Inches(0.9), desc,
            size=10.5, color=MUTED, line_spacing=1.05)


def s_lifecycle(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "The Product Lifecycle", kicker="5-STAGE JOURNEY", num=6, total=d.total)

    steps = [
        ("1", "RECEIVE", "Purchase receipts create stock batches with expiry dates", SKY),
        ("2", "STORE", "Batches assigned to locations; stock + value tracked live", INDIGO),
        ("3", "MONITOR", "Expiry alerts & risk scoring flag what needs attention", AMBER),
        ("4", "SELL", "Checkout auto-picks the earliest-expiring batch (FEFO)", GREEN),
        ("5", "ANALYZE", "Sales velocity, waste and margins feed the next cycle", VIOLET),
    ]
    x = Inches(0.7)
    w = Inches(2.3)
    gap = Inches(0.14)
    y = Inches(1.95)
    h = Inches(1.35)
    for num, t, desc, col in steps:
        box(s, x, y, w, h, fill=WHITE, line=BORDER, radius=0.1)
        box(s, x, y, w, Inches(0.09), fill=col, radius=0.5)
        cir = icon_badge(s, x + Inches(0.85), y + Inches(0.25), Inches(0.6), num, col, size=18)
        txt(s, x, y + Inches(1.02), w, Inches(0.35), t, size=16, bold=True, color=NAVY,
            align=PP_ALIGN.CENTER)
        if num != "5":
            box(s, x + w + Inches(0.03), y + Inches(0.4), gap - Inches(0.04), Inches(0.55),
                fill=MUTED, shape=MSO_SHAPE.RIGHT_ARROW)
        x += w + gap
    x = Inches(0.7)
    y2 = Inches(3.55)
    for num, t, desc, col in steps:
        txt(s, x, y2, w, Inches(0.9), desc, size=10.5, color=MUTED, align=PP_ALIGN.CENTER,
            line_spacing=1.08)
        x += w + gap

    box(s, Inches(0.7), Inches(4.85), Inches(12.0), Inches(1.7), fill=NAVY, radius=0.12)
    txt(s, Inches(1.1), Inches(5.02), Inches(11.2), Inches(0.4),
        "Why shelf life matters at every step", size=18, bold=True, color=WHITE)
    para_box(s, Inches(1.1), Inches(5.5), Inches(11.2), Inches(1.0), [
        "Every batch carries its own expiry date \u2014 decisions (pick, discount, dispose) are made on data, not guesswork.",
        ("FEFO keeps the freshest stock for customers while the Risk engine clears expiring stock before it turns to loss.", "b"),
    ], size=14, color=SLATE, gap=6, bullet=False)


def s_fefo(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "FEFO Picking Engine", kicker="FIRST-EXPIRED, FIRST-OUT", num=7, total=d.total)

    txt(s, Inches(0.85), Inches(1.6), Inches(5.5), Inches(0.5), "How it works",
        size=20, bold=True, color=NAVY)
    rules = [
        ("1", "Sort", "All available batches ordered by expiry date (earliest first).", SKY),
        ("2", "Exclude", "Expired batches are routed to waste, never to customers.", AMBER),
        ("3", "Allocate", "Requested quantity drawn from the oldest batch first.", INDIGO),
        ("4", "Top up", "When one batch runs out, the next-earliest fills the rest.", GREEN),
    ]
    y = Inches(2.2)
    for num, t, desc, col in rules:
        box(s, Inches(0.85), y, Inches(5.6), Inches(0.9), fill=WHITE, line=BORDER, radius=0.1)
        icon_badge(s, Inches(1.1), y + Inches(0.2), Inches(0.5), num, col, size=15)
        txt(s, Inches(1.8), y + Inches(0.15), Inches(1.7), Inches(0.6), t,
            size=15, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
        txt(s, Inches(3.5), y + Inches(0.15), Inches(2.8), Inches(0.6), desc,
            size=12, color=MUTED, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
        y += Inches(1.05)

    txt(s, Inches(7.0), Inches(1.6), Inches(5.4), Inches(0.5), "Why FEFO wins",
        size=20, bold=True, color=NAVY)
    para_box(s, Inches(7.0), Inches(2.2), Inches(5.5), Inches(3.6), [
        "Expiring stock sells first \u2014 shrink drops, margins hold.",
        "Fresh stock stays on the shelf for tomorrow's customers.",
        "Zero guesswork: the engine decides, operators execute.",
        "Consistent across sales, transfers and promotions.",
        ("No per-user judgement, no 'last-in' mistakes, no manual checks.", "lead"),
    ], size=15, gap=12, color=TEXT)

    box(s, Inches(0.85), Inches(6.3), Inches(11.6), Inches(0.65), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.2), Inches(6.38), Inches(11), Inches(0.5),
        "Applied automatically at every sale and location transfer \u2014 no manual first-out decisions, ever.",
        size=14.5, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_fefo_demo(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "FEFO in Action", kicker="WORKED EXAMPLE", num=8, total=d.total)

    txt(s, Inches(0.85), Inches(1.55), Inches(6.8), Inches(0.5),
        "A customer buys 6 units of Milk 1L. Three batches are in stock.", size=16,
        bold=True, color=NAVY)

    rows = [
        ("Batch", "Expiry (days)", "Stock", "Sale of 6"),
        ("B-01", "Left 1 day", "3", "3 \u2713 FEFO"),
        ("B-02", "Left 10 days", "5", "3 \u2713"),
        ("B-03", "Left 30 days", "8", "0 \u2717 kept"),
    ]
    tbl = s.shapes.add_table(len(rows), 4, Inches(0.85), Inches(2.15), Inches(6.6), Inches(1.9)).table
    tbl.columns[0].width = Inches(1.6)
    tbl.columns[1].width = Inches(1.9)
    tbl.columns[2].width = Inches(1.3)
    tbl.columns[3].width = Inches(1.8)
    tbl.first_row = False
    tbl.horz_banding = False
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = Pt(10)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(NAVY if r == 0 else (WHITE if r % 2 else LIGHT))
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.name = FONT
            run.font.size = Pt(13 if r == 0 else 12.5)
            run.font.bold = (r == 0)
            if r == 0:
                run.font.color.rgb = rgb(WHITE)
            elif c == 0:
                run.font.color.rgb = rgb(NAVY)
            else:
                run.font.color.rgb = rgb(TEXT)

    txt(s, Inches(0.85), Inches(4.35), Inches(6.6), Inches(0.9),
        "B-01 (left 1 day) is picked first. B-02 tops up the remaining 3 units. "
        "B-03 stays untouched for tomorrow.",
        size=13.5, color=MUTED, line_spacing=1.2)

    # pick-order arrow diagram
    txt(s, Inches(0.85), Inches(5.35), Inches(6.6), Inches(0.4),
        "Pick order", size=16, bold=True, color=NAVY)
    pl = [("B-01", "3", RED), ("B-02", "3", INDIGO), ("B-03", "0", MUTED)]
    x = Inches(0.85)
    pwb = Inches(1.6)
    for i, (b, q, col) in enumerate(pl):
        box(s, x, Inches(5.8), pwb, Inches(0.62), fill=col, radius=0.35)
        tf = box(s, x, Inches(5.8), pwb, Inches(0.62), fill=col, radius=0.35).text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        _zero_margins(tf)
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        rn = p.add_run()
        rn.text = f"{b}  {q}u"
        rn.font.name = FONT
        rn.font.size = Pt(13)
        rn.font.bold = True
        rn.font.color.rgb = rgb(WHITE)
        if i < 2:
            box(s, x + pwb + Inches(0.06), Inches(5.93), Inches(0.6), Inches(0.36),
                fill=MUTED, shape=MSO_SHAPE.RIGHT_ARROW)
        x += pwb + Inches(0.72)

    # right: outcome card
    box(s, Inches(7.95), Inches(2.15), Inches(4.55), Inches(4.35), fill=NAVY, radius=0.12)
    txt(s, Inches(8.35), Inches(2.45), Inches(3.8), Inches(0.4),
        "Your basket", size=13, bold=True, color=SLATE)
    txt(s, Inches(8.35), Inches(2.9), Inches(3.8), Inches(0.5),
        "6 units", size=28, bold=True, color=WHITE)
    txt(s, Inches(8.35), Inches(3.5), Inches(3.8), Inches(0.6),
        "3 \u00d7 B-01 (1 day)  +  3 \u00d7 B-02 (10 days)", size=13.5, color=SLATE,
        line_spacing=1.15)
    box(s, Inches(8.35), Inches(4.35), Inches(3.8), Inches(0.045), fill=SKY)
    txt(s, Inches(8.35), Inches(4.6), Inches(3.8), Inches(1.6),
        "Earliest-expiring stock always leaves the shelf first. The freshest "
        "batch is preserved for the next sale \u2014 automatically.",
        size=13, color=SLATE, line_spacing=1.25)

    txt(s, Inches(0.85), Inches(6.6), Inches(11.6), Inches(0.4),
        "Same logic powers transfers and promotions \u2014 one deterministic rule everywhere.",
        size=13.5, bold=True, color=INDIGO)


def s_risk(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Spoilage Risk Scoring", kicker="PREDICT BEFORE LOSS", num=9, total=d.total)

    txt(s, Inches(0.85), Inches(1.6), Inches(5.2), Inches(0.5), "Risk inputs per batch",
        size=20, bold=True, color=NAVY)
    para_box(s, Inches(0.85), Inches(2.15), Inches(5.3), Inches(3.0), [
        "Days to expiry  \u2014  weighted heaviest",
        "Perishability of the product type",
        "Storage condition  \u2014  chilled / ambient",
        "Sales velocity over the last 30 days",
        "Stock on hand vs. expected demand",
    ], size=15, gap=11, color=TEXT)

    txt(s, Inches(6.6), Inches(1.6), Inches(6), Inches(0.5), "The 0\u2013100 score",
        size=20, bold=True, color=NAVY)
    box(s, Inches(6.6), Inches(2.2), Inches(5.6), Inches(0.5), fill=WHITE, line=BORDER, radius=0.5)
    segs = [(0.20, GREEN, "LOW"), (0.25, AMBER, "MED"), (0.25, (0xEA, 0x58, 0x0C), "HIGH"),
            (0.30, RED, "CRIT")]
    gx = Inches(6.6)
    gw = Inches(5.6)
    for f, col, lab in segs:
        sw = Inches(gw.inches * f)
        chip(s, gx, Inches(2.2), sw, Inches(0.5), lab, col, radius=0.5, size=12)
        gx += sw
    txt(s, Inches(6.6), Inches(2.85), Inches(5.6), Inches(0.7),
        "Score = weighted blend; the engine explains the 'why' behind every number.",
        size=12.5, color=MUTED, line_spacing=1.15)

    para_box(s, Inches(6.6), Inches(3.7), Inches(5.6), Inches(1.9), [
        "Every batch is scored automatically on receipt and on each stock event.",
        "Score re-computed as expiry approaches and sales velocity changes.",
        ("The score feeds the Pricing module with a suggested discount %.", "b"),
    ], size=14, gap=10, color=TEXT)

    box(s, Inches(0.7), Inches(6.05), Inches(12.0), Inches(0.75), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.1), Inches(6.15), Inches(11.2), Inches(0.55),
        "Each batch gets a 0\u2013100 risk score. High and critical batches are flagged to operators in real time.",
        size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_risk_levels(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Risk Levels & Actions", kicker="WHAT EACH LEVEL MEANS", num=10, total=d.total)

    levels = [
        ("LOW", "0\u201320", "Plenty of shelf life.", "No action needed.", GREEN),
        ("MEDIUM", "21\u201345", "Moving slower than expected.", "Plan a promotion soon.", AMBER),
        ("HIGH", "46\u201370", "Expiring within days.", "Discount strongly now.", (0xEA, 0x58, 0x0C)),
        ("CRITICAL", "71\u2013100", "Imminent expiry loss.", "Clear or dispose immediately.", RED),
    ]
    y = Inches(1.75)
    for label, rng, desc, action, col in levels:
        box(s, Inches(0.85), y, Inches(11.6), Inches(1.12), fill=WHITE, line=BORDER, radius=0.12)
        box(s, Inches(0.85), y, Inches(0.14), Inches(1.12), fill=col, radius=0.5)
        chip(s, Inches(1.25), y + Inches(0.3), Inches(1.7), Inches(0.52), label, col,
             size=14, radius=0.5)
        txt(s, Inches(3.2), y + Inches(0.12), Inches(1.6), Inches(0.9), rng,
            size=20, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
        txt(s, Inches(5.0), y + Inches(0.12), Inches(4.6), Inches(0.9), desc,
            size=15, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
        chip(s, Inches(9.75), y + Inches(0.3), Inches(2.4), Inches(0.52), action, col,
             size=13, radius=0.5)
        y += Inches(1.3)

    txt(s, Inches(0.85), Inches(6.85), Inches(11.6), Inches(0.4),
        "Operators see a colour-coded risk column everywhere stock appears \u2014 dashboards, batches, checkout.",
        size=13.5, bold=True, color=INDIGO)


def s_pricing(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Dynamic Pricing & Promotions", kicker="CLEAR BEFORE IT EXPIRES", num=11,
              total=d.total)

    txt(s, Inches(0.85), Inches(1.6), Inches(5.4), Inches(0.5), "How a discount is recommended",
        size=20, bold=True, color=NAVY)
    para_box(s, Inches(0.85), Inches(2.15), Inches(5.5), Inches(2.9), [
        "Risk score \u2192 suggested discount % (risk-based table).",
        "Recommended price states the clear reason, e.g. \u201cexpires in 5 days\u201d.",
        "Manager drafts the promotion with the suggested value.",
        "Admin approves \u2192 promotion becomes Active \u2192 applied at checkout.",
    ], size=15, gap=11, color=TEXT)

    txt(s, Inches(6.9), Inches(1.6), Inches(5.4), Inches(0.5), "Risk maps to discount",
        size=20, bold=True, color=NAVY)
    table_rows = [
        ("Risk", "Suggested discount"),
        ("LOW", "0% \u2013 10%"),
        ("MEDIUM", "10% \u2013 20%"),
        ("HIGH", "20% \u2013 40%"),
        ("CRITICAL", "40% \u2013 60%"),
    ]
    tbl = s.shapes.add_table(len(table_rows), 2, Inches(6.9), Inches(2.15), Inches(5.5),
                             Inches(2.3)).table
    tbl.columns[0].width = Inches(2.2)
    tbl.columns[1].width = Inches(3.3)
    tbl.first_row = False
    tbl.horz_banding = False
    for r, row in enumerate(table_rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = Pt(10)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(NAVY if r == 0 else (WHITE if r % 2 else LIGHT))
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.name = FONT
            run.font.size = Pt(13 if r == 0 else 12.5)
            run.font.bold = (r == 0)
            run.font.color.rgb = rgb(WHITE if r == 0 else TEXT)

    txt(s, Inches(6.9), Inches(4.7), Inches(5.5), Inches(1.0),
        "Discounts are suggestions, not surprises: the operator always sees the "
        "product, batch, expiry window and reason before acting.",
        size=13.5, color=MUTED, line_spacing=1.2)

    # example pricing card
    box(s, Inches(0.85), Inches(5.2), Inches(11.6), Inches(1.35), fill=NAVY, radius=0.12)
    txt(s, Inches(1.25), Inches(5.45), Inches(1.8), Inches(0.5), "\u20B960.00", size=22,
        bold=True, color=(0x94, 0xA3, 0xB8))
    txt(s, Inches(3.05), Inches(5.45), Inches(1.6), Inches(0.5), "\u201345%", size=22,
        bold=True, color=rgb(GOLD))
    txt(s, Inches(4.65), Inches(5.45), Inches(1.8), Inches(0.5), "\u20B933.00", size=22,
        bold=True, color=rgb(GREEN))
    txt(s, Inches(1.25), Inches(6.0), Inches(8.9), Inches(0.45),
        "Milk 1L  \u2022  batch ML101  \u2022  expires in 5 days  \u2022  risk 80 CRITICAL  \u2192  recommend 45%",
        size=11.5, color=SLATE)


def s_promo_flow(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Promotion Approval Workflow", kicker="DRAFT \u2192 ACTIVE", num=12,
              total=d.total)

    txt(s, Inches(0.85), Inches(1.6), Inches(6), Inches(0.5), "Lifecycle of a promotion",
        size=20, bold=True, color=NAVY)
    wf = [
        ("Draft", "Manager creates from the suggested discount", INDIGO),
        ("Pending Approval", "Submitted for review, not yet live", AMBER),
        ("Active", "Applied automatically at checkout", GREEN),
        ("Rejected / Expired", "Never applied \u2014 reason recorded", RED),
    ]
    y = Inches(2.2)
    for label, desc, col in wf:
        box(s, Inches(0.85), y, Inches(5.6), Inches(0.85), fill=WHITE, line=BORDER, radius=0.1)
        chip(s, Inches(1.1), y + Inches(0.18), Inches(2.1), Inches(0.5), label, col,
             size=13, radius=0.4)
        txt(s, Inches(3.4), y + Inches(0.12), Inches(2.9), Inches(0.6), desc,
            size=12, color=MUTED, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.05)
        if label != "Rejected / Expired":
            box(s, Inches(0.85), y + Inches(0.85), Inches(5.6), Inches(0.045), fill=MUTED)
            box(s, Inches(0.85), y + Inches(0.8), Inches(0.28), Inches(0.28),
                fill=SKY, shape=MSO_SHAPE.DOWN_ARROW)
        y += Inches(1.1)

    txt(s, Inches(7.0), Inches(1.6), Inches(5.4), Inches(0.5), "Who can do what",
        size=20, bold=True, color=NAVY)
    rows = [
        ("Manager", "Draft & submit promotions", INDIGO),
        ("Admin", "Approve / reject", SKY),
        ("Admin", "Edit price, expiry & settings", VIOLET),
        ("Cashier", "Sell at active promo price", GREEN),
    ]
    y = Inches(2.2)
    for role, desc, col in rows:
        box(s, Inches(7.0), y, Inches(5.5), Inches(0.75), fill=WHITE, line=BORDER, radius=0.1)
        chip(s, Inches(7.25), y + Inches(0.15), Inches(1.5), Inches(0.45), role, col,
             size=12.5, radius=0.4)
        txt(s, Inches(9.0), y + Inches(0.12), Inches(3.3), Inches(0.5), desc,
            size=12.5, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(1.0)

    box(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.62), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.2), Inches(6.43), Inches(11), Inches(0.5),
        "State machine is enforced at the API level \u2014 only valid transitions are allowed.",
        size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_modules(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Platform at a Glance", kicker="12 API MODULES", num=13, total=d.total)

    rows = [
        ("Auth / Users", "Login, register, roles, 2FA, password & account security"),
        ("Products", "Catalogue, categories, brands, pricing profiles"),
        ("Suppliers", "Supplier master and purchase receipts"),
        ("Inventory", "Locations, stock levels, transfers, movements"),
        ("Batches", "Lot receipt, expiry tracking, batch lifecycle"),
        ("Expiry", "Expiry alerts and age analysis"),
        ("FEFO", "First-Expired-First-Out picking engine"),
        ("Risk", "Spoilage risk scoring for batches"),
        ("Pricing", "Recommended pricing, discounts and promotions"),
        ("Sales", "Checkout, invoices, payments (FEFO applied)"),
        ("Waste", "Waste recording and value tracking"),
        ("Alerts & Reports", "Notifications, dashboards & reporting"),
    ]
    tbl = s.shapes.add_table(len(rows) + 1, 2, Inches(0.85), Inches(1.7), Inches(11.6),
                             Inches(5.0)).table
    tbl.columns[0].width = Inches(2.6)
    tbl.columns[1].width = Inches(9.0)
    tbl.first_row = False
    tbl.horz_banding = False
    for c, h in enumerate(("Module", "Responsibility")):
        cell = tbl.cell(0, c)
        cell.margin_left = Pt(12)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = h
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = rgb(WHITE)
        run.font.name = FONT
    for r, (m, desc) in enumerate(rows, start=1):
        for c, val in enumerate((m, desc)):
            cell = tbl.cell(r, c)
            cell.margin_left = Pt(12)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(WHITE if r % 2 else LIGHT)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(12.5)
            run.font.bold = (c == 0)
            run.font.name = FONT
            run.font.color.rgb = rgb(NAVY if c == 0 else TEXT)


def s_architecture(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Architecture", kicker="HOW IT'S BUILT", num=14, total=d.total)

    layers = [
        ("Presentation", "HTML5  \u2022  CSS  \u2022  JavaScript  \u2022  Chart.js", SKY, "\U0001F5A5"),
        ("REST API", "12 Flask blueprints  \u2022  auth, products, inventory, sales, pricing, analytics...",
         INDIGO, "\U0001F50C"),
        ("Business Engines", "FEFO Engine  \u2022  Risk Scoring  \u2022  Pricing  \u2022  Sales Analysis  \u2022  Reports",
         VIOLET, "\u2699"),
        ("Data & Storage", "SQLAlchemy ORM  \u2192  SQLite (dev)  \u2022  MySQL  \u2022  PostgreSQL",
         (0x0E, 0x74, 0x92), "\U0001F5C4"),
    ]
    y = Inches(1.65)
    hh = Inches(1.12)
    for name, desc, col, ico in layers:
        box(s, Inches(0.85), y, Inches(8.3), hh, fill=WHITE, line=BORDER, radius=0.12)
        box(s, Inches(0.85), y, Inches(0.14), hh, fill=col, radius=0.5)
        icon_badge(s, Inches(1.2), y + Inches(0.28), Inches(0.56), ico, col, size=18)
        txt(s, Inches(2.0), y + Inches(0.14), Inches(6.9), Inches(0.4), name,
            size=16, bold=True, color=NAVY)
        txt(s, Inches(2.0), y + Inches(0.55), Inches(6.9), Inches(0.45), desc,
            size=11.5, color=MUTED)
        if name != "Data & Storage":
            box(s, Inches(9.3), y + Inches(0.34), Inches(3.0), Inches(0.45),
                fill=MUTED, shape=MSO_SHAPE.STRIPED_RIGHT_ARROW)
        y += hh + Inches(0.18)

    box(s, Inches(0.85), Inches(6.15), Inches(11.6), Inches(0.62), fill=NAVY, radius=0.5)
    txt(s, Inches(1.15), Inches(6.23), Inches(11), Inches(0.5),
        "Cross-cutting:  bcrypt hashing  \u2022  TOTP 2FA  \u2022  account lockout  \u2022  rate limits  \u2022  audit logs  \u2022  secure sessions",
        size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_datamodel(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Data Model", kicker="NORMALIZED SCHEMA", num=15, total=d.total)

    rows = [
        ("Accounts & Security", "users, roles, login_logs, settings",
         "Logins, RBAC, audit trail, system config"),
        ("Catalogue", "categories, products, suppliers", "SKUs, packaging, sourcing master"),
        ("Stock & Movement", "locations, inventory_ledger, inventory_batches",
         "On-hand quantity, movement history, lot control"),
        ("Freshness", "expiry_alerts, waste_records", "Expiry watch, disposal tracking"),
        ("Pricing", "promotions, promo_items", "Discounts + approval workflow"),
        ("Commerce", "sales, sale_items, payments, expenses",
         "Checkout, totals, payments, running costs"),
    ]
    tbl = s.shapes.add_table(len(rows) + 1, 3, Inches(0.85), Inches(1.7), Inches(11.6),
                             Inches(4.35)).table
    tbl.columns[0].width = Inches(3.0)
    tbl.columns[1].width = Inches(4.2)
    tbl.columns[2].width = Inches(4.4)
    tbl.first_row = False
    tbl.horz_banding = False
    for c, h in enumerate(("Domain", "Tables", "Responsibility")):
        cell = tbl.cell(0, c)
        cell.margin_left = Pt(12)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = h
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = rgb(WHITE)
        run.font.name = FONT
    for r, (dom, tab, resp) in enumerate(rows, start=1):
        for c, val in enumerate((dom, tab, resp)):
            cell = tbl.cell(r, c)
            cell.margin_left = Pt(12)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(WHITE if r % 2 else LIGHT)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(12.5)
            run.font.bold = (c == 0)
            run.font.name = FONT
            run.font.color.rgb = rgb(NAVY if c == 0 else TEXT)

    box(s, Inches(0.85), Inches(6.25), Inches(11.6), Inches(0.62), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.2), Inches(6.33), Inches(11), Inches(0.5),
        "SQLite for zero-setup development; switch to MySQL / PostgreSQL via DATABASE_URL.",
        size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_security(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Security by Default", kicker="PROTECTION BUILT-IN", num=16, total=d.total)

    items = [
        ("\U0001F510", "bcrypt Password Hashing", "Adaptive hashing with per-user salt"),
        ("\U0001F5DD", "2FA (TOTP)", "Six-digit codes from any authenticator app"),
        ("\u26D4", "Account Lockout", "5 failed logins lock for 15 minutes"),
        ("\U0001F6A6", "IP Rate Limiting", "10 login attempts per 5-minute window"),
        ("\U0001F6E1", "Password Policy", "8+ chars, complexity + common-password check"),
        ("\U0001F4DC", "Login Audit Trail", "Every success/failure with IP & user-agent"),
        ("\U0001F36A", "Secure Sessions", "HttpOnly, SameSite, configurable Secure flag"),
        ("\U0001F517", "Signed Reset Tokens", "30-minute, single-use password resets"),
    ]
    cols = 4
    rows = 2
    cw = Inches(2.95)
    ch = Inches(1.95)
    gx = Inches(0.22)
    gy = Inches(0.2)
    x0 = Inches(0.55)
    y0 = Inches(1.65)
    for i, (ico, t, desc) in enumerate(items):
        r = i // cols
        c = i % cols
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        box(s, x, y, cw, ch, fill=WHITE, line=BORDER, radius=0.1)
        icon_badge(s, x + Inches(0.25), y + Inches(0.3), Inches(0.72), ico, INDIGO, size=24)
        txt(s, x + Inches(1.2), y + Inches(0.25), cw - Inches(1.4), Inches(0.7), t,
            size=14.5, bold=True, color=NAVY, line_spacing=1.05)
        txt(s, x + Inches(1.2), y + Inches(0.95), cw - Inches(1.4), Inches(0.9), desc,
            size=11, color=MUTED, line_spacing=1.1)

    txt(s, Inches(0.85), Inches(6.0), Inches(11.6), Inches(0.5),
        "Hardening verified by an automated security test suite (33 scenarios: lockout, 2FA, resets, rate limiting).",
        size=14.5, bold=True, color=INDIGO)


def s_authflow(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Authentication & Sessions", kicker="FROM LOGIN TO AUDIT", num=17,
              total=d.total)

    steps = [
        ("Login", "Credentials checked against bcrypt hash", INDIGO),
        ("2FA (optional)", "TOTP code when enabled", SKY),
        ("Secure Session", "HttpOnly + SameSite + 1h lifetime", GREEN),
        ("Logout / Audit", "Every event logged with IP + user-agent", MUTED),
    ]
    x = Inches(0.85)
    w = Inches(2.55)
    y = Inches(1.8)
    for i, (t, desc, col) in enumerate(steps):
        box(s, x, y, w, Inches(1.5), fill=WHITE, line=BORDER, radius=0.12)
        box(s, x, y, w, Inches(0.09), fill=col, radius=0.5)
        txt(s, x + Inches(0.2), y + Inches(0.25), w - Inches(0.4), Inches(0.4), t,
            size=15.5, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s, x + Inches(0.2), y + Inches(0.72), w - Inches(0.4), Inches(0.7), desc,
            size=11, color=MUTED, align=PP_ALIGN.CENTER, line_spacing=1.1)
        if i < 3:
            box(s, x + w + Inches(0.06), y + Inches(0.55), Inches(0.62), Inches(0.4),
                fill=MUTED, shape=MSO_SHAPE.RIGHT_ARROW)
        x += w + Inches(0.75)

    txt(s, Inches(0.85), Inches(3.75), Inches(5.6), Inches(0.5), "Lockout & rate limiting",
        size=19, bold=True, color=NAVY)
    para_box(s, Inches(0.85), Inches(4.3), Inches(5.6), Inches(1.7), [
        "5 failed passwords \u2192 account locked for 15 minutes.",
        "10 attempts per IP in 5 minutes \u2192 temporarily blocked.",
        "Failed attempts cleared on successful login.",
    ], size=14.5, gap=9, color=TEXT)

    txt(s, Inches(6.9), Inches(3.75), Inches(5.6), Inches(0.5), "Password & reset",
        size=19, bold=True, color=NAVY)
    para_box(s, Inches(6.9), Inches(4.3), Inches(5.6), Inches(1.7), [
        "Policy: 8+ characters, complexity + common-password block.",
        "Signed reset tokens \u2014 expire in 30 minutes, single use.",
        "First login after reset / admin setup forces a new password.",
    ], size=14.5, gap=9, color=TEXT)

    box(s, Inches(0.85), Inches(6.2), Inches(11.6), Inches(0.62), fill=NAVY, radius=0.5)
    txt(s, Inches(1.2), Inches(6.28), Inches(11), Inches(0.5),
        "Login history reviewable from the Settings page \u2014 full audit trail for every account.",
        size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_roles(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Roles & Access", kicker="RBAC PERMISSIONS", num=18, total=d.total)

    cap_roles = [
        ("View dashboards & analytics", True, True, True, True, True, True),
        ("Process sales & checkout", True, True, True, True, True, False),
        ("Record wastage & customers", True, True, True, False, True, False),
        ("View inventory, expiry & risk", True, True, True, True, True, True),
        ("Edit products, suppliers & batches", True, True, False, False, False, False),
        ("Create & submit promotions", True, True, False, False, False, False),
        ("Manage users & approve promotions", True, True, False, False, False, False),
        ("System configuration & full admin", True, False, False, False, False, False),
    ]
    tbl = s.shapes.add_table(len(cap_roles) + 1, 7, Inches(0.85), Inches(1.7), Inches(11.6),
                             Inches(5.0)).table
    widths = [Inches(5.0), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1),
              Inches(1.1)]
    for i, wv in enumerate(widths):
        tbl.columns[i].width = wv
    tbl.first_row = False
    tbl.horz_banding = False
    headers = ["Capability", "Admin", "Manager", "Biller", "Cashier", "Staff", "User"]
    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = h
        run.font.bold = True
        run.font.size = Pt(11.5)
        run.font.color.rgb = rgb(WHITE)
        run.font.name = FONT
        cell.margin_left = Pt(8)
    for r, (cap, admin, mgr, bil, cash, stf, usr) in enumerate(cap_roles, start=1):
        vals = [cap, ("\u2713" if admin else "\u2014"), ("\u2713" if mgr else "\u2014"),
                ("\u2713" if bil else "\u2014"), ("\u2713" if cash else "\u2014"),
                ("\u2713" if stf else "\u2014"), ("\u2713" if usr else "\u2014")]
        for cc, val in enumerate(vals):
            cell = tbl.cell(r, cc)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(WHITE if r % 2 else LIGHT)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(12)
            run.font.bold = (cc == 0) or (cc > 0 and val == "\u2713")
            run.font.name = FONT
            run.font.color.rgb = rgb(NAVY if cc == 0 else (GREEN if val == "\u2713" else MUTED))
            cell.margin_left = Pt(8)

    txt(s, Inches(0.85), Inches(6.85), Inches(11.6), Inches(0.4),
        "Roles are hierarchical \u2014 ADMIN > MANAGER > BILLER > CASHIER > STAFF > USER with endpoint-level enforcement.",
        size=12.5, color=MUTED)


def s_techstack(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Technology Stack", kicker="BUILDING BLOCKS", num=19, total=d.total)

    rows = [
        ("Backend", "Python 3 + Flask + SQLAlchemy", "Lightweight, modular blueprints, REST JSON API"),
        ("Frontend", "HTML5 / CSS / JavaScript + Chart.js", "Server-rendered pages, live dashboard charts"),
        ("Database", "SQLite \u2192 MySQL \u2192 PostgreSQL", "SQLite for zero-setup dev; production switch via DATABASE_URL"),
        ("Security", "Flask-Login, bcrypt, itsdangerous", "Sessions, TOTP 2FA, signed reset tokens"),
        ("Logic", "Custom engines (FEFO, risk, pricing)", "Pure-Python, unit-tested decision logic"),
        ("Quality", "Standalone test suites + smoke tests", "35 security scenarios + functional smoke coverage"),
    ]
    tbl = s.shapes.add_table(len(rows) + 1, 3, Inches(0.85), Inches(1.7), Inches(11.6),
                             Inches(4.4)).table
    tbl.columns[0].width = Inches(2.3)
    tbl.columns[1].width = Inches(4.6)
    tbl.columns[2].width = Inches(4.7)
    tbl.first_row = False
    tbl.horz_banding = False
    for c, h in enumerate(("Layer", "Technology", "Why it was chosen")):
        cell = tbl.cell(0, c)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(NAVY)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = h
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = rgb(WHITE)
        run.font.name = FONT
        cell.margin_left = Pt(8)
    for r, (layer, tech, why) in enumerate(rows, start=1):
        for c, val in enumerate((layer, tech, why)):
            cell = tbl.cell(r, c)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(WHITE if r % 2 else LIGHT)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(12.5)
            run.font.bold = (c == 0)
            run.font.name = FONT
            run.font.color.rgb = rgb(NAVY if c == 0 else TEXT)
            cell.margin_left = Pt(8)

    box(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.62), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.15), Inches(6.43), Inches(11), Inches(0.5),
        "Fully self-hosted \u2014 no external SaaS required; pandas powers sales analytics.",
        size=13.5, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_demo(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Live Demo & Quick Start", kicker="TRY IT YOURSELF", num=20, total=d.total)

    term = box(s, Inches(0.85), Inches(1.7), Inches(6.2), Inches(4.75), fill=NAVY, radius=0.1)
    txt(s, Inches(1.1), Inches(1.95), Inches(5.4), Inches(0.4),
        "Terminal", size=12, bold=True, color=SLATE)
    cmds = [
        ("$ cd SmartShelf", False),
        ("$ .venv\\Scripts\\python.exe -m flask --app app init-db", False),
        ("$ .venv\\Scripts\\python.exe -m flask --app app seed", False),
        ("$ .venv\\Scripts\\python.exe -m flask --app app run", False),
        ("", False),
        ("  * Running on http://127.0.0.1:5000", True),
        ("  * Open /login in your browser", True),
    ]
    tb = txt(s, Inches(0.95), Inches(2.4), Inches(5.9), Inches(4.0), [], line_spacing=1.25)
    tf = tb.text_frame
    tf.clear()
    for i, (cmd, isout) in enumerate(cmds):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = cmd
        run.font.name = MONO
        run.font.size = Pt(14)
        run.font.bold = isout
        run.font.color.rgb = rgb((0x8B, 0xB8, 0xFF))

    txt(s, Inches(7.35), Inches(1.7), Inches(5.1), Inches(0.5), "Try these first",
        size=20, bold=True, color=NAVY)
    tries = [
        ("\U0001F6E1", "Enable 2FA", "Settings \u2192 Security \u2192 scan the QR with any authenticator app"),
        ("\U0001F504", "Run a sale", "Watch checkout auto-pick the earliest-expiring batch"),
        ("\U0001F4B0", "Check pricing", "Risk-driven discount suggestions with clear reasons"),
        ("\U0001F4CA", "Open analytics", "Velocity, KPIs and the expiry health board"),
    ]
    y = Inches(2.25)
    for ico, t, desc in tries:
        box(s, Inches(7.35), y, Inches(5.1), Inches(0.98), fill=WHITE, line=BORDER, radius=0.12)
        icon_badge(s, Inches(7.6), y + Inches(0.2), Inches(0.58), ico, LIGHT, size=20)
        txt(s, Inches(8.35), y + Inches(0.12), Inches(3.9), Inches(0.4), t,
            size=14.5, bold=True, color=NAVY)
        txt(s, Inches(8.35), y + Inches(0.48), Inches(3.9), Inches(0.45), desc,
            size=11, color=MUTED, line_spacing=1.05)
        y += Inches(1.12)

    txt(s, Inches(0.85), Inches(6.7), Inches(11.6), Inches(0.4),
        "Everything above is free of external SaaS \u2014 fully self-hosted.", size=13,
        color=MUTED)


def s_logins(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Demo Accounts", kicker="READY TO LOG IN", num=21, total=d.total)

    logins = [
        ("Admin", "admin", "admin123", "Everything: users, pricing, system config", INDIGO),
        ("Manager", "manager", "manager123", "Operations: products, batches, promos", SKY),
        ("Cashier", "cashier", "cashier123", "Front desk: checkout & sales only", GREEN),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for role, u, pw, scope, col in logins:
        card = box(s, x, Inches(1.8), w, Inches(4.2), fill=WHITE, line=BORDER, radius=0.1)
        box(s, x, Inches(1.8), w, Inches(0.14), fill=col, radius=0.5)
        chip(s, x + Inches(0.35), Inches(2.15), Inches(1.5), Inches(0.5), role, col,
             size=13, radius=0.4)
        txt(s, x + Inches(0.35), Inches(2.95), w - Inches(0.7), Inches(0.4),
            "username", size=11, bold=True, color=MUTED)
        txt(s, x + Inches(0.35), Inches(3.3), w - Inches(0.7), Inches(0.5), u,
            size=20, bold=True, color=NAVY, font=MONO)
        txt(s, x + Inches(0.35), Inches(4.0), w - Inches(0.7), Inches(0.4),
            "password", size=11, bold=True, color=MUTED)
        txt(s, x + Inches(0.35), Inches(4.35), w - Inches(0.7), Inches(0.5), pw,
            size=20, bold=True, color=NAVY, font=MONO)
        txt(s, x + Inches(0.35), Inches(5.05), w - Inches(0.7), Inches(0.8), scope,
            size=12.5, color=TEXT, line_spacing=1.15)
        x += w + Inches(0.42)

    txt(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.5),
        "Tip: log in with the Admin account and enable 2FA in Settings to watch the full security flow.",
        size=14, bold=True, color=INDIGO)


def s_quality(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Quality & Reliability", kicker="SHIPPED, NOT PROTOTYPED", num=22,
              total=d.total)

    stats = [
        ("30", "automated security test scenarios passed", INDIGO),
        ("102", "registered API + page routes", SKY),
        ("19", "database tables in a normalized schema", GREEN),
        ("3", "database backends supported (SQLite/MySQL/PostgreSQL)", VIOLET),
    ]
    x = Inches(0.85)
    w = Inches(2.75)
    for val, desc, col in stats:
        box(s, x, Inches(1.7), w, Inches(2.5), fill=WHITE, line=BORDER, radius=0.1)
        txt(s, x + Inches(0.3), Inches(1.95), w - Inches(0.6), Inches(0.8), val,
            size=40, bold=True, color=col)
        txt(s, x + Inches(0.3), Inches(2.9), w - Inches(0.6), Inches(1.2), desc,
            size=13.5, color=TEXT, line_spacing=1.15)
        x += w + Inches(0.42)

    txt(s, Inches(0.85), Inches(4.6), Inches(11.6), Inches(0.5), "What that means you can trust",
        size=20, bold=True, color=NAVY)
    para_box(s, Inches(0.85), Inches(5.15), Inches(11.6), Inches(1.6), [
        "FEFO engine + risk scoring unit tests (ordering, cross-batch allocation, thresholds).",
        "End-to-end smoke test: login \u2192 receive \u2192 sale (FEFO allocation) \u2192 reports \u2192 pages.",
        "Security suite: lockout, rate limiting, password policy, 2FA enable/verify/disable, reset tokens, audit logs.",
        ("Schema ships in SQL, seeded demo data included, plus a /api/health endpoint for uptime checks.", "b"),
    ], size=14, gap=9, color=TEXT)


def s_coverage(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Test Coverage", kicker="HOW IT'S VERIFIED", num=23, total=d.total)

    suites = [
        ("Security", "30 scenarios", [
            "Lockout after 5 failed logins",
            "IP rate limiting (10 per 5 min)",
            "Password policy & common passwords",
            "2FA enable / verify / disable",
            "Signed reset tokens + single use",
            "Audit logging for every login",
        ], INDIGO),
        ("Functional", "End-to-end smoke", [
            "Login and session creation",
            "Inventory receipt \u2192 batch created",
            "Sale with automatic FEFO allocation",
            "Pricing / risk endpoints live",
            "All 17 pages render (200 OK)",
            "Reports workbook generation",
        ], SKY),
        ("Unit", "Engines", [
            "FEFO ordering by expiry date",
            "Cross-batch allocation correctness",
            "Insufficient stock raises cleanly",
            "Risk high when expired",
            "Risk low when fresh & selling",
            "Threshold boundaries verified",
        ], GREEN),
    ]
    x = Inches(0.85)
    w = Inches(3.75)
    for name, tag, tests, col in suites:
        box(s, x, Inches(1.7), w, Inches(4.55), fill=WHITE, line=BORDER, radius=0.1)
        box(s, x, Inches(1.7), w, Inches(0.14), fill=col, radius=0.5)
        txt(s, x + Inches(0.3), Inches(2.0), w - Inches(0.6), Inches(0.5), name,
            size=19, bold=True, color=NAVY)
        chip(s, x + Inches(0.3), Inches(2.55), Inches(1.8), Inches(0.42), tag, col,
             size=12, radius=0.4)
        para_box(s, x + Inches(0.3), Inches(3.2), w - Inches(0.6), Inches(2.9), tests,
                 size=12, gap=7, color=TEXT, line_spacing=1.12)
        x += w + Inches(0.42)

    box(s, Inches(0.85), Inches(6.45), Inches(11.6), Inches(0.52), fill=NAVY, radius=0.5)
    txt(s, Inches(1.2), Inches(6.53), Inches(11), Inches(0.4),
        "Run anytime:  python tests\\test_security.py   python tests\\smoke_test.py   python tests\\test_engines.py",
        size=13, bold=True, color=WHITE, font=MONO, anchor=MSO_ANCHOR.MIDDLE)


def s_roadmap(d):
    s = d.blank()
    d.background(s, LIGHT)
    title_bar(s, "Roadmap", kicker="NEXT HORIZONS", num=24, total=d.total)

    items = [
        ("\U0001F4D9", "POS & Barcode", "Barcode/SKU scanners, receipt printing & offline-friendly checkout"),
        ("\U0001F9E0", "Demand Forecasting", "ML-driven reorder points & replenishment suggestions"),
        ("\U0001F5FA", "Multi-Warehouse", "Distributed locations, cross-warehouse FEFO transfers"),
        ("\U0001F4F1", "Mobile & Reports", "Manager dashboards and auto-generated report exports"),
        ("\u2601", "Production Hardening", "Docker packaging, HTTPS reverse proxy, email delivery for resets"),
    ]
    x = Inches(0.85)
    w = Inches(2.3)
    gap = Inches(0.15)
    y = Inches(1.8)
    h = Inches(4.1)
    for i, (ico, t, desc) in enumerate(items):
        box(s, x, y, w, h, fill=WHITE, line=BORDER, radius=0.1)
        icon_badge(s, x + (w - Inches(0.9)) / 2, y + Inches(0.4), Inches(0.9), ico,
                   INDIGO, size=26)
        txt(s, x + Inches(0.15), y + Inches(1.55), w - Inches(0.3), Inches(0.9), t,
            size=15, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        txt(s, x + Inches(0.15), y + Inches(2.35), w - Inches(0.3), Inches(1.6), desc,
            size=11, color=MUTED, align=PP_ALIGN.CENTER, line_spacing=1.12)
        x += w + gap

    box(s, Inches(0.85), Inches(6.2), Inches(11.6), Inches(0.7), fill=INDIGO, radius=0.5)
    txt(s, Inches(1.2), Inches(6.3), Inches(11), Inches(0.5),
        "Phase 1 (done): complete inventory\u2013sales platform with FEFO, risk, pricing & security.",
        size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def s_close(d):
    s = d.blank()
    d.background(s, NAVY)
    box(s, Inches(-2.0), Inches(-1.5), Inches(8.0), Inches(5.5), fill=NAVY2, shape=MSO_SHAPE.OVAL)
    box(s, Inches(10.6), Inches(4.9), Inches(4.4), Inches(4.4), fill=INDIGO, shape=MSO_SHAPE.OVAL)
    box(s, Inches(11.8), Inches(-1.4), Inches(2.8), Inches(2.8), fill=SKY, shape=MSO_SHAPE.OVAL)

    txt(s, Inches(1.0), Inches(2.3), Inches(11.3), Inches(1.2),
        "Thank You", size=48, bold=True, color=WHITE)
    txt(s, Inches(1.0), Inches(3.4), Inches(11.3), Inches(0.8),
        "SmartShelf \u2014 Inventory Intelligence for Perishable Retail", size=22, color=SLATE)
    txt(s, Inches(1.0), Inches(4.15), Inches(11.3), Inches(0.5),
        "FEFO  \u2022  Risk Scoring  \u2022  Dynamic Pricing  \u2022  Analytics  \u2022  Secure by Default",
        size=16, color=SKY)
    box(s, Inches(1.0), Inches(5.1), Inches(3.7), Inches(0.06), fill=SKY)
    txt(s, Inches(1.0), Inches(5.45), Inches(11.3), Inches(0.5),
        "Questions? Let's walk through the live demo.", size=15, color=MUTED)
    footer(s, d.total, d.total, dark=True)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(output_path):
    d = Deck()
    s_title(d)
    s_agenda(d)
    s_problem(d)
    s_solution(d)
    s_features(d)
    s_lifecycle(d)
    s_fefo(d)
    s_fefo_demo(d)
    s_risk(d)
    s_risk_levels(d)
    s_pricing(d)
    s_promo_flow(d)
    s_modules(d)
    s_architecture(d)
    s_datamodel(d)
    s_security(d)
    s_authflow(d)
    s_roles(d)
    s_techstack(d)
    s_demo(d)
    s_logins(d)
    s_quality(d)
    s_coverage(d)
    s_roadmap(d)
    s_close(d)
    d.prs.save(output_path)
    print(f"Saved {output_path} with {len(d.prs.slides._sldIdLst)} slides.")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(base, "SmartShelf_Presentation.pptx")
    build(out)