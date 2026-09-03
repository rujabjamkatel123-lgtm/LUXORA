from datetime import timedelta
from flask import Flask, render_template
from .controllers.customer import store_bp
from .routes.auth import auth_bp
from .controllers.manager import admin_bp
import config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=config.SECURE_SESSION_COOKIE,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    if test_config:
        app.config.update(test_config)
    app.register_blueprint(store_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        from .modules.database import db

        categories = db.query("SELECT * FROM categories ORDER BY name")
        cart = db.cart_items(session_user_id())
        return {
            "nav_categories": categories,
            "cart_count": sum(int(x["quantity"]) for x in cart),
        }

    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template(
                "customer/error.html",
                code=404,
                message="The page you requested could not be found.",
            ),
            404,
        )

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception(error)
        return (
            render_template(
                "customer/error.html",
                code=500,
                message="Something went wrong. Please try again.",
            ),
            500,
        )

    return app


def session_user_id():
    from flask import session

    return session.get("user_id")
