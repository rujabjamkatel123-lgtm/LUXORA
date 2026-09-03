from app.modules.database import Database, db
from werkzeug.security import generate_password_hash

cats = [
    ("Fashion", "fashion"),
    ("Electronics", "electronics"),
    ("Beauty", "beauty"),
    ("Home & Living", "home-living"),
    ("Accessories", "accessories"),
]
for name, slug in cats:
    if not db.one("SELECT id FROM categories WHERE slug=?", (slug,)):
        db.execute(
            "INSERT INTO categories(name,slug,description) VALUES(?,?,?)",
            (name, slug, "Thoughtfully curated essentials."),
        )
products = []  # Add your own products from Admin > Products & inventory.

for idx, (name, slug, price, sale) in enumerate(products, 1):
    if not db.one("SELECT id FROM products WHERE name=?", (name,)):
        cid = db.one("SELECT id FROM categories WHERE slug=?", (slug,))["id"]
        base = "-".join(name.lower().replace("°", "").split())
        db.execute(
            "INSERT INTO products(category_id,name,slug,brand,description,price,sale_price,image,sku,stock,rating,review_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                cid,
                name,
                base,
                "LUXORA Studio",
                "Beautifully considered essentials for modern living.",
                price,
                sale,
                None,
                f"LUX-{idx:04}",
                8 + idx % 18,
                4.5 + (idx % 5) / 10,
                12 + idx * 7,
            ),
        )
for email, name, pw, role in [
    ("admin@luxora.com", "LUXORA Admin", "admin123", "admin"),
    ("shopper@luxora.test", "Demo Shopper", "Shopper123!", "customer"),
]:
    existing_user = db.one("SELECT id FROM users WHERE email=?", (email,))
    if existing_user:
        db.execute(
            "UPDATE users SET name=?, password=?, role=? WHERE id=?",
            (
                name,
                generate_password_hash(pw, method="pbkdf2:sha256"),
                role,
                existing_user["id"],
            ),
        )
    elif role == "admin" and db.one("SELECT id FROM users WHERE role=?", ("admin",)):
        db.execute(
            "UPDATE users SET name=?, email=?, password=? WHERE role=?",
            (
                name,
                email,
                generate_password_hash(pw, method="pbkdf2:sha256"),
                role,
            ),
        )
    else:
        db.execute(
            "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (
                name,
                email,
                generate_password_hash(pw, method="pbkdf2:sha256"),
                role,
            ),
        )
if not db.one("SELECT id FROM coupons WHERE code=?", ("WELCOME10",)):
    db.execute(
        "INSERT INTO coupons(code,kind,value,min_purchase) VALUES(?,?,?,?)",
        ("WELCOME10", "percent", 10, 0),
    )
print(
    "Seeded LUXORA. Admin: admin@luxora.com / admin123 Customer: shopper@luxora.test / Shopper123!"
)
