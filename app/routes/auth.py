from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.modules.database import db

auth_bp = Blueprint("auth", __name__)


def safe_next(value):
    return (
        value
        if value and value.startswith("/") and not value.startswith("//")
        else url_for("store.home")
    )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login", next=request.full_path))
        user = db.one("SELECT id,name,email,role FROM users WHERE id=?", (user_id,))
        if not user:
            session.clear()
            return redirect(url_for("auth.login", next=request.full_path))
        # Keep the session synchronized with the database. This prevents an old
        # role value in a long-lived browser session from causing a false 403.
        session.update(
            user_id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
        )
        if user["role"] != "admin":
            return ("Forbidden", 403)
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET" and session.get("user_id"):
        if session.get("role") == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("store.home"))
    requested_next = request.args.get("next") or request.form.get("next")
    nxt = safe_next(requested_next)
    if request.method == "POST":
        user = db.one(
            "SELECT * FROM users WHERE email=?",
            (request.form.get("email", "").strip().lower(),),
        )
        if user and check_password_hash(
            user["password"], request.form.get("password", "")
        ):
            session.clear()
            session.update(
                user_id=user["id"],
                role=user["role"],
                name=user["name"],
                email=user["email"],
            )
            session.permanent = True
            if not requested_next or requested_next in (url_for("store.home"), "/"):
                if user["role"] == "admin":
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("store.home"))
            return redirect(nxt)
        flash("Email or password is incorrect.", "error")
    return render_template("auth/login.html", next=nxt)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    nxt = safe_next(request.args.get("next") or request.form.get("next"))
    if request.method == "POST":
        name, email, phone, password = [
            request.form.get(x, "").strip()
            for x in ("name", "email", "phone", "password")
        ]
        if (
            len(name) < 2
            or "@" not in email
            or len(password) < 8
            or password != request.form.get("confirm_password")
        ):
            flash(
                "Please provide valid details and a matching password (8+ characters).",
                "error",
            )
        elif db.one("SELECT id FROM users WHERE email=?", (email.lower(),)):
            flash("An account with that email already exists.", "error")
        else:
            uid = db.execute(
                "INSERT INTO users(name,email,phone,password) VALUES(?,?,?,?)",
                (
                    name,
                    email.lower(),
                    phone,
                    generate_password_hash(password, method="pbkdf2:sha256"),
                ),
            )
            session.update(user_id=uid, role="customer", name=name, email=email.lower())
            session.permanent = True
            return redirect(nxt)
    return render_template("auth/register.html", next=nxt)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("store.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        flash("If that email exists, reset instructions have been sent.", "success")
    return render_template("auth/forgot.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset(token):
    return render_template("auth/reset.html", token=token)
