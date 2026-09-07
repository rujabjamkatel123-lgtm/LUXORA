import os

if not os.getenv("LUXORA_DB"):
    os.environ["LUXORA_DB"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "luxora.db"
    )

from app import create_app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
