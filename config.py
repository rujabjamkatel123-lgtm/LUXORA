import os


# =========================================================
# LOCAL DEVELOPMENT CONFIGURATION
# =========================================================
# Edit the MySQL values below for your local database.
# Environment variables, when present, override these values.

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-in-production",
)

# Keep this 0 while running on http://localhost.
# Change it to 1 only after deploying behind HTTPS.
SECURE_SESSION_COOKIE = os.environ.get(
    "SECURE_SESSION_COOKIE",
    "0",
).lower() in {"1", "true", "yes", "on"}


# =========================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================
# Typical local XAMPP/WAMP defaults are:
# host=localhost, port=3306, user=root, password=""
# Create the database named below once in MySQL/phpMyAdmin.

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "dilochan@123")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "class_db")


# Optional compatibility with hosting providers using DB_* names.
if os.environ.get("DB_HOST"):
    MYSQL_HOST = os.environ["DB_HOST"]
if os.environ.get("DB_PORT"):
    MYSQL_PORT = int(os.environ["DB_PORT"])
if os.environ.get("DB_USER"):
    MYSQL_USER = os.environ["DB_USER"]
if os.environ.get("DB_PASSWORD"):
    MYSQL_PASSWORD = os.environ["DB_PASSWORD"]
if os.environ.get("DB_NAME"):
    MYSQL_DATABASE = os.environ["DB_NAME"]
