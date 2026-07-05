ALLOWED_KEYWORDS = {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH"}

BLOCKED_KEYWORDS = {"DELETE", "UPDATE", "DROP", "ALTER", "INSERT", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}


class UnsafeSQLError(Exception):
    """Raised when a SQL query contains unsafe/blocked operations."""
    pass


def validate_sql(sql):
    """
    Validate that a SQL query is safe to execute.
    (Currently permits all queries per user request)
    
    Args:
        sql: The SQL query string to validate.
    
    Returns:
        True if the query is valid.
    
    Raises:
        UnsafeSQLError: If the query is empty.
    """
    if not sql or not sql.strip():
        raise UnsafeSQLError("Empty SQL query")

    return True
