from flask import Flask, jsonify, request, render_template_string
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            description TEXT NOT NULL,
            amount NUMERIC NOT NULL,
            paid_by TEXT NOT NULL,
            currency TEXT NOT NULL DEFAULT 'EUR',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

HTML = open(os.path.join(os.path.dirname(__file__), "templates", "index.html")).read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/expenses", methods=["GET"])
def get_expenses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY created_at ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (description, amount, paid_by, currency) VALUES (%s, %s, %s, %s) RETURNING *",
        (data["description"], data["amount"], data["paid_by"], data.get("currency", "EUR"))
    )
    row = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(row), 201

@app.route("/expenses/<id>", methods=["DELETE"])
def delete_expense(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return "", 204

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
