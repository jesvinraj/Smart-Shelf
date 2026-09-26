# SmartShelf — A Local FEFO-Driven Inventory Engine for Automated Spoilage Risk & Dynamic Pricing

A production-grade, layered inventory management and retail decision-support platform designed to eliminate perishable inventory waste, enforce strict First-Expired, First-Out (FEFO) order fulfilment, dynamically calculate multi-factor spoilage risk scores, and automate revenue-recovering dynamic price markdowns.

---

## 1. System Architecture (5-Layer Model)

SmartShelf is structured according to a strict **5-Layer Architecture** with clear boundaries of concern, high cohesion, and low coupling:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             1. PRESENTATION LAYER                                │
│        Jinja2 Templates (HTML5) · Responsive UI (CSS3) · Client Controllers (JS) │
│           Pages: Dashboard · Products · Inventory · Batches · Scan · FEFO        │
│             Pricing · Risk · Sales/POS · Analytics · Alerts · Reports            │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ JSON API & HTML Requests
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       2. APPLICATION / SERVICE LAYER                             │
│       REST Blueprints (/api/*) · RBAC Authorization (@at_least, @roles_required) │
│        Stock Service · Expiry Service · Alert Service · Notification Service     │
│       Waste & Recovery Service · Audit Log Service · Product/Barcode Lookup      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Algorithmic Invocations
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      3. INTELLIGENCE / ENGINE LAYER                              │
│       • FEFO Allocation Engine (sort_batches_fefo, select_batch_for_sale)        │
│       • Spoilage Risk Engine (0-100 score: Expiry 45%, Perishability 35%, Vel 20%)│
│       • Dynamic Pricing Engine (Auto markdown 10%-60% + Reason Generator)        │
│       • Demand & Velocity Engine (Pandas sales velocity & demand forecasting)    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Data Aggregations & Query Execution
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                               4. DATA LAYER                                      │
│      SQLAlchemy ORM Models (User, Product, StockBatch, Sale, Wastage, ...)        │
│           Connection Pool Management · Relational DDL (schema.sql) · Seed        │
│             SQLite (Zero-Setup Dev) · MySQL 8.4 / PostgreSQL (Production)        │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Business Metric Aggregation
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       5. ANALYTICS & OUTCOME LAYER                               │
│      Multi-dimensional Reporting (Sales, Inventory, Expiry, Discounts, Audit)   │
│       Real-Time Financial Recovery Ledger · Waste Loss vs Savings Realized       │
│              Decision Support Dashboard KPIs · System Health Telemetry           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules Breakdown (17 Modules)

The platform is organized across 17 core business modules:

| # | Module Name | Layer | Purpose & Key Capabilities |
|---|---|---|---|
| **1** | **User & Access Management** | Application & Data | 6-tier hierarchical RBAC (`USER` $\rightarrow$ `STAFF` $\rightarrow$ `CASHIER` $\rightarrow$ `BILLER` $\rightarrow$ `MANAGER` $\rightarrow$ `ADMIN`), TOTP 2FA, brute-force IP rate limiting, account lockout after 5 failures, signed password reset tokens, and audit trail. |
| **2** | **Product Management** | Application & Data | Catalog management for items, categories, brands, SKUs, barcodes, unit pricing, cost pricing, storage condition tags (`AMBIENT`, `CHILLED`, `FROZEN`), and reorder thresholds. |
| **3** | **Supplier Management** | Application & Data | Supplier directory, vendor contact information, and supplier-to-batch tracking. |
| **4** | **Inventory Management** | Application & Data | Inbound receiving, inter-location stock transfers, manual adjustments, and complete audit movement logging (`IN`, `OUT`, `TRANSFER`, `ADJUSTMENT`, `WASTAGE`). |
| **5** | **Batch Management** | Application & Data | Batch-level traceability tracking batch codes, manufacturing dates, expiry dates, batch unit costs, and warehouse shelf locations. |
| **6** | **Expiry & Shelf-Life Management** | Application & Service | Automated remaining shelf-life calculation and categorization into `OK`, `EXPIRING_SOON`, and `EXPIRED` status. |
| **7** | **FEFO Inventory Engine** | Intelligence / Engine | Core First-Expired, First-Out allocation algorithm. Prioritizes nearest-expiry batches and automatically blocks expired stock from sale. |
| **8** | **Sales & Transaction Management** | Application & Data | Point-of-Sale checkout workflow with atomic inventory decrement (`UPDATE ... WHERE quantity >= x`), multi-batch line item allocation, and invoice generation. |
| **9** | **Demand & Sales Analysis** | Intelligence / Engine | Pandas-powered sales velocity analysis (units/day), product velocity classification (`FAST`, `NORMAL`, `SLOW`), and moving-average demand forecasting. |
| **10** | **Spoilage Risk Prediction Engine** | Intelligence / Engine | 0–100 multi-factor risk scoring engine combining days-to-expiry (45%), category perishability & storage multiplier (35%), and sales velocity (20%) into `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` risk grades. |
| **11** | **Dynamic Pricing Engine** | Intelligence / Engine | Automated discount recommendation algorithm (10%–60% markdown) paired with human-readable rationale to liquidate at-risk stock before spoilage. |
| **12** | **Discount & Promotion Management** | Application & Data | Promotion lifecycle management (`DRAFT` $\rightarrow$ `PENDING_APPROVAL` $\rightarrow$ `ACTIVE` / `REJECTED`) with multi-level manager creation and admin approval. |
| **13** | **Alert & Notification Management** | Application & Service | Near-expiry warnings, low-stock reorder triggers, and high-risk spoilage alerts with targeted user and admin notification delivery. |
| **14** | **Analytics & Decision Support Dashboard** | Analytics & Outcome | Real-time executive dashboard summarizing inventory valuation, sales revenue, waste write-off valuation, risk distributions, and sales trends. |
| **15** | **Waste & Revenue Recovery Management** | Analytics & Outcome | Spoilage write-off recording, potential financial loss calculation, and recovered revenue / markdown savings tracking. |
| **16** | **Reporting & Administration** | Analytics & Outcome | Comprehensive reporting suite (Sales, Stock, Expiry, Discount, Wastage, Performance, and Security Audit) and `/api/health` system probe. |
| **17** | **Barcode Scanning & Quick Entry** | Presentation & Service | In-browser client-side 1D barcode scanning (`html5-qrcode` CDN) via phone/laptop camera or USB scanner, instantaneous product barcode lookup (`GET /api/products/lookup/<barcode>`), automated inbound batch pre-fill (expiry calculation, cost price), and immediate new product registration fallback. *Requires HTTPS or localhost for browser `getUserMedia` camera permissions.* |

---

## 3. End-to-End Decision & Fulfilment Pipeline

```
Inbound Stock Received (Batch + Expiry Date Registered)
                        │
                        ▼
       Expiry Scan & Shelf-Life Classification
                        │
                        ▼
    Multi-Factor Spoilage Risk Calculation (0-100)
    ├── Days to Expiry (Max 45 pts)
    ├── Category & Storage Factor (Max 35 pts)
    └── Sales Velocity (Max 20 pts)
                        │
                        ▼
   Automated Dynamic Pricing Suggestion (10% - 60% Off)
                        │
                        ▼
       Manager Files / Admin Approves Promotion
                        │
                        ▼
       FEFO-First Point-of-Sale (POS) Checkout
      (Atomic deduction from earliest expiring batch)
                        │
                        ▼
  Financial Outcome: Revenue Recovered & Waste Avoided
```

---

## 4. Directory Structure

```text
SmartShelf/
├── app.py                          # Flask application factory
├── config.py                       # Configuration (SQLite / MySQL / Postgres)
├── cli.py                          # Database initialization & seeding CLI
├── Dockerfile                      # Container build
├── docker-compose.yml              # Multi-container orchestration (App + MySQL + Nginx)
│
├── presentation/                   # [Layer 1: Presentation Layer]
│   ├── templates/                  # Jinja2 HTML templates
│   │   ├── base.html               # Base layout, sidebar & navigation
│   │   ├── dashboard.html          # Executive KPI overview
│   │   ├── products.html           # Product catalog management
│   │   ├── suppliers.html          # Supplier directory
│   │   ├── inventory.html          # Stock receiving & movements
│   │   ├── batches.html            # Batch management
│   │   ├── scan.html               # Barcode scanner & quick stock intake
│   │   ├── expiry.html             # Shelf-life & expiry monitoring
│   │   ├── fefo.html               # FEFO dispatch & queue visualization
│   │   ├── sales.html              # POS checkout & transactions
│   │   ├── risk.html               # Spoilage risk prediction scoring
│   │   ├── pricing.html            # Dynamic pricing & promotions
│   │   ├── analytics.html          # Demand velocity & forecasting
│   │   ├── alerts.html             # Notifications & alert rules
│   │   ├── waste.html              # Waste recording & revenue recovery
│   │   ├── reports.html            # Multi-dimensional reporting suite
│   │   ├── settings.html           # User management & security settings
│   │   ├── login.html              # Secure authentication view
│   │   └── register.html           # Staff onboarding registration
│   ├── static/                     # CSS, JavaScript & theme assets
│   │   ├── css/style.css           # Modern, responsive design theme
│   │   └── js/                     # Frontend client controllers (including scan.js)
│   └── routes/                     # Server-side page routing
│       └── page_routes.py          # HTML view blueprint
│
├── services/                       # [Layer 2: Application / Service Layer]
│   ├── stock_service.py            # Inbound, transfer, adjustment & stock deduction
│   ├── expiry_service.py           # Shelf-life classification & batch expiry scanning
│   ├── alert_service.py            # Alert rules (low-stock, near-expiry, high-risk)
│   ├── notification_service.py     # In-app notifications & read tracking
│   ├── waste_service.py            # Wastage write-off & revenue recovery ledger
│   ├── audit_service.py            # Audit logging service
│   └── api/                        # REST API Blueprints
│       ├── auth_routes.py          # Authentication, 2FA, lockout & user management
│       ├── product_routes.py       # Products, categories & brands API
│       ├── supplier_routes.py      # Supplier management API
│       ├── inventory_routes.py     # Inbound, movements & transfer API
│       ├── batch_routes.py         # Batch queries & FEFO order API
│       ├── sales_routes.py         # Sales checkout & purchase orders API
│       ├── pricing_routes.py       # Spoilage risk, pricing & promotions API
│       ├── alert_routes.py         # Notifications & alert scans API
│       └── waste_routes.py         # Waste write-offs & recovery summary API
│
├── engines/                        # [Layer 3: Intelligence / Engine Layer]
│   ├── __init__.py                 # Engine package exports
│   ├── fefo_engine.py              # Pure FEFO allocation & batch prioritization
│   ├── risk_engine.py              # Spoilage risk prediction engine (0–100 score)
│   ├── pricing_engine.py           # Dynamic markdown pricing & justification generator
│   └── demand_engine.py            # Pandas sales velocity & demand forecasting
│
├── data/                           # [Layer 4: Data Layer]
│   ├── __init__.py                 # Data package exports
│   ├── database.py                 # SQLAlchemy db instance, session & health check
│   ├── schema.sql                  # Canonical SQL DDL
│   ├── seed_data.sql               # Reference & demo seed data
│   └── models/                     # SQLAlchemy ORM models
│       ├── __init__.py             # Model exports
│       ├── user.py, login.py       # User authentication & login audit
│       ├── enums.py                # System-wide enumerations & roles
│       ├── product.py, supplier.py # Products, brands, categories, suppliers
│       ├── batch.py, inventory.py  # Stock batches, locations, movements
│       ├── sales.py, discount.py   # Orders, invoices, payments, promotions
│       └── alert.py, waste.py      # Notifications, audit logs, wastage records
│
├── analytics/                      # [Layer 5: Analytics & Outcome Layer]
│   ├── __init__.py                 # Analytics package exports
│   ├── report_service.py           # Multi-dimensional reporting service
│   └── routes/                     # Analytics & reporting API endpoints
│       ├── analytics_routes.py     # Dashboard KPIs, velocity & forecasting API
│       └── report_routes.py        # Business reports & health API
│
├── core/                           # Cross-Cutting Security & Shared Utilities
│   ├── __init__.py                 # Core package exports
│   ├── security.py                 # Password policy, TOTP, lockout, IP rate limit
│   ├── decorators.py               # RBAC decorators (@at_least, @roles_required)
│   ├── helpers.py                  # Formatters & SKU helpers
│   └── validators.py               # Input validation helpers
│
├── tests/                          # Automated Test Suites
│   ├── test_engines.py             # FEFO, risk scoring & dynamic pricing unit tests
│   ├── test_security.py            # RBAC, TOTP, lockout & token reset tests
│   ├── test_concurrency.py         # Atomic stock deduction & race condition tests
│   ├── test_barcode.py             # Barcode lookup, 404, duplicates & scanning tests
│   └── test_smoke.py               # End-to-end user & inventory workflow tests
│
├── docs/                           # Architecture diagrams & project documentation
├── docker/                         # Nginx TLS termination & entrypoint scripts
└── tools/                          # Utility & presentation build scripts
```

---

## 5. Quick Start (Local Development)

### 1. Set Up Environment

```bash
# Clone or navigate into the repository
cd SmartShelf

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Demo Data

```bash
# Initialize database tables
flask --app app init-db

# Seed sample demo products, batches, suppliers, and users
flask --app app seed
```

### 3. Run Application

```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## 6. Default Demo Credentials

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full system access, approval authority, user administration |
| **Manager** | `manager` | `manager123` | Product, inventory, pricing, promotions, and reports management |
| **Cashier** | `cashier` | `cashier123` | Sales/POS checkout, customer lookup, inventory lookup |

*Note: Newly self-registered accounts start in a pending state and must be activated by an Administrator in the Settings panel.*

---

## 7. Running Automated Test Suites

All tests are written using standard Python `unittest.TestCase` classes:

```bash
# Run all test suites via discovery
python -m unittest discover tests

# Or run individual test suites directly
python tests/test_engines.py      # Core FEFO, risk scoring, and pricing math
python tests/test_security.py     # 35 security scenarios (2FA, lockout, tokens)
python tests/test_concurrency.py  # 20 concurrent threads testing atomic stock deductions
python tests/test_barcode.py      # Barcode lookup, 404 handling & quick entry
python tests/test_smoke.py        # End-to-end workflow verification
```

---

## 8. Docker Deployment (MySQL 8.4 + App + Nginx HTTPS)

Prerequisites: **Docker** & **Docker Compose**.

```bash
# Generate a secure secret key
# On PowerShell:
$env:SECRET_KEY = "your-long-random-secret-key"
# On Bash:
export SECRET_KEY="your-long-random-secret-key"

# Build and start all services
docker compose up -d --build
```

- **App Container**: Runs Flask with Gunicorn workers.
- **DB Container**: Runs MySQL 8.4 with automated schema creation and data seeding.
- **Web Container**: Nginx reverse proxy terminating TLS on port 443 (HTTP auto-redirects to HTTPS).
- Access at **https://localhost** (accept the self-signed certificate in development).