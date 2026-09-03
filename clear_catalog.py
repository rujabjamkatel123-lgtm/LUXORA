"""Remove all catalog products from the active LUXORA database.

Run this once when replacing the original demo catalog. It keeps users,
categories, orders, and order history intact.
"""

from app.modules.database import db

product_tables = (
    "product_variants",
    "wishlists",
    "cart_items",
    "reviews",
)

for table in product_tables:
    db.execute(f"DELETE FROM {table}")

db.execute("DELETE FROM products")
print(f"Removed all products from the active {db.backend} database.")
print("Users, categories, orders, and order history were kept.")
