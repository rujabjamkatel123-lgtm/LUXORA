from decimal import Decimal
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from app.modules.database import db
from app.routes.auth import login_required

store_bp = Blueprint("store", __name__)


def uid():
    return session.get("user_id")


def items():
    return db.cart_items(uid(), request.cookies.get("luxora_session", "guest"))


def product_query(extra="", args=()):
    return db.query(
        "SELECT p.*, c.name category_name,c.slug category_slug FROM products p JOIN categories c ON c.id=p.category_id WHERE p.is_published=1 ORDER BY p.created_at DESC"
        + extra,
        args,
    )


@store_bp.route("/")
def home():
    return render_template(
        "customer/home.html",
        products=product_query(" LIMIT 8"),
        new_products=product_query(" LIMIT 6"),
    )


@store_bp.route("/shop")
def shop():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "")
    sort = request.args.get("sort", "newest")
    where = ["p.is_published=1"]
    args = []
    if q:
        where.append("(p.name LIKE ? OR p.description LIKE ? OR p.brand LIKE ?)")
        args += [f"%{q}%"] * 3
    if cat:
        where.append("c.slug=?")
        args.append(cat)
    ordering = {
        "price_asc": "p.sale_price IS NULL, COALESCE(p.sale_price,p.price) ASC",
        "price_desc": "COALESCE(p.sale_price,p.price) DESC",
        "rating": "p.rating DESC",
        "newest": "p.created_at DESC",
    }.get(sort, "p.created_at DESC")
    products = db.query(
        "SELECT p.*,c.name category_name,c.slug category_slug FROM products p JOIN categories c ON c.id=p.category_id WHERE "
        + " AND ".join(where)
        + " ORDER BY "
        + ordering,
        args,
    )
    return render_template(
        "customer/shop.html", products=products, q=q, active_category=cat, sort=sort
    )


@store_bp.route("/category/<slug>")
def category(slug):
    return redirect(url_for("store.shop", category=slug))


@store_bp.route("/search")
def search():
    return redirect(url_for("store.shop", q=request.args.get("q", "")))


@store_bp.route("/product/<slug>")
def product(slug):
    p = db.one(
        "SELECT p.*,c.name category_name,c.slug category_slug FROM products p JOIN categories c ON c.id=p.category_id WHERE p.slug=? AND p.is_published=1",
        (slug,),
    )
    if not p:
        return render_template("customer/error.html", code=404, message="Product not found"), 404
    reviews = db.query(
        'SELECT r.*,u.name FROM reviews r JOIN users u ON u.id=r.user_id WHERE r.product_id=? AND r.status="Approved" ORDER BY r.created_at DESC',
        (p["id"],),
    )
    return render_template("customer/product.html", product=p, reviews=reviews)


@store_bp.route("/cart")
def cart():
    data = items()
    return render_template("customer/cart.html", items=data, totals=db.totals(data))


