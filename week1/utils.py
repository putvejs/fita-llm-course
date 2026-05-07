def format_schema_for_prompt(context: dict) -> str:
    lines = [f"Server: {context['server']}", f"Extracted: {context['extracted_at']}", ""]
    for db_name, tables in context["databases"].items():
        lines.append(f"Database: {db_name}")
        for table_name, info in tables.items():
            lines.append(f"  Table: {table_name} ({info['row_count']} rows)")
            for col in info["columns"]:
                constraint = ""
                if col["key"] == "PRI":
                    constraint = " [PRIMARY KEY]"
                elif col["key"] == "UNI":
                    constraint = " [UNIQUE]"
                elif col["key"] == "MUL":
                    constraint = " [INDEX]"
                nullable = "" if col["nullable"] else " NOT NULL"
                lines.append(f"    - {col['name']}: {col['type']}{nullable}{constraint}")
            for fk in info.get("foreign_keys", []):
                lines.append(
                    f"    FK: {fk['column']} -> {fk['references_table']}.{fk['references_column']}"
                )
        lines.append("")
    return "\n".join(lines)
