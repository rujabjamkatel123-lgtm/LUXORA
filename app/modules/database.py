import os
import sqlite3
from decimal import Decimal
from pathlib import Path

import config

try:
    import pymysql
except ImportError:  # Local SQLite development does not require PyMySQL.
    pymysql = None


BASE_DIR = Path(__file__).resolve().parents[2]
SQLITE_PATH = Path(os.getenv("LUXORA_DB", BASE_DIR / "luxora.db"))


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'customer',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    image TEXT
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    brand TEXT,
    description TEXT,
    price NUMERIC NOT NULL,
    sale_price NUMERIC,
    image TEXT,
    sku TEXT UNIQUE NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    rating NUMERIC DEFAULT 4.8,
    review_count INTEGER DEFAULT 0,
    is_published INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    stock INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS carts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    session_key TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    UNIQUE(cart_id, product_id)
);
CREATE TABLE IF NOT EXISTS wishlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    UNIQUE(user_id, product_id)
);
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    full_name TEXT,
    line1 TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    is_default INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    status TEXT DEFAULT 'Pending',
    payment_method TEXT,
    subtotal NUMERIC,
    discount NUMERIC DEFAULT 0,
    shipping NUMERIC DEFAULT 0,
    tax NUMERIC DEFAULT 0,
    total NUMERIC,
    shipping_address TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER,
    name TEXT,
    quantity INTEGER,
    price NUMERIC
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id),
    method TEXT,
    status TEXT DEFAULT 'Pending',
    masked_reference TEXT
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    rating INTEGER,
    comment TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    kind TEXT,
    value NUMERIC,
    min_purchase NUMERIC DEFAULT 0,
    expires_at TEXT,
    usage_limit INTEGER DEFAULT 100,
    active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS coupon_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id INTEGER,
    user_id INTEGER
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS store_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


