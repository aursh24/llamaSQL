from database.connection import get_connection, set_active_database
import re


def execute_query(sql):
    """
    Execute a SQL query and return (columns, rows).
    Handles multi-statement queries, commits for DML/DDL, and database switching.
    
    Returns:
        tuple: (list of column names, list of row tuples)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        
        use_match = re.search(r"USE\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
        if use_match:
            db_name = use_match.group(1)
            set_active_database(db_name)

        
        
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        
        all_rows = []
        columns = []
        
        for statement in statements:
            cursor.execute(statement)
            if cursor.description is not None:
                
                all_rows.extend(cursor.fetchall())
                columns = [desc[0] for desc in cursor.description]
            else:
                
                conn.commit()

        if not columns and not all_rows:
            return ["Status"], [("Query executed successfully.",)]
            
        return columns, all_rows

    except Exception as e:
        raise e

    finally:
        cursor.close()
        conn.close()
