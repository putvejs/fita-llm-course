"""
Flask web server: interactive dashboard with data filtering.
Run: python app.py  (or via Docker Compose)
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
import mysql.connector

load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": "direct_payments",
}


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def q(conn, sql: str, params: tuple = ()):
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows


def _next_month(ym: str) -> str:
    y, m = map(int, ym.split("-"))
    m += 1
    if m > 12:
        m, y = 1, y + 1
    return f"{y:04d}-{m:02d}-01"


def build_where(currency=None, vertical=None, source=None, start=None, end=None):
    conds, params = [], []
    if currency and currency != "ALL":
        conds.append("p.currency = %s")
        params.append(currency)
    if vertical and vertical != "ALL":
        conds.append("o.parent_vertical = %s")
        params.append(vertical)
    if source and source != "ALL":
        conds.append("p.source = %s")
        params.append(source)
    if start:
        conds.append("p.created_at >= %s")
        params.append(start + "-01")
    if end:
        conds.append("p.created_at < %s")
        params.append(_next_month(end))
    where = ("WHERE " + " AND ".join(conds)) if conds else ""
    return where, tuple(params)


def args():
    f = request.args
    return f.get("currency"), f.get("vertical"), f.get("source"), f.get("start"), f.get("end")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/filters")
def get_filters():
    conn = get_conn()
    verticals = [r["parent_vertical"] for r in q(conn,
        "SELECT DISTINCT parent_vertical FROM organisations ORDER BY parent_vertical")]
    sources = [r["source"] for r in q(conn,
        "SELECT DISTINCT source FROM payments ORDER BY source")]
    bounds = q(conn,
        "SELECT MIN(DATE_FORMAT(created_at, '%Y-%m')) AS min_m, "
        "MAX(DATE_FORMAT(created_at, '%Y-%m')) AS max_m FROM payments")
    conn.close()
    return jsonify({
        "verticals": verticals,
        "sources": sources,
        "min_month": bounds[0]["min_m"],
        "max_month": bounds[0]["max_m"],
    })


@app.route("/api/summary")
def summary():
    where, params = build_where(*args())
    conn = get_conn()
    row = q(conn, f"""
        SELECT COUNT(*) AS total_payments,
               ROUND(SUM(p.amount ), 2) AS total_revenue,
               ROUND(AVG(p.amount ), 2) AS avg_payment,
               COUNT(DISTINCT m.organisation_id) AS active_orgs,
               COUNT(DISTINCT p.mandate_id) AS active_mandates
        FROM payments p
        JOIN mandates m ON p.mandate_id = m.id
        JOIN organisations o ON m.organisation_id = o.id
        {where}
    """, params)
    conn.close()
    return jsonify(row[0] if row else {})


@app.route("/api/revenue-over-time")
def revenue_over_time():
    where, params = build_where(*args())
    conn = get_conn()
    rows = q(conn, f"""
        SELECT DATE_FORMAT(p.created_at, '%Y-%m') AS month,
               COUNT(*) AS payment_count,
               ROUND(SUM(p.amount ), 2) AS revenue
        FROM payments p
        JOIN mandates m ON p.mandate_id = m.id
        JOIN organisations o ON m.organisation_id = o.id
        {where}
        GROUP BY DATE_FORMAT(p.created_at, '%Y-%m')
        ORDER BY month
    """, params)
    conn.close()
    return jsonify(rows)


@app.route("/api/revenue-by-vertical")
def revenue_by_vertical():
    currency, _, source, start, end = args()
    where, params = build_where(currency, None, source, start, end)
    conn = get_conn()
    rows = q(conn, f"""
        SELECT o.parent_vertical AS vertical,
               ROUND(SUM(p.amount ), 2) AS revenue,
               COUNT(*) AS payment_count
        FROM payments p
        JOIN mandates m ON p.mandate_id = m.id
        JOIN organisations o ON m.organisation_id = o.id
        {where}
        GROUP BY o.parent_vertical
        ORDER BY revenue DESC
    """, params)
    conn.close()
    return jsonify(rows)


@app.route("/api/source-breakdown")
def source_breakdown():
    currency, vertical, _, start, end = args()
    where, params = build_where(currency, vertical, None, start, end)
    conn = get_conn()
    rows = q(conn, f"""
        SELECT p.source,
               COUNT(*) AS payment_count,
               ROUND(SUM(p.amount ), 2) AS revenue,
               ROUND(AVG(p.amount ), 2) AS avg_amount
        FROM payments p
        JOIN mandates m ON p.mandate_id = m.id
        JOIN organisations o ON m.organisation_id = o.id
        {where}
        GROUP BY p.source
        ORDER BY revenue DESC
    """, params)
    conn.close()
    return jsonify(rows)


@app.route("/api/avg-value-by-vertical")
def avg_value_by_vertical():
    currency, _, source, start, end = args()
    where, params = build_where(currency, None, source, start, end)
    conn = get_conn()
    rows = q(conn, f"""
        SELECT o.parent_vertical AS vertical,
               ROUND(AVG(p.amount ), 2) AS avg_amount,
               COUNT(*) AS payment_count
        FROM payments p
        JOIN mandates m ON p.mandate_id = m.id
        JOIN organisations o ON m.organisation_id = o.id
        {where}
        GROUP BY o.parent_vertical
        ORDER BY avg_amount DESC
    """, params)
    conn.close()
    return jsonify(rows)


@app.route("/api/mandate-productivity")
def mandate_productivity():
    conn = get_conn()
    rows = q(conn, """
        SELECT m.scheme,
               COUNT(DISTINCT m.id) AS mandate_count,
               COUNT(p.id) AS payment_count,
               ROUND(COUNT(p.id) / COUNT(DISTINCT m.id), 2) AS avg_payments_per_mandate
        FROM mandates m
        LEFT JOIN payments p ON p.mandate_id = m.id
        GROUP BY m.scheme
        ORDER BY avg_payments_per_mandate DESC
    """)
    conn.close()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