MYSQL_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(120) NOT NULL,
        email VARCHAR(190) UNIQUE NOT NULL,
        phone VARCHAR(40),
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(120) UNIQUE NOT NULL,
        slug VARCHAR(140) UNIQUE NOT NULL,
        description TEXT,
        image VARCHAR(255)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT NOT NULL,
        name VARCHAR(190) NOT NULL,
        slug VARCHAR(220) UNIQUE NOT NULL,
        brand VARCHAR(120),
        description TEXT,
        price DECIMAL(12,2) NOT NULL,
        sale_price DECIMAL(12,2),
        image VARCHAR(500),
        sku VARCHAR(100) UNIQUE NOT NULL,
        stock INT NOT NULL DEFAULT 0,
        low_stock_threshold INT DEFAULT 5,
        rating DECIMAL(3,2) DEFAULT 4.8,
        review_count INT DEFAULT 0,
        is_published TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS carts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        session_key VARCHAR(190) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS cart_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cart_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        UNIQUE KEY unique_cart_product (cart_id, product_id),
        FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS product_variants (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        name VARCHAR(80) NOT NULL,
        value VARCHAR(120) NOT NULL,
        stock INT DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS wishlists (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        UNIQUE KEY unique_wishlist_product (user_id, product_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS addresses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        full_name VARCHAR(120),
        line1 VARCHAR(255),
        city VARCHAR(100),
        state VARCHAR(100),
        postal_code VARCHAR(30),
        country VARCHAR(100),
        is_default TINYINT(1) DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        status VARCHAR(40) DEFAULT 'Pending',
        payment_method VARCHAR(80),
        subtotal DECIMAL(12,2),
        discount DECIMAL(12,2) DEFAULT 0,
        shipping DECIMAL(12,2) DEFAULT 0,
        tax DECIMAL(12,2) DEFAULT 0,
        total DECIMAL(12,2),
        shipping_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT,
        name VARCHAR(190),
        quantity INT,
        price DECIMAL(12,2),
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        method VARCHAR(80),
        status VARCHAR(40) DEFAULT 'Pending',
        masked_reference VARCHAR(80),
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        product_id INT NOT NULL,
        rating INT,
        comment TEXT,
        status VARCHAR(30) DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS coupons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(80) UNIQUE,
        kind VARCHAR(20),
        value DECIMAL(12,2),
        min_purchase DECIMAL(12,2) DEFAULT 0,
        expires_at DATE,
        usage_limit INT DEFAULT 100,
        active TINYINT(1) DEFAULT 1
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS coupon_usage (
        id INT AUTO_INCREMENT PRIMARY KEY,
        coupon_id INT NOT NULL,
        user_id INT NOT NULL,
        FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        message TEXT,
        is_read TINYINT(1) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS store_settings (
        `key` VARCHAR(100) PRIMARY KEY,
        value TEXT
    ) ENGINE=InnoDB
    """,
]


class Database:
    """Small database helper using MySQL from config.py or SQLite locally."""

    def __init__(self):
        self.backend = "mysql" if self._mysql_is_configured() else "sqlite"
        if self.backend == "mysql":
            if pymysql is None:
                raise RuntimeError("Install PyMySQL to use the configured MySQL database.")
            self.conn = pymysql.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
            )
        else:
            self.conn = sqlite3.connect(
                str(SQLITE_PATH), check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys=ON")

    @staticmethod
    def _mysql_is_configured():
        # Tests can set LUXORA_DB to force an isolated SQLite database.
        if os.getenv("LUXORA_DB"):
            return False
        return all(
            [
                config.MYSQL_HOST,
                config.MYSQL_USER,
                config.MYSQL_DATABASE,
            ]
        )

    def _convert_sql(self, sql):
        if self.backend == "mysql":
            return sql.replace("?", "%s")
        return sql

    def init(self):
        if self.backend == "sqlite":
            self.conn.executescript(SQLITE_SCHEMA)
            self.conn.commit()
            return
        for statement in MYSQL_TABLES:
            self.execute(statement)

    def query(self, sql, args=()):
        cursor = self.conn.cursor()
        cursor.execute(self._convert_sql(sql), args)
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]

    def one(self, sql, args=()):
        rows = self.query(sql, args)
        return rows[0] if rows else None

    def execute(self, sql, args=()):
        cursor = self.conn.cursor()
        try:
            cursor.execute(self._convert_sql(sql), args)
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def close(self):
        self.conn.close()

    def cart_id(self, user_id, session_key):
        if user_id:
            row = self.one("SELECT id FROM carts WHERE user_id=?", (user_id,))
            return row["id"] if row else self.execute(
                "INSERT INTO carts(user_id) VALUES(?)", (user_id,)
            )
        row = self.one("SELECT id FROM carts WHERE session_key=?", (session_key,))
        return row["id"] if row else self.execute(
            "INSERT INTO carts(session_key) VALUES(?)", (session_key,)
        )

    def cart_items(self, user_id, session_key="guest"):
        cart_id = self.cart_id(user_id, session_key)
        return self.query(
            "SELECT ci.*, p.name, p.slug, p.price, p.sale_price, p.image, p.stock "
            "FROM cart_items ci JOIN products p ON p.id=ci.product_id "
            "WHERE cart_id=?",
            (cart_id,),
        )

    def totals(self, items):
        subtotal = sum(
            (
                Decimal(str(item["sale_price"] or item["price"]))
                * int(item["quantity"])
                for item in items
            ),
            Decimal("0"),
        )
        shipping = Decimal("0") if subtotal >= 50 or not items else Decimal("6.99")
        tax = (subtotal * Decimal("0.08")).quantize(Decimal("0.01"))
        return {
            "subtotal": subtotal,
            "shipping": shipping,
            "tax": tax,
            "discount": Decimal("0"),
            "total": subtotal + shipping + tax,
        }


try:
    db = Database()
    db.init()
    print(f"LUXORA database backend: {db.backend}")
except Exception as error:
    print(f"Database initialization failed: {error}")
    raise
