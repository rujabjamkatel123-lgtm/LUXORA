import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app.modules.database import db
from app.routes.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def save_product_image():
    upload = request.files.get("image_file")
    if not upload or not upload.filename:
        return request.form.get("image", "").strip() or None
    allowed = {"png", "jpg", "jpeg", "webp", "gif"}
    extension = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
    if extension not in allowed:
        return request.form.get("image", "").strip() or None
    filename = f"product-{uuid.uuid4().hex}.{extension}"
    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images"))
    os.makedirs(folder, exist_ok=True)
    upload.save(os.path.join(folder, secure_filename(filename)))
    return f"/static/images/{filename}"


@admin_bp.before_request
def guard():
    return admin_required(lambda: None)() if False else None


@admin_bp.route("")
@admin_required
def dashboard():
    stats = {
        "revenue": db.one("SELECT COALESCE(SUM(total),0) x FROM orders")["x"],
        "orders": db.one("SELECT COUNT(*) x FROM orders")["x"],
        "customers": db.one("SELECT COUNT(*) x FROM users WHERE role='customer'")["x"],
        "products": db.one("SELECT COUNT(*) x FROM products")["x"],
        "low_stock": db.one(
            "SELECT COUNT(*) x FROM products WHERE stock<=low_stock_threshold"
        )["x"],
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/products")
@admin_required
def products():
    categories = db.query("SELECT * FROM categories ORDER BY name")
    if not categories:
        default_categories = [
            ("Fashion", "fashion", "Modern clothing and everyday style."),
            ("Electronics", "electronics", "Useful technology for work and life."),
            ("Beauty", "beauty", "Simple self-care and beauty essentials."),
            ("Home & Living", "home-living", "Thoughtful pieces for a comfortable home."),
            ("Accessories", "accessories", "Finishing touches for every day."),
        ]
        for name, slug, description in default_categories:
            db.execute(
                "INSERT INTO categories(name,slug,description) VALUES(?,?,?)",
                (name, slug, description),
            )
        categories = db.query("SELECT * FROM categories ORDER BY name")
    return render_template(
        "admin/products.html",
        products=db.query(
            "SELECT p.*,c.name category_name FROM products p JOIN categories c ON c.id=p.category_id ORDER BY p.id DESC"
        ),
        categories=categories,
    )


@admin_bp.route("/products/create", methods=["POST"])
@admin_required
def create_product():
    name = request.form.get("name", "").strip()
    slug = "-".join(name.lower().split())
    db.execute(
        "INSERT INTO products(category_id,name,slug,brand,description,price,sale_price,image,sku,stock) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (
            request.form.get("category_id"),
            name,
            slug,
            request.form.get("brand"),
            request.form.get("description"),
            request.form.get("price"),
            request.form.get("sale_price") or None,
            save_product_image(),
            request.form.get("sku"),
            request.form.get("stock", 0),
        ),
    )
    flash("Product created.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/update", methods=["POST"])
@admin_required
def update_product(product_id):
    name = request.form.get("name", "").strip()
    db.execute(
        "UPDATE products SET name=?, brand=?, category_id=?, price=?, sale_price=?, image=?, stock=?, description=?, is_published=? WHERE id=?",
        (
            name,
            request.form.get("brand"),
            request.form.get("category_id"),
            request.form.get("price"),
            request.form.get("sale_price") or None,
            save_product_image(),
            request.form.get("stock", 0),
            request.form.get("description"),
            1 if request.form.get("is_published") == "1" else 0,
            product_id,
        ),
    )
    flash("Product and inventory updated.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    for table in ("product_variants", "wishlists", "cart_items", "reviews"):
        db.execute(f"DELETE FROM {table} WHERE product_id=?", (product_id,))
    db.execute("DELETE FROM products WHERE id=?", (product_id,))
    flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))


@admin_bp.route("/inventory", methods=["GET", "POST"])
@admin_required
def inventory():
    if request.method == "POST":
        db.execute(
            "UPDATE products SET stock=? WHERE id=?",
            (request.form.get("stock"), request.form.get("product_id")),
        )
        flash("Inventory updated.", "success")
    return render_template(
        "admin/inventory.html",
        products=db.query("SELECT * FROM products ORDER BY stock ASC"),
    )


