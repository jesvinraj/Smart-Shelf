"""SmartShelf application entry point and factory.

Run with:
    python app.py
  or:
    flask --app app run
"""
import os

from flask import Flask, jsonify, redirect, request, url_for

from config import Config
from data.database import db, login_manager, migrate


def create_app(config_object=None) -> Flask:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "presentation", "templates"),
        static_folder=os.path.join(base_dir, "presentation", "static"),
    )
    app.config.from_object(Config)
    if config_object:
        app.config.from_object(config_object)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "pages.login"

    @login_manager.unauthorized_handler
    def _unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"error": "Authentication required", "status": 401}), 401
        return redirect(url_for("pages.login", next=request.path))

    login_manager.session_protection = "strong"

    # Register all models & user_loader
    import data.models  # noqa: F401
    from data.models.user import load_user  # noqa: F401

    register_all_blueprints(app)

    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        register_commands(app)

    return app


def register_all_blueprints(app: Flask) -> None:
    # Presentation
    from presentation.routes.page_routes import bp as pages_bp
    app.register_blueprint(pages_bp)

    # Services API
    from services.api.auth_routes import bp as auth_bp
    from services.api.product_routes import bp as products_bp
    from services.api.supplier_routes import bp as suppliers_bp
    from services.api.inventory_routes import bp as inventory_bp
    from services.api.batch_routes import bp as batch_bp
    from services.api.sales_routes import bp as sales_bp
    from services.api.pricing_routes import bp as pricing_bp
    from services.api.alert_routes import bp as alerts_bp
    from services.api.waste_routes import bp as waste_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(waste_bp)

    # Analytics API
    from analytics.routes.analytics_routes import bp as analytics_bp
    from analytics.routes.report_routes import bp as reports_bp

    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)


def register_commands(app: Flask) -> None:
    from cli import create_admin, init_db, init_sql, seed

    app.cli.add_command(init_db)
    app.cli.add_command(init_sql)
    app.cli.add_command(seed)
    app.cli.add_command(create_admin)


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
