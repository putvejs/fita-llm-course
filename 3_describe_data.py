"""
Step 3: Run the generated SQL queries against MySQL, then use Claude API
to produce a natural-language description and insights report.
"""
import json
import os
import mysql.connector
from anthropic import Anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv
from utils import format_schema_for_prompt

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

OUTPUT_DIR = "output"


def run_queries_and_describe():
    ctx_path = os.path.join(OUTPUT_DIR, "context.json")
    with open(ctx_path, "r", encoding="utf-8") as f:
        context = json.load(f)

    q_path = os.path.join(OUTPUT_DIR, "generated_queries.json")
    with open(q_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    if "queries" not in queries_data:
        print("[Step 3] No queries found. Run step 2 first.")
        return

    db_name = list(context["databases"].keys())[0]
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"USE `{db_name}`")

    results = []
    for q in queries_data["queries"]:
        try:
            cursor.execute(q["sql"])
            rows = cursor.fetchall()
            results.append({
                "description": q["description"],
                "sql": q["sql"],
                "rows": rows[:20],
                "total_rows": len(rows),
            })
            print(f"  OK  {q['description']} ({len(rows)} rows)")
        except Exception as e:
            results.append({"description": q["description"], "sql": q["sql"], "error": str(e)})
            print(f"  ERR {q['description']}: {e}")

    cursor.close()
    conn.close()

    results_path = os.path.join(OUTPUT_DIR, "query_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    schema_text = format_schema_for_prompt(context)
    results_text = _format_results(results)

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=(
            "You are a data analyst. Write clear, insightful descriptions of "
            "database contents based on schema and aggregated query results."
        ),
        messages=[
            {
                "role": "user",
                "content": f"""Using the MySQL schema and aggregated query results below,
write a comprehensive data description report in Markdown.

DATABASE SCHEMA:
{schema_text}

AGGREGATED QUERY RESULTS:
{results_text}

Structure the report as:
1. **Database Overview** — what domain/purpose this database serves
2. **Key Metrics** — the most important numbers from the queries
3. **Notable Patterns & Insights** — patterns or anomalies worth highlighting
4. **Potential Use Cases** — what analyses or decisions this data could support
""",
            }
        ],
    )

    description = next(b.text for b in response.content if isinstance(b, TextBlock))

    report_path = os.path.join(OUTPUT_DIR, "data_description.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Data Description Report\n\n")
        f.write(description)

    print(f"[Step 3] Report saved to {report_path}")
    return description


def _format_results(results):
    lines = []
    for r in results:
        if "error" in r:
            lines.append(f"Query: {r['description']}\nError: {r['error']}\n")
        else:
            lines.append(f"Query: {r['description']}")
            lines.append(f"SQL: {r['sql']}")
            lines.append(f"Result ({r['total_rows']} rows, showing up to 5):")
            for row in r["rows"][:5]:
                lines.append(f"  {dict(row)}")
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    run_queries_and_describe()
