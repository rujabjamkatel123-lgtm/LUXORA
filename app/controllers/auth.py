"""Authentication controller exports for simple reference-style organization."""

from app.routes.auth import login_required, admin_required

__all__ = ["login_required", "admin_required"]
