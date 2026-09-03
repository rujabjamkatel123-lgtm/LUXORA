"""Authentication helpers exposed from the simple app-level auth module."""

from app.routes.auth import login_required, admin_required

__all__ = ["login_required", "admin_required"]
