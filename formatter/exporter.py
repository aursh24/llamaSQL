import csv
import os
from datetime import datetime
from openpyxl import Workbook

EXPORT_DIR = "exports"


def _get_export_path(filename):
    """Ensure export directory exists and return full path."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    return os.path.join(EXPORT_DIR, filename)


def _generate_filename(extension):
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"query_result_{timestamp}.{extension}"


def export_csv(columns, rows, filename=None):
    """
    Export query results to a CSV file.
    
    Args:
        columns: List of column names.
        rows: List of row tuples.
        filename: Optional filename. Auto-generated if not provided.
    
    Returns:
        str: Path to the exported file.
    """
    if filename is None:
        filename = _generate_filename("csv")

    path = _get_export_path(filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    return path


def export_excel(columns, rows, filename=None):
    """
    Export query results to an Excel (.xlsx) file.
    
    Args:
        columns: List of column names.
        rows: List of row tuples.
        filename: Optional filename. Auto-generated if not provided.
    
    Returns:
        str: Path to the exported file.
    """
    if filename is None:
        filename = _generate_filename("xlsx")

    path = _get_export_path(filename)

    wb = Workbook()
    ws = wb.active
    ws.title = "Query Results"

    
    ws.append(columns)

    
    for row in rows:
        ws.append(list(row))

    
    for col_idx, col_name in enumerate(columns, 1):
        max_len = len(str(col_name))
        for row in rows:
            cell_len = len(str(row[col_idx - 1])) if col_idx - 1 < len(row) else 0
            max_len = max(max_len, cell_len)
        ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else "A"].width = min(max_len + 2, 50)

    wb.save(path)
    return path
