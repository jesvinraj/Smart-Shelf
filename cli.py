"""Flask CLI commands: init-db, init-sql, seed, create-admin.

- `init-db`  : create all tables from the ORM metadata.
- `init-sql` : run data/schema.sql against the configured database.
- `seed`     : insert demo data (also mirrored in data/seed_data.sql).
- `create-admin`: create a single admin account.
"""
import os
import bcrypt
import click
from flask.cli import with_appcontext

from data.database import db


@click.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Database tables created from ORM metadata.")


@click.command("init-sql")
@with_appcontext
def init_sql():
    """Create tables by executing data/schema.sql."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "schema.sql")
    if not os.path.exists(path):
        click.echo("data/schema.sql not found.")
        return
    from sqlalchemy import text

    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    db.session.execute(text(sql))
    db.session.commit()
    click.echo("Schema executed.")


@click.command("seed")
@with_appcontext
def seed():
    from datetime import datetime, timedelta, timezone

    from data.models import (
        Brand, Category, Location, Product, StockBatch, Supplier, User,
    )
    from data.models.enums import Role

    if User.query.first():
        click.echo("Database already seeded (users exist).")
        return

    def h(p):
        return bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    admin = User(username="admin", email="admin@local", full_name="Admin",
                 password_hash=h("admin123"), role=Role.ADMIN.value)
    manager = User(username="manager", email="manager@local", full_name="Manager",
                    password_hash=h("manager123"), role=Role.MANAGER.value)
    cashier = User(username="cashier", email="cashier@local", full_name="Cashier",
                    password_hash=h("cashier123"), role=Role.CASHIER.value)
    db.session.add_all([admin, manager, cashier])

    fresh = Category(name="Fresh Produce")
    dairy = Category(name="Dairy")
    bakery = Category(name="Bakery")
    db.session.add_all([fresh, dairy, bakery])
    db.session.flush()

    brand = Brand(name="DemoBrand")
    db.session.add(brand)
    db.session.flush()

    products = [
        Product(name="Milk 1L", sku="MILK1", category_id=dairy.id, brand_id=brand.id,
                unit="btl", unit_price=60.0, cost_price=40.0, shelf_life_days=7,
                storage_condition="CHILLED", is_perishable=True, reorder_level=20, lead_time_days=2),
        Product(name="Bread Loaf", sku="BRD1", category_id=bakery.id, brand_id=brand.id,
                unit="loaf", unit_price=50.0, cost_price=32.0, shelf_life_days=5,
                storage_condition="AMBIENT", is_perishable=True, reorder_level=15, lead_time_days=1),
        Product(name="Curd 500g", sku="CRD1", category_id=dairy.id, brand_id=brand.id,
                unit="cup", unit_price=52.0, cost_price=35.0, shelf_life_days=8,
                storage_condition="CHILLED", is_perishable=True, reorder_level=18, lead_time_days=2),
        Product(name="Tomatoes 500g", sku="TOM500", category_id=fresh.id, brand_id=brand.id,
                unit="pk", unit_price=45.0, cost_price=28.0, shelf_life_days=5,
                storage_condition="AMBIENT", is_perishable=True, reorder_level=30, lead_time_days=1),
    ]
    db.session.add_all(products)
    db.session.flush()

    loc1 = Location(code="A1", name="Shelf A1", zone="Dairy")
    loc2 = Location(code="B2", name="Shelf B2", zone="Fresh")
    loc3 = Location(code="C3", name="Shelf C3", zone="Bakery")
    db.session.add_all([loc1, loc2, loc3])
    db.session.flush()

    sup = Supplier(name="Acme Foods", contact_person="Jane", phone="555-0100")
    db.session.add(sup)
    db.session.flush()

    today = datetime.now(timezone.utc)
    db.session.add_all([
        StockBatch(product_id=products[0].id, location_id=loc1.id, supplier_id=sup.id,
                   batch_code="ML101", batch_number="ML101", quantity=50, cost_price=40.0,
                   manufactured_date=today - timedelta(days=1),
                   expiry_date=today + timedelta(days=6)),
        StockBatch(product_id=products[0].id, location_id=loc1.id, supplier_id=sup.id,
                   batch_code="ML102", batch_number="ML102", quantity=30, cost_price=38.0,
                   manufactured_date=today - timedelta(days=4),
                   expiry_date=today + timedelta(days=2)),
        StockBatch(product_id=products[1].id, location_id=loc3.id, supplier_id=sup.id,
                   batch_code="BR201", batch_number="BR201", quantity=40, cost_price=32.0,
                   manufactured_date=today - timedelta(days=1),
                   expiry_date=today + timedelta(days=3)),
        StockBatch(product_id=products[2].id, location_id=loc1.id, supplier_id=sup.id,
                   batch_code="CR301", batch_number="CR301", quantity=25, cost_price=35.0,
                   manufactured_date=today - timedelta(days=3),
                   expiry_date=today + timedelta(days=4)),
        StockBatch(product_id=products[3].id, location_id=loc2.id, supplier_id=sup.id,
                   batch_code="TM401", batch_number="TM401", quantity=80, cost_price=28.0,
                   manufactured_date=today - timedelta(days=2),
                   expiry_date=today + timedelta(days=3)),
    ])
    db.session.commit()
    click.echo(
        "Seeded demo data. "
        "Logins: admin/admin123, manager/manager123, cashier/cashier123"
    )


@click.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_admin(username, email, password):
    from data.models import User
    from data.models.enums import Role

    user = User(
        username=username, email=email, full_name=username,
        password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        role=Role.ADMIN.value,
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin {username} created.")
