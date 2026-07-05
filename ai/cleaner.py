import re


def clean_sql(raw_response):
    """
    Clean LLM response to extract executable SQL.
    
    Handles:
        - Markdown code fences (```sql ... ```)
        - Leading/trailing explanatory text
        - Inline comments
        - Extra whitespace
    
    Args:
        raw_response: Raw string from LLM.
    
    Returns:
        str: Clean, executable SQL query.
    """
    sql = raw_response.strip()

    # 1. Extract SQL from markdown code fences if present
    fence_pattern = r"```(?:sql)?\s*\n?(.*?)```"
    fence_match = re.search(fence_pattern, sql, re.DOTALL | re.IGNORECASE)
    if fence_match:
        sql = fence_match.group(1).strip()

    # 2. Remove lines that are purely comments
    lines = sql.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if stripped.startswith("#"):
            continue
        cleaned_lines.append(line)
    sql = "\n".join(cleaned_lines).strip()

    # 3. Remove leading explanatory text before the first SQL keyword
    sql_keywords = r"(SELECT|SHOW|DESCRIBE|EXPLAIN|WITH)"
    keyword_match = re.search(sql_keywords, sql, re.IGNORECASE)
    if keyword_match:
        sql = sql[keyword_match.start():]

    # 4. Remove trailing text after the last semicolon
    last_semicolon = sql.rfind(";")
    if last_semicolon != -1:
        sql = sql[:last_semicolon + 1]

    # 5. Clean up extra whitespace
    sql = sql.strip()

    return sql
