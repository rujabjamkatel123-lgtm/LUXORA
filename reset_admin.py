from werkzeug.security import generate_password_hash
from app.modules.database import db

EMAIL = "admin@luxora.com"
PASSWORD = "admin123"
PASSWORD_HASH = generate_password_hash(PASSWORD, method="pbkdf2:sha256")

admin = db.one("SELECT id FROM users WHERE role=? LIMIT 1", ("admin",))
if admin:
    db.execute(
        "UPDATE users SET email=?, password=?, name=? WHERE id=?",
        (EMAIL, PASSWORD_HASH, "LUXORA Admin", admin["id"]),
    )
    print(f"Updated existing admin in {db.backend} database.")
else:
    db.execute(
        "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
        ("LUXORA Admin", EMAIL, PASSWORD_HASH, "admin"),
    )
    print(f"Created admin in {db.backend} database.")

print(f"Email: {EMAIL}")
print(f"Password: {PASSWORD}")
