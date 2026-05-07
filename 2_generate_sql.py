"""
Step 2: Use Claude API with the schema context to generate SQL queries
that produce aggregated, meaningful indicators from the data.
"""
import json
import os
import re
from anthropic import Anthropic
from utils import format_schema_for_prompt

OUTPUT_DIR = "output"


def generate_sql():
    ctx_path = os.path.join(OUTPUT_DIR, "context.json")
    with open(ctx_path, "r", encoding="utf-8") as f:
        context = json.load(f)

    schema_text = format_schema_for_prompt(context)

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "You are a SQL expert. Generate practical aggregated SQL queries "
            "based on the provided MySQL database schema."
        ),
        messages=[
            {
                "role": "user",
                "content": f"""Based on this MySQL database schema, generate 6-8 SQL queries
that provide useful aggregated insights and key metrics.

SCHEMA:
{schema_text}

Requirements for each query:
- Use aggregation: COUNT, SUM, AVG, MIN, MAX, GROUP BY, ORDER BY
- Be practically useful for understanding patterns in the data
- Add a short comment explaining what it measures
- Must be compatible with MySQL ONLY_FULL_GROUP_BY mode: every non-aggregated expression in SELECT must appear verbatim in GROUP BY (do not rely on functional dependency inference)

Return ONLY valid JSON in this exact format:
{{
  "queries": [
    {{"description": "...", "sql": "SELECT ..."}},
    ...
  ]
}}""",
            }
        ],
    )

    content = response.content[0].text
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    queries_data = json.loads(json_match.group()) if json_match else {"raw_response": content}

    out_path = os.path.join(OUTPUT_DIR, "generated_queries.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(queries_data, f, indent=2, ensure_ascii=False)

    if "queries" in queries_data:
        print(f"[Step 2] Generated {len(queries_data['queries'])} SQL queries:")
        for i, q in enumerate(queries_data["queries"], 1):
            print(f"  {i}. {q['description']}")
    else:
        print("[Step 2] Raw response saved.")

    return queries_data


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    generate_sql()
