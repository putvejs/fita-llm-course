"""
Step 1: Read context.md and use Claude to generate a visualization plan.
Outputs: output/plan.md, output/plan.json
"""
import json
import os
import re
from datetime import datetime
from typing import Any

import mysql.connector
from anthropic import Anthropic
from anthropic.types import TextBlock


DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

SYSTEM_DBS = {"information_schema", "mysql", "performance_schema", "sys"}
OUTPUT_DIR = "output"
CONTEXT_MD = os.path.join(os.path.dirname(__file__), "..", "context.md")


def _read_context_md() -> str:
    with open(CONTEXT_MD, encoding="utf-8") as f:
        return f.read()


def explore_schema() -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS
    )
    cursor: Any = conn.cursor()

    cursor.execute("SHOW DATABASES")
    user_dbs = [r[0] for r in cursor.fetchall() if r[0] not in SYSTEM_DBS]

    schema = {}
    for db_name in user_dbs:
        cursor.execute(f"USE `{db_name}`")
        cursor.execute("SHOW TABLES")
        tables = [r[0] for r in cursor.fetchall()]
        schema[db_name] = {}
        for table_name in tables:
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = [
                {"name": c[0], "type": c[1], "nullable": c[2] == "YES", "key": c[3]}
                for c in cursor.fetchall()
            ]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row = cursor.fetchone()
                row_count = row[0] if row else None
            except Exception:
                row_count = None

            cursor.execute(
                """SELECT kcu.COLUMN_NAME, kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME
                   FROM information_schema.KEY_COLUMN_USAGE kcu
                   WHERE kcu.TABLE_SCHEMA = %s AND kcu.TABLE_NAME = %s
                   AND kcu.REFERENCED_TABLE_NAME IS NOT NULL""",
                (db_name, table_name),
            )
            foreign_keys = [
                {"column": f[0], "references_table": f[1], "references_column": f[2]}
                for f in cursor.fetchall()
            ]
            schema[db_name][table_name] = {
                "columns": columns,
                "row_count": row_count,
                "foreign_keys": foreign_keys,
            }

    cursor.close()
    conn.close()

    context = {
        "server": DB_HOST,
        "extracted_at": datetime.now().isoformat(),
        "databases": schema,
    }
    with open(os.path.join(OUTPUT_DIR, "context.json"), "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False, default=str)

    print(f"[Step 1] Schema extracted:")
    for db, tables in schema.items():
        print(f"  {db}: {len(tables)} table(s)")
        for tbl, info in tables.items():
            print(f"    - {tbl}: {len(info['columns'])} columns, {info['row_count']} rows")

    return context


def generate_plan() -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    context_text = _read_context_md()

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are a data visualization expert. Create clear, business-relevant visualization plans.",
        messages=[
            {
                "role": "user",
                "content": f"""Based on the dataset context below, create a visualization plan with 5-7 charts
that reveal the most important business insights.

CONTEXT:
{context_text}

For each chart specify:
- title: concise chart title
- description: what business question this chart answers
- chart_type: one of "bar", "horizontal_bar", "line", "pie", "scatter"
- x_label: label for the x-axis (or "Labels" for pie)
- y_label: label for the y-axis (or "Values" for pie)
- sql_hint: brief hint about the SQL needed (which tables, grouping, aggregation)

Return ONLY valid JSON:
{{
  "plan": [
    {{
      "title": "...",
      "description": "...",
      "chart_type": "bar|horizontal_bar|line|pie|scatter",
      "x_label": "...",
      "y_label": "...",
      "sql_hint": "..."
    }}
  ]
}}""",
            }
        ],
    )

    content = next(b.text for b in response.content if isinstance(b, TextBlock))
    match = re.search(r"\{.*\}", content, re.DOTALL)
    plan = json.loads(match.group()) if match else {"plan": []}

    # Save machine-readable plan
    with open(os.path.join(OUTPUT_DIR, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    # Save human-readable plan.md
    _write_plan_md(plan)

    print(f"[Step 1] Visualization plan ({len(plan.get('plan', []))} charts):")
    for i, item in enumerate(plan.get("plan", []), 1):
        print(f"  {i}. [{item['chart_type']:15s}] {item['title']}")

    return plan


def _write_plan_md(plan: dict) -> None:
    lines = [
        "# Visualization Plan",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"Context: [context.md](../context.md)",
        "",
    ]

    for i, item in enumerate(plan.get("plan", []), 1):
        lines += [
            "---",
            "",
            f"## {i}. {item['title']}",
            "",
            f"**Chart type:** `{item['chart_type']}`  ",
            f"**X axis:** {item['x_label']}  ",
            f"**Y axis:** {item['y_label']}",
            "",
            f"{item['description']}",
            "",
            f"> **SQL hint:** {item['sql_hint']}",
            "",
        ]

    with open(os.path.join(OUTPUT_DIR, "plan.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Step 1] Plan saved -> output/plan.md")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    generate_plan()
