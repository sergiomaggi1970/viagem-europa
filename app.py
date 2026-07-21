from flask import Flask, jsonify, request, render_template_string
import os
import psycopg

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_db():
    return psycopg.connect(DATABASE_URL)

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                description TEXT NOT NULL,
                amount NUMERIC NOT NULL,
                paid_by TEXT NOT NULL,
                currency TEXT NOT NULL DEFAULT 'EUR',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

HTML = open(os.path.join(os.path.dirname(__file__), "templates", "index.html")).read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/expenses", methods=["GET"])
def get_expenses():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY created_at ASC").fetchall()
        cols = [d.name for d in conn.execute("SELECT * FROM expenses LIMIT 0").description or []]
    # re-fetch with column names
    with get_db() as conn:
        cur = conn.execute("SELECT id::text, description, amount::float, paid_by, currency, created_at::text FROM expenses ORDER BY created_at ASC")
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    return jsonify(rows)

@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.json
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO expenses (description, amount, paid_by, currency) VALUES (%s, %s, %s, %s) RETURNING id::text, description, amount::float, paid_by, currency, created_at::text",
            (data["description"], data["amount"], data["paid_by"], data.get("currency", "EUR"))
        )
        cols = [d.name for d in cur.description]
        row = dict(zip(cols, cur.fetchone()))
    return jsonify(row), 201

@app.route("/expenses/<id>", methods=["DELETE"])
def delete_expense(id):
    with get_db() as conn:
        conn.execute("DELETE FROM expenses WHERE id = %s", (id,))
    return "", 204

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