@store_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_cart(product_id):
    p = db.one("SELECT * FROM products WHERE id=? AND is_published=1", (product_id,))
    qty = max(1, int(request.form.get("quantity", 1)))
    if not p or p["stock"] < qty:
        flash("This product is unavailable or low in stock.", "error")
        return redirect(request.referrer or url_for("store.shop"))
    cid = db.cart_id(uid(), request.cookies.get("luxora_session", "guest"))
    existing = db.one(
        "SELECT * FROM cart_items WHERE cart_id=? AND product_id=?", (cid, product_id)
    )
    if existing:
        db.execute(
            "UPDATE cart_items SET quantity=MIN(?,quantity+?) WHERE id=?",
            (p["stock"], qty, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO cart_items(cart_id,product_id,quantity) VALUES(?,?,?)",
            (cid, product_id, qty),
        )
    flash("Product added to cart.", "success")
    return redirect(
        request.form.get("next") or request.referrer or url_for("store.cart")
    )


@store_bp.route("/cart/update/<int:item_id>", methods=["POST"])
def update_cart(item_id):
    qty = max(0, int(request.form.get("quantity", 1)))
    if qty == 0:
        db.execute("DELETE FROM cart_items WHERE id=?", (item_id,))
    else:
        item = db.one(
            "SELECT p.stock FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.id=?",
            (item_id,),
        )
        if not item:
            return redirect(url_for("store.cart"))
        db.execute(
            "UPDATE cart_items SET quantity=? WHERE id=?",
            (min(qty, int(item["stock"])), item_id),
        )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        current_items = items()
        return jsonify(
            {
                "ok": True,
                "count": sum(int(item["quantity"]) for item in current_items),
                "totals": {key: str(value) for key, value in db.totals(current_items).items()},
            }
        )
    return redirect(url_for("store.cart"))


@store_bp.route("/wishlist")
@login_required
def wishlist():
    return render_template(
        "customer/wishlist.html",
        products=db.query(
            "SELECT p.* FROM wishlists w JOIN products p ON p.id=w.product_id WHERE w.user_id=?",
            (uid(),),
        ),
    )


@store_bp.route("/wishlist/toggle/<int:product_id>", methods=["POST"])
@login_required
def wishlist_toggle(product_id):
    found = db.one(
        "SELECT id FROM wishlists WHERE user_id=? AND product_id=?", (uid(), product_id)
    )
    (
        db.execute("DELETE FROM wishlists WHERE id=?", (found["id"],))
        if found
        else db.execute(
            "INSERT INTO wishlists(user_id,product_id) VALUES(?,?)", (uid(), product_id)
        )
    )
    return redirect(request.referrer or url_for("store.shop"))


@store_bp.route("/checkout")
@login_required
def checkout():
    return render_template("customer/checkout.html", items=items(), totals=db.totals(items()))


@store_bp.route("/checkout/place", methods=["POST"])
@login_required
def place_order():
    data = items()
    totals = db.totals(data)
    if not data:
        flash("Your cart is empty.", "error")
        return redirect(url_for("store.cart"))
    for i in data:
        p = db.one("SELECT stock FROM products WHERE id=?", (i["product_id"],))
        if not p or p["stock"] < i["quantity"]:
            flash("Stock changed. Please review your cart.", "error")
            return redirect(url_for("store.cart"))
    addr = f"{request.form.get('full_name')}, {request.form.get('line1')}, {request.form.get('city')}, {request.form.get('state')}, {request.form.get('country')}"
    oid = db.execute(
        "INSERT INTO orders(user_id,payment_method,subtotal,shipping,tax,total,shipping_address) VALUES(?,?,?,?,?,?,?)",
        (
            uid(),
            request.form.get("payment_method", "Cash on Delivery"),
            str(totals["subtotal"]),
            str(totals["shipping"]),
            str(totals["tax"]),
            str(totals["total"]),
            addr,
        ),
    )
    for i in data:
        db.execute(
            "INSERT INTO order_items(order_id,product_id,name,quantity,price) VALUES(?,?,?,?,?)",
            (
                oid,
                i["product_id"],
                i["name"],
                i["quantity"],
                str(i["sale_price"] or i["price"]),
            ),
        )
        db.execute(
            "UPDATE products SET stock=stock-? WHERE id=?",
            (i["quantity"], i["product_id"]),
        )
    cid = db.cart_id(uid(), request.cookies.get("luxora_session", "guest"))
    db.execute("DELETE FROM cart_items WHERE cart_id=?", (cid,))
    return redirect(url_for("store.success", order_id=oid))


@store_bp.route("/order-success/<int:order_id>")
@login_required
def success(order_id):
    order = db.one("SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, uid()))
    its = db.query("SELECT * FROM order_items WHERE order_id=?", (order_id,))
    return render_template("customer/success.html", order=order, items=its)


@store_bp.route("/orders/<int:order_id>/track")
@login_required
def track(order_id):
    return render_template(
        "customer/track.html",
        order=db.one(
            "SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, uid())
        ),
    )


@store_bp.route("/account")
@login_required
def account():
    orders = db.query(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (uid(),)
    )
    return render_template("customer/account.html", orders=orders)


@store_bp.route("/account/orders")
@login_required
def account_orders():
    return redirect(url_for("store.account"))


@store_bp.route("/account/addresses", methods=["GET", "POST"])
@login_required
def addresses():
    if request.method == "POST":
        db.execute(
            "INSERT INTO addresses(user_id,full_name,line1,city,state,country) VALUES(?,?,?,?,?,?)",
            (
                uid(),
                request.form.get("full_name"),
                request.form.get("line1"),
                request.form.get("city"),
                request.form.get("state"),
                request.form.get("country"),
            ),
        )
        flash("Address saved.", "success")
    return render_template(
        "customer/account_addresses.html",
        addresses=db.query("SELECT * FROM addresses WHERE user_id=?", (uid(),)),
    )


@store_bp.route("/api/cart")
def api_cart():
    return jsonify(
        {"items": items(), "totals": {k: str(v) for k, v in db.totals(items()).items()}}
    )
