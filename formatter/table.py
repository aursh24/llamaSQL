from tabulate import tabulate


def format_table(columns, rows):
    """
    Format query results as a pretty console table.
    
    Args:
        columns: List of column names.
        rows: List of row tuples.
    
    Returns:
        str: Formatted table string.
    """
    if not rows:
        return " No results found."

    return tabulate(rows, headers=columns, tablefmt="pretty")
