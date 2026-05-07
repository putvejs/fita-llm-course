"""
Step 1: Connect to MySQL server and extract schema metadata.
Saves table names, column names, data types and constraints to output/context.json.
"""
import json
import os
from datetime import datetime
import mysql.connector

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

SYSTEM_DBS = {"information_schema", "mysql", "performance_schema", "sys"}
OUTPUT_DIR = "output"


def explore_schema():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES")
    all_dbs = [row[0] for row in cursor.fetchall()]
    user_dbs = [db for db in all_dbs if db not in SYSTEM_DBS]

    schema = {}

    for db_name in user_dbs:
        cursor.execute(f"USE `{db_name}`")
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        schema[db_name] = {}

        for table_name in tables:
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == "YES",
                    "key": col[3],
                    "default": col[4],
                    "extra": col[5],
                }
                for col in cursor.fetchall()
            ]

            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                row_count = cursor.fetchone()[0]
            except Exception:
                row_count = None

            cursor.execute(
                """
                SELECT kcu.COLUMN_NAME, kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE kcu
                WHERE kcu.TABLE_SCHEMA = %s
                  AND kcu.TABLE_NAME = %s
                  AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                """,
                (db_name, table_name),
            )
            foreign_keys = [
                {"column": fk[0], "references_table": fk[1], "references_column": fk[2]}
                for fk in cursor.fetchall()
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

    out_path = os.path.join(OUTPUT_DIR, "context.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False, default=str)

    print(f"[Step 1] Schema extracted from {len(user_dbs)} database(s):")
    for db, tables in schema.items():
        print(f"  {db}: {len(tables)} table(s)")
        for tbl, info in tables.items():
            print(f"    - {tbl}: {len(info['columns'])} columns, {info['row_count']} rows")

    return context


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    explore_schema()
