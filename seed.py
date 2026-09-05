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
products = [
    # Fashion
    ("Organic Cotton Hoodie", "fashion", 89.00, 69.00, "/static/images/cotton-hoodie.jpg", "LUXORA Wear", "Ultra-soft heavyweight organic cotton hoodie designed for everyday comfort."),
    ("Linen Oversized Shirt", "fashion", 75.00, None, "/static/images/linen-shirt.jpg", "LUXORA Wear", "Breathable pure linen button-up shirt crafted with a relaxed fit."),
    ("Relaxed Tapered Joggers", "fashion", 65.00, 49.00, "/static/images/relaxed-joggers.jpg", "LUXORA Wear", "Tapered lounge joggers with drawstring waist and deep side pockets."),
    ("Everyday Canvas Cap", "fashion", 35.00, None, "/static/images/canvas-cap.jpg", "LUXORA Wear", "Classic 6-panel canvas cap with adjustable metallic clasp."),
    ("Denim Cap", "fashion", 38.00, 29.00, "/static/images/everyday-denim-cap.jpg", "LUXORA Wear", "Washed indigo denim cap with embroidered subtle branding."),
    # Electronics
    ("Mini Bluetooth Speaker", "electronics", 129.00, 99.00, "/static/images/mini-bluetooth-speaker.jpg", "LUXORA Tech", "Compact wireless speaker with 360-degree room-filling acoustic audio."),
    ("Ergonomic Wireless Mouse", "electronics", 59.00, 45.00, "/static/images/wireless-mouse.jpg", "LUXORA Tech", "Precision optical wireless mouse with silent clicks and ergonomic grip."),
    ("Minimal Desk Phone Stand", "electronics", 29.00, None, "/static/images/desk-phone-stand.jpg", "LUXORA Tech", "Solid aluminum desktop stand for smartphones and tablets."),
    ("USB LED Desk Light", "electronics", 49.00, 39.00, "/static/images/usb-desk-light.jpg", "LUXORA Tech", "Dimmable touch-control LED lamp with flexible neck and warm light modes."),
    ("Cable Organizer Set", "electronics", 24.00, None, "/static/images/cable-organizer-set.jpg", "LUXORA Tech", "Silicone magnetic cable management clips to keep desks clean."),
    # Beauty
    ("Hydrating Face Mist", "beauty", 32.00, 26.00, "/static/images/hydrating-face-mist.jpg", "LUXORA Skin", "Botanical facial toner infused with rosewater and hyaluronic acid."),
    ("Gentle Detox Clay Mask", "beauty", 42.00, None, "/static/images/gentle-clay-mask.jpg", "LUXORA Skin", "Purifying French green clay mask for smooth and refreshed skin."),
    ("Daily Body Moisture Lotion", "beauty", 38.00, 29.00, "/static/images/daily-body-lotion.jpg", "LUXORA Skin", "Nourishing shea butter body lotion providing 24-hour hydration."),
    ("Restorative Hand Cream", "beauty", 22.00, None, "/static/images/daily-hand-cream.jpg", "LUXORA Skin", "Velvety non-greasy hand cream with almond oil and vitamin E."),
    ("Rose Tinted Lip Balm", "beauty", 18.00, 14.00, "/static/images/rose-lip-balm.jpg", "LUXORA Skin", "Moisturizing lip balm with natural jojoba oil and subtle rose tint."),
    # Home & Living
    ("Stoneware Ceramic Mug", "home-living", 25.00, None, "/static/images/stoneware-mug.jpg", "LUXORA Home", "Handcrafted stoneware mug with matte satin glaze."),
    ("Scented Soy Candle", "home-living", 36.00, 28.00, "/static/images/scented-candle.jpg", "LUXORA Home", "Hand-poured soy wax candle with sandalwood and amber scent notes."),
    ("Cotton Cushion Cover", "home-living", 34.00, None, "/static/images/cotton-cushion-cover.jpg", "LUXORA Home", "Textured woven cotton pillow cover with hidden zip closure."),
    ("Wooden Serving Tray", "home-living", 68.00, 52.00, "/static/images/wooden-serving-tray.jpg", "LUXORA Home", "Solid oak wood serving board with carved handles."),
    ("Woven Storage Basket", "home-living", 45.00, 36.00, "/static/images/woven-storage-basket.jpg", "LUXORA Home", "Hand-woven natural seagrass basket for blanket and laundry storage."),
    # Accessories
    ("Leather Card Holder", "accessories", 48.00, 38.00, "/static/images/leather-card-holder.jpg", "LUXORA Studio", "Slim full-grain leather wallet with 5 card slots and RFID protection."),
    ("Minimalist Sunglasses", "accessories", 79.00, 59.00, "/static/images/minimal-sunglasses.jpg", "LUXORA Studio", "UV400 protection polarized acetate sunglasses with timeless frame."),
    ("Daily Canvas Tote Bag", "accessories", 42.00, None, "/static/images/daily-tote-bag.jpg", "LUXORA Studio", "Heavyweight canvas tote with inner zippered phone pocket."),
    ("Handmade Beaded Bracelet", "accessories", 28.00, 22.00, "/static/images/beaded-bracelet.jpg", "LUXORA Studio", "Natural gemstone stretch bracelet with metallic accent bead."),
    ("Classic Hair Clip", "accessories", 16.00, None, "/static/images/classic-hair-clip.jpg", "LUXORA Studio", "Durable tortoiseshell hair claw clip for effortless styling."),
]

for idx, item in enumerate(products, 1):
    name, c_slug, price, sale, img, brand, desc = item
    if not db.one("SELECT id FROM products WHERE name=?", (name,)):
        cid = db.one("SELECT id FROM categories WHERE slug=?", (c_slug,))["id"]
        base = "-".join(name.lower().replace("°", "").replace("&", "and").replace("'", "").split())
        db.execute(
            "INSERT INTO products(category_id,name,slug,brand,description,price,sale_price,image,sku,stock,rating,review_count) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                cid,
                name,
                base,
                brand,
                desc,
                price,
                sale,
                img,
                f"LUX-{idx:04}",
                12 + idx % 15,
                4.6 + (idx % 4) / 10,
                15 + idx * 6,
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
