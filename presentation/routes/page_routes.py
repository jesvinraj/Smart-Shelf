"""Presentation Layer: Server-rendered HTML page routes."""
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("pages", __name__)


def p(template: str, active: str):
    return render_template(template, active=active)


@bp.route("/login")
def login():
    return render_template("login.html", active="")


@bp.route("/register")
def register():
    return render_template("register.html", active="")


@bp.route("/")
@login_required
def dashboard():
    return p("dashboard.html", "dashboard")


@bp.route("/products")
@login_required
def products():
    return p("products.html", "products")


@bp.route("/suppliers")
@login_required
def suppliers():
    return p("suppliers.html", "suppliers")


@bp.route("/inventory")
@login_required
def inventory():
    return p("inventory.html", "inventory")


@bp.route("/batches")
@login_required
def batches():
    return p("batches.html", "batches")


@bp.route("/expiry")
@login_required
def expiry():
    return p("expiry.html", "expiry")


@bp.route("/fefo")
@login_required
def fefo():
    return p("fefo.html", "fefo")


@bp.route("/pricing")
@login_required
def pricing():
    return p("pricing.html", "pricing")


@bp.route("/risk")
@login_required
def risk():
    return p("risk.html", "risk")


@bp.route("/sales")
@login_required
def sales():
    return p("sales.html", "sales")


@bp.route("/analytics")
@login_required
def analytics():
    return p("analytics.html", "analytics")


@bp.route("/alerts")
@login_required
def alerts():
    return p("alerts.html", "alerts")


@bp.route("/waste")
@login_required
def waste():
    return p("waste.html", "waste")


@bp.route("/reports")
@login_required
def reports():
    return p("reports.html", "reports")


@bp.route("/settings")
@login_required
def settings():
    return p("settings.html", "settings")
