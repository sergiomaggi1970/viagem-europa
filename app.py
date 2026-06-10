from flask import Flask, jsonify, request, render_template_string
import os
import httpx

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://espasbxfpnghcujhrqld.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

HTML = open(os.path.join(os.path.dirname(__file__), "templates", "index.html")).read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/expenses", methods=["GET"])
def get_expenses():
    r = httpx.get(f"{SUPABASE_URL}/rest/v1/expenses?order=created_at.asc", headers=HEADERS)
    return jsonify(r.json())

@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.json
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/expenses", headers=HEADERS, json={
        "description": data["description"],
        "amount": data["amount"],
        "paid_by": data["paid_by"]
    })
    return jsonify(r.json()), 201

@app.route("/expenses/<id>", methods=["DELETE"])
def delete_expense(id):
    r = httpx.delete(f"{SUPABASE_URL}/rest/v1/expenses?id=eq.{id}", headers=HEADERS)
    return "", 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
