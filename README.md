# LUXORA

LUXORA is a Flask e-commerce store. It uses the uploaded ZIP only as a simple architecture reference: `app/controllers`, `app/modules`, `app/routes`, `app/templates`, and `app/static`. It contains no restaurant, cafe, kitchen, table, menu, or reception functionality.

## Simple structure

```text
LUXORA/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── controllers/
│   │   ├── customer.py
│   │   └── manager.py
│   ├── modules/
│   │   └── database.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── customer.py
│   │   └── manager.py
│   ├── templates/
│   │   ├── layouts/       # shared base layout
│   │   ├── customer/      # storefront and account pages
│   │   ├── auth/          # login and registration pages
│   │   ├── admin/         # admin dashboard pages
│   │   └── components/    # reusable UI pieces
│   └── static/
├── tests/
├── config.py
├── seed.py
├── setup_database.py
├── run.py
├── requirements.txt
└── .env.example
```

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_database.py
python seed.py
python reset_admin.py
python run.py
```

If the database already contains the original 30 demo products, run `python clear_catalog.py` once. It removes products and product-related cart, wishlist, review, and variant records while keeping users, categories, orders, and order history. New runs of `seed.py` do not add demo products.

Open `http://127.0.0.1:5000`.

Demo accounts:

- Admin: `admin@luxora.com` / `admin123`
- Customer: `shopper@luxora.test` / `Shopper123!`

When the app starts, it prints `LUXORA database backend: mysql` or `sqlite`. If login still fails, run `python reset_admin.py` and confirm that it reports the same backend you expect. This updates the admin record in the active database, including an existing admin with an older email address.

## Main features

Customer browsing, search, category filtering, sorting, product details, guest cart, login-required checkout, secure password hashing, mock payment options, orders, inventory updates, order tracking, wishlist, addresses, and account pages are implemented. Admin users can manage products, inventory, orders, customers, reviews, coupons, analytics, and settings.

The database is initialized through `setup_database.py` and the schema in `app/modules/database.py`; there is no separate `.sql` file. Set the local MySQL values directly in `config.py` before running setup, or export matching `MYSQL_*` environment variables. SQLite is used only by tests when `LUXORA_DB` is explicitly set. Payment-card and wallet options are development mocks and do not store CVV or raw card data.

## Tests

```bash
PYTHONPATH=. pytest -q
```
