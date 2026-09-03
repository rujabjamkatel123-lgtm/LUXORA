import os

os.environ["LUXORA_DB"] = "/tmp/luxora_test.db"
from app import create_app
from app.modules.database import db
from seed import products


def setup_module():
    db.init()
    import seed


def test_homepage():
    c = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    assert c.get("/").status_code == 200


def test_checkout_requires_login():
    c = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    r = c.get("/checkout")
    assert r.status_code == 302 and "/login" in r.location


def test_register_and_add_cart():
    c = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    r = c.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    category = db.one("SELECT id FROM categories LIMIT 1")
    db.execute(
        "INSERT OR IGNORE INTO products(category_id,name,slug,price,sku,stock) VALUES(?,?,?,?,?,?)",
        (category["id"], "Test Product", "test-product", 10, "TEST-001", 5),
    )
    p = db.one("SELECT id FROM products LIMIT 1")
    r = c.post(f'/cart/add/{p["id"]}', data={"quantity": 1}, follow_redirects=True)
    assert r.status_code == 200 and b"Shopping cart" in r.data


def test_admin_is_protected():
    c = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
    assert c.get("/admin").status_code == 403
