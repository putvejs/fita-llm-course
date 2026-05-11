"""
Step 2: For each plan item — generate SQL (with validation/retry), create chart, generate insights.
Outputs: output/results.json + output/charts/*.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import mysql.connector
from anthropic import Anthropic
from anthropic.types import TextBlock

from utils import extract_sql, format_schema_for_prompt, slugify

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

OUTPUT_DIR = "output"
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3", "#8C8C8C"]


def _run_sql(conn, sql: str, db_name: str) -> list[dict]:
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"USE `{db_name}`")
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def generate_sql_with_retry(
    client: Anthropic,
    plan_item: dict,
    schema_text: str,
    conn,
    db_name: str,
    max_retries: int = 3,
) -> tuple[str | None, list[dict] | None]:
    messages = [
        {
            "role": "user",
            "content": f"""Generate a MySQL SELECT query for this visualization:

Title: {plan_item['title']}
Description: {plan_item['description']}
Chart type: {plan_item['chart_type']}
X axis: {plan_item['x_label']}
Y axis: {plan_item['y_label']}
Hint: {plan_item['sql_hint']}

DATABASE SCHEMA:
{schema_text}

Rules:
- MySQL ONLY_FULL_GROUP_BY compatible: every non-aggregated SELECT column must appear verbatim in GROUP BY
- Use DATE_FORMAT(..., '%Y-%m') for month grouping, and include it in GROUP BY
- Return at most 30 rows (use LIMIT)
- Return ONLY the raw SQL query, no explanation, no markdown fences""",
        }
    ]

    for attempt in range(max_retries):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system="You are a MySQL expert. Return only valid MySQL SELECT statements.",
            messages=messages,
        )
        reply_text = next(b.text for b in response.content if isinstance(b, TextBlock))
        sql = extract_sql(reply_text)

        if not sql:
            messages.append({"role": "assistant", "content": reply_text})
            messages.append({"role": "user", "content": "Could not extract SQL. Return ONLY the SELECT statement, no prose."})
            continue

        try:
            rows = _run_sql(conn, sql, db_name)
            print(f"    SQL OK ({len(rows)} rows, attempt {attempt + 1})")
            return sql, rows
        except Exception as e:
            print(f"    SQL error attempt {attempt + 1}: {e}")
            messages.append({"role": "assistant", "content": reply_text})
            messages.append(
                {
                    "role": "user",
                    "content": f"SQL error: {e}\nFix the SQL and return only the corrected SELECT statement.",
                }
            )

    return None, None


def create_chart(plan_item: dict, rows: list[dict], chart_path: str) -> bool:
    if not rows or len(list(rows[0].keys())) < 2:
        return False

    cols = list(rows[0].keys())
    x_col, y_col = cols[0], cols[1]
    x_vals = [str(r[x_col]) for r in rows]
    y_vals = [float(r[y_col]) if r[y_col] is not None else 0.0 for r in rows]

    chart_type = plan_item["chart_type"]
    title = plan_item["title"]
    x_label = plan_item.get("x_label", x_col)
    y_label = plan_item.get("y_label", y_col)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    bar_colors = (PALETTE * ((len(x_vals) // len(PALETTE)) + 1))[: len(x_vals)]

    if chart_type == "pie":
        ax.pie(y_vals, labels=x_vals, colors=bar_colors, autopct="%1.1f%%", startangle=90)
        ax.set_aspect("equal")

    elif chart_type == "line":
        ax.plot(x_vals, y_vals, marker="o", color=PALETTE[0], linewidth=2, markersize=5)
        ax.fill_between(range(len(x_vals)), y_vals, alpha=0.1, color=PALETTE[0])
        ax.set_xticks(range(len(x_vals)))
        ax.set_xticklabels(x_vals, rotation=45, ha="right", fontsize=8)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    elif chart_type == "horizontal_bar":
        bars = ax.barh(x_vals, y_vals, color=bar_colors)
        ax.set_xlabel(y_label)
        ax.set_ylabel(x_label)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        for bar, val in zip(bars, y_vals):
            ax.text(
                bar.get_width() * 1.005,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f}",
                va="center",
                fontsize=8,
            )
        ax.grid(axis="x", linestyle="--", alpha=0.4)

    elif chart_type == "scatter":
        try:
            x_num = [float(v) for v in x_vals]
        except ValueError:
            x_num = list(range(len(x_vals)))
        ax.scatter(x_num, y_vals, color=PALETTE[0], alpha=0.7, s=60, edgecolors="white", linewidths=0.5)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.grid(linestyle="--", alpha=0.4)

    else:  # bar (default)
        bars = ax.bar(x_vals, y_vals, color=bar_colors)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xticks(range(len(x_vals)))
        ax.set_xticklabels(x_vals, rotation=45, ha="right", fontsize=8)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    return True


def generate_insights(client: Anthropic, plan_item: dict, rows: list[dict]) -> str:
    sample = rows[:10]
    data_summary = json.dumps(sample, ensure_ascii=False, default=str, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system="You are a data analyst. Write concise, specific, actionable insights.",
        messages=[
            {
                "role": "user",
                "content": f"""Chart: {plan_item['title']}
Question: {plan_item['description']}
Data ({len(rows)} total rows, showing first 10):
{data_summary}

Write exactly 3 bullet-point insights. Be specific with numbers from the data. Max 120 words total.
Format each bullet starting with "- ".""",
            }
        ],
    )
    return next(b.text for b in response.content if isinstance(b, TextBlock)).strip()


def execute_plan() -> list[dict]:
    os.makedirs(CHARTS_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "context.json"), encoding="utf-8") as f:
        context = json.load(f)
    with open(os.path.join(OUTPUT_DIR, "plan.json"), encoding="utf-8") as f:
        plan = json.load(f)

    db_name = list(context["databases"].keys())[0]
    schema_text = format_schema_for_prompt(context)
    client = Anthropic()

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS
    )

    results = []
    plan_items = plan.get("plan", [])

    for i, item in enumerate(plan_items):
        print(f"\n[Step 2] {i + 1}/{len(plan_items)}: {item['title']}")
        chart_path = os.path.join(CHARTS_DIR, f"{i + 1:02d}_{slugify(item['title'])}.png")

        result = {
            "index": i,
            "title": item["title"],
            "chart_type": item["chart_type"],
            "description": item["description"],
            "x_label": item.get("x_label", ""),
            "y_label": item.get("y_label", ""),
            "sql": None,
            "rows_count": 0,
            "chart_path": chart_path,
            "insights": "",
            "error": None,
        }

        sql, rows = generate_sql_with_retry(client, item, schema_text, conn, db_name)

        if sql is None:
            result["error"] = "Failed to generate valid SQL after retries"
            print(f"  SKIP: {result['error']}")
        else:
            result["sql"] = sql
            result["rows_count"] = len(rows)

            if create_chart(item, rows, chart_path):
                print(f"  Chart saved: {chart_path}")
            else:
                result["error"] = "Insufficient data for chart"
                print(f"  SKIP chart: {result['error']}")

            result["insights"] = generate_insights(client, item, rows)

        results.append(result)

    conn.close()

    with open(os.path.join(OUTPUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    ok = sum(1 for r in results if not r["error"])
    print(f"\n[Step 2] Done: {ok}/{len(results)} charts generated")
    return results


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    execute_plan()