@admin_bp.route("/orders")
@admin_required
def orders():
    return render_template(
        "admin/orders.html",
        orders=db.query(
            "SELECT o.*,u.name,u.email FROM orders o JOIN users u ON u.id=o.user_id ORDER BY o.created_at DESC"
        ),
    )


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def status(order_id):
    db.execute(
        "UPDATE orders SET status=? WHERE id=?", (request.form.get("status"), order_id)
    )
    return redirect(url_for("admin.orders"))


@admin_bp.route("/customers")
@admin_required
def customers():
    return render_template(
        "admin/customers.html",
        customers=db.query(
            "SELECT u.*,COUNT(o.id) order_count,COALESCE(SUM(o.total),0) total_spent FROM users u LEFT JOIN orders o ON o.user_id=u.id WHERE u.role='customer' GROUP BY u.id"
        ),
    )


@admin_bp.route("/reviews")
@admin_required
def reviews():
    return render_template(
        "admin/reviews.html",
        reviews=db.query(
            "SELECT r.*,p.name product_name,u.name user_name FROM reviews r JOIN products p ON p.id=r.product_id JOIN users u ON u.id=r.user_id"
        ),
    )


@admin_bp.route("/reviews/<int:rid>/<action>", methods=["POST"])
@admin_required
def review_action(rid, action):
    db.execute(
        "UPDATE reviews SET status=? WHERE id=?",
        ("Approved" if action == "approve" else "Hidden", rid),
    )
    return redirect(url_for("admin.reviews"))


@admin_bp.route("/discounts", methods=["GET", "POST"])
@admin_required
def discounts():
    if request.method == "POST":
        db.execute(
            "INSERT INTO coupons(code,kind,value,min_purchase,expires_at) VALUES(?,?,?,?,?)",
            (
                request.form.get("code", "").upper(),
                request.form.get("kind", "percent"),
                request.form.get("value"),
                request.form.get("min_purchase", 0),
                request.form.get("expires_at"),
            ),
        )
        flash("Coupon created.", "success")
    return render_template(
        "admin/discounts.html", coupons=db.query("SELECT * FROM coupons")
    )


@admin_bp.route("/analytics")
@admin_required
def analytics():
    summary = {
        "revenue": db.one("SELECT COALESCE(SUM(total),0) value FROM orders")["value"],
        "orders": db.one("SELECT COUNT(*) value FROM orders")["value"],
        "average_order": db.one("SELECT COALESCE(AVG(total),0) value FROM orders")["value"],
        "customers": db.one("SELECT COUNT(*) value FROM users WHERE role='customer'")["value"],
    }
    return render_template(
        "admin/analytics.html",
        summary=summary,
        orders=db.query(
            "SELECT substr(created_at,1,10) day, SUM(total) revenue, COUNT(*) count FROM orders GROUP BY day ORDER BY day"
        ),
        top_products=db.query(
            "SELECT oi.name, SUM(oi.quantity) units FROM order_items oi GROUP BY oi.product_id, oi.name ORDER BY units DESC LIMIT 5"
        ),
    )


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        values = {
            "store_name": request.form.get("store_name", "LUXORA").strip(),
            "currency": request.form.get("currency", "USD").strip(),
            "free_shipping_threshold": request.form.get("free_shipping_threshold", "50").strip(),
            "tax_rate": request.form.get("tax_rate", "8").strip(),
        }
        for key, value in values.items():
            if db.backend == "mysql":
                db.execute(
                    "INSERT INTO store_settings(`key`,`value`) VALUES(?,?) ON DUPLICATE KEY UPDATE `value`=?",
                    (key, value, value),
                )
            else:
                db.execute(
                    "INSERT OR REPLACE INTO store_settings(`key`,`value`) VALUES(?,?)",
                    (key, value),
                )
        flash("Store settings saved.", "success")
    settings_data = {row["key"]: row["value"] for row in db.query("SELECT `key`,`value` FROM store_settings")}
    return render_template("admin/settings.html", settings=settings_data)
    