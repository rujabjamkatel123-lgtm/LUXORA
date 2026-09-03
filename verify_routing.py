from app import create_app

client = create_app({"TESTING": True}).test_client()
admin = client.post("/login", data={"email": "admin@luxora.com", "password": "admin123"})
assert admin.status_code == 302 and admin.location.endswith("/admin")
customer = client.post("/login", data={"email": "shopper@luxora.test", "password": "Shopper123!"})
assert customer.status_code == 302 and customer.location.endswith("/")
print("admin and customer redirects passed")
