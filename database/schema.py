from database.connection import get_connection


def get_all_tables(connection):
    """Return a list of all table names in the connected database."""
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_table_columns(connection, table_name):
    """
    Return column details for a given table via DESCRIBE.
    
    Returns:
        list of dicts with keys: name, type, null, key, default, extra
    """
    cursor = connection.cursor()
    cursor.execute(f"DESCRIBE `{table_name}`")
    columns = []
    for row in cursor.fetchall():
        columns.append({
            "name": row[0],
            "type": row[1],
            "null": row[2],
            "key": row[3],
            "default": row[4],
            "extra": row[5]
        })
    cursor.close()
    return columns


def get_schema_text(connection=None):
    """
    Build a complete schema description string for all tables.
    
    If no connection is provided, creates one automatically.
    
    Returns:
        str: Formatted schema text for prompt injection.
    
    Example output:
        Table: employees
          - id (int, PRI, NOT NULL)
          - name (varchar(100), NOT NULL)
          - email (varchar(255))
    """
    close_conn = False
    if connection is None:
        from database.connection import get_connection
        connection = get_connection()
        close_conn = True

    try:
        tables = get_all_tables(connection)
        schema_parts = []

        for table in tables:
            columns = get_table_columns(connection, table)
            col_lines = []
            for col in columns:
                parts = [col["type"]]
                if col["key"]:
                    parts.append(col["key"])
                if col["null"] == "NO":
                    parts.append("NOT NULL")
                col_lines.append(f"  - {col['name']} ({', '.join(parts)})")

            schema_parts.append(f"Table: {table}\n" + "\n".join(col_lines))

        return "\n\n".join(schema_parts)

    finally:
        if close_conn:
            connection.close()
