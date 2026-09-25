"""Generate the SmartShelf reference architecture + workflow diagram (PNG).

Output: docs/assets/architecture.png
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets", "architecture.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

FONT_DIR = r"C:\Windows\Fonts"


def _font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        try:
            return ImageFont.truetype(os.path.join(FONT_DIR, name.replace("segoe", "arial")), size)
        except OSError:
            return ImageFont.load_default(size)


BOLD55 = _font("segoeuib.ttf", 55)
BOLD32 = _font("segoeuib.ttf", 32)
BOLD24 = _font("segoeuib.ttf", 24)
BOLD22 = _font("segoeuib.ttf", 22)
BOLD18 = _font("segoeuib.ttf", 18)
REG26 = _font("segoeui.ttf", 26)
REG22 = _font("segoeui.ttf", 22)
REG20 = _font("segoeui.ttf", 20)
REG18 = _font("segoeui.ttf", 18)
REG16 = _font("segoeui.ttf", 16)

NAVY = (11, 36, 71)
BLUE = (11, 95, 165)
SKY = (234, 242, 251)
TEAL = (14, 131, 136)
GREEN_BG = (231, 246, 242)
AMBER_BG = (255, 247, 230)
RED_BG = (253, 235, 237)
GREY = (80, 90, 110)
DARK = (51, 65, 85)
WHITE = (255, 255, 255)
LINE = (40, 60, 90)

W, H = 2500, 1500
img = Image.new("RGB", (W, H), WHITE)
d = ImageDraw.Draw(img)


def rbox(x, y, w, h, r, fill, outline, width=2):
    d.rounded_rectangle((x, y, x + w, y + h), radius=r, fill=fill, outline=outline, width=width)


def arrow_down(x, y1, y2, color=BLUE, width=5, size=14):
    d.line((x, y1, x, y2 - size), fill=color, width=width)
    d.polygon((x - size, y2 - size, x + size, y2 - size, x, y2), fill=color)


def wrap(text, font, maxw):
    words = text.split()
    out, cur = [], []
    for w in words:
        probe = " ".join(cur + [w])
        if d.textlength(probe, font=font) <= maxw or not cur:
            cur.append(w)
        else:
            out.append(" ".join(cur))
            cur = [w]
    if cur:
        out.append(" ".join(cur))
    return out


def block(x, y, text, font, maxw, fill, lh=1.18, halign="left"):
    lines = wrap(text, font, maxw)
    yy = y
    for ln in lines:
        w_ = d.textlength(ln, font=font)
        xx = x if halign == "left" else (x + maxw / 2 - w_ / 2)
        d.text((xx, yy), ln, font=font, fill=fill)
        yy += int(font.size * lh)
    return yy


# ---- Header ----
d.text((60, 34), "SmartShelf - Smart Retail Inventory & FEFO Management System", font=BOLD55, fill=NAVY)
d.text((60, 108), "Reference Architecture & End-to-End Working Flow", font=REG26, fill=BLUE)
d.rectangle((60, 158, 2440, 163), fill=LINE)
d.rectangle((60, 163, 2440, 168), fill=TEAL)

# ---- Panel A: architecture ----
PA_X, PA_W = 80, 1250
d.text((PA_X, 200), "HIGH-LEVEL ARCHITECTURE (LAYERED)", font=BOLD32, fill=NAVY)

layers = [
    ("1. PRESENTATION LAYER (/presentation)",
     "Jinja2 HTML templates (presentation/templates), CSS & vanilla JS (presentation/static), "
     "and page routes (presentation/routes). Serves Dashboard, Products, Suppliers, Inventory, "
     "Batches, Expiry, FEFO, Pricing, Risk, Sales, Analytics, Alerts, Waste, Reports, Settings."),
    ("2. APPLICATION / SERVICE LAYER (/services)",
     "Flask blueprints under /api (services/api) + domain services: stock_service, "
     "expiry_service, alert_service, notification_service, waste_service, audit_service. "
     "Enforces RBAC (@at_least, @roles_required) and business transaction orchestration."),
    ("3. INTELLIGENCE / ENGINE LAYER (/engines)",
     "Autonomous core algorithmic decision engines: fefo_engine (batch prioritization & "
     "allocation), risk_engine (multi-factor 0-100 spoilage scoring), pricing_engine "
     "(dynamic markdown pricing + reason generator), and demand_engine (velocity & forecasting)."),
    ("4. DATA LAYER (/data)",
     "SQLAlchemy ORM models (data/models: product, supplier, batch, inventory, sales, "
     "discount, alert, waste, login, user) + shared enums. SQLite for dev; MySQL 8 / "
     "PostgreSQL for production. DDL in data/schema.sql, seed in data/seed_data.sql."),
    ("5. ANALYTICS & OUTCOME LAYER (/analytics)",
     "Outcome metrics, KPI aggregations, and multi-dimensional reporting: sales_report, "
     "inventory_report, expiry_report, discount_report, waste_report (revenue recovery & "
     "savings realization), and system health probes (/api/health)."),
]

ly = 250
for title, body in layers:
    rbox(PA_X, ly, PA_W, 118, 14, SKY, BLUE, 3)
    d.text((PA_X + 20, ly + 12), title, font=BOLD24, fill=BLUE)
    block(PA_X + 20, ly + 46, body, REG18, PA_W - 40, DARK)
    ly += 118 + 26
    if title != layers[-1][0]:
        arrow_down(PA_X + PA_W // 2, ly - 24, ly + 2)

# side boxes
sb_w, sb_y, sb_h = (PA_W - 24) // 2, 848, 128
rbox(PA_X, sb_y, sb_w, sb_h, 14, AMBER_BG, (200, 150, 40), 3)
d.text((PA_X + 16, sb_y + 10), "SECURITY & CROSS-CUTTING", font=BOLD18, fill=(160, 110, 10))
block(PA_X + 16, sb_y + 44,
      "bcrypt hashing \u00b7 strong session protection (IP + UA) \u00b7 TOTP 2FA \u00b7 "
      "lockout & rate limiting \u00b7 audit log on every mutation",
      REG16, sb_w - 32, DARK)
rbox(PA_X + sb_w + 24, sb_y, sb_w, sb_h, 14, RED_BG, (196, 69, 54), 3)
d.text((PA_X + sb_w + 40, sb_y + 10), "CORE ENGINES", font=BOLD18, fill=(170, 40, 30))
block(PA_X + sb_w + 40, sb_y + 44,
      "FEFO allocation \u00b7 spoilage risk 0-100 \u00b7 dynamic pricing + reason \u00b7 "
      "sales velocity \u00b7 simple forecast \u00b7 expiry classification",
      REG16, sb_w - 32, DARK)

d.text((PA_X, sb_y + sb_h + 26), "Concurrency: one guarded atomic UPDATE (WHERE quantity >= ?) "
       "per FEFO deduction prevents overselling under parallel sales.",
      font=REG20, fill=GREY)

# ---- Panel B: workflow ----
PB_X, PB_W = 1380, 1100
d.text((PB_X, 200), "END-TO-END WORKING FLOW", font=BOLD32, fill=NAVY)

steps = [
    ("1  LOGIN & ACCESS CONTROL",
     "User authenticates (bcrypt verify); session bound to IP + user-agent; role returned: "
     "ADMIN / MANAGER / BILLER / CASHIER / STAFF / USER. Optional TOTP 2FA. Every login recorded in history."),
    ("2  MASTER DATA",
     "Admin creates categories, brands, products (SKU, unit price, reorder level) and "
     "registers suppliers before any stock can move."),
    ("3  STOCK IN (PURCHASE)",
     "Manager raises a PO against a supplier. Receiving calls add_stock: creates or tops up "
     "a batch (code + expiry), appends an IN inventory movement, raises product stock."),
    ("4  CLASSIFY & SCORE",
     "Expiry scan tags each batch OK / EXPIRING_SOON / EXPIRED. Risk engine scores every "
     "in-stock batch 0-100 from days-to-expiry plus sales velocity."),
    ("5  SELL FEFO-FIRST",
     "Sales API calls deduct_stock: atomic guarded UPDATE picks the earliest-expiry batch "
     "first. SaleItem links the exact batch sold; an OUT movement is recorded; invoice issued."),
    ("6  PRICE SMARTLY",
     "Pricing engine suggests a % discount and a plain-language reason for at-risk batches. "
     "Manager files a promotion -> SUBMIT -> ADMIN approves/rejects -> ACTIVE/INACTIVE."),
    ("7  STAY ALERT",
     "Alert engine raises low-stock, near-expiry, high-risk and expired notifications; unread "
     "badge on every page. Wastage recorded to recover cost and estimate savings."),
    ("8  ANALYZE & REPORT",
     "Dashboard KPIs, velocity, demand analysis, forecast, and sales / inventory / expiry / "
     "discount / waste / performance / audit reports plus a /api/health endpoint."),
]

sy = 250
for num, (title, body) in enumerate(steps):
    rbox(PB_X, sy, PB_W, 132, 14, GREEN_BG, TEAL, 3)
    d.text((PB_X + 18, sy + 10), title, font=BOLD22, fill=TEAL)
    block(PB_X + 18, sy + 50, body, REG16, PB_W - 36, DARK)
    sy += 132 + 22
    if num != len(steps) - 1:
        arrow_down(PB_X + PB_W // 2, sy - 20, sy + 2, color=TEAL)

# ---- Bottom banner ----
rbox(60, 1416, 2380, 46, 12, NAVY, BLUE, 3)
d.text((90, 1428),
       "QUALITY & OPERATIONS - 4 test suites (engines, security, smoke, concurrency) \u00b7 ~72% coverage "
       "\u00b7 GitHub Actions CI (Python 3.11/3.12) \u00b7 Docker deploy: MySQL 8 + gunicorn + nginx TLS",
       font=REG20, fill=WHITE)

img.save(OUT)
print("wrote", OUT, img.size)