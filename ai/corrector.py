from ai.llm import ask_llm
from ai.cleaner import clean_sql
from ai.prompt import build_prompt


def auto_correct(question, schema_text, failed_sql, error_message, history=None, max_retries=3):
    """
    Attempt to fix a failed SQL query by sending the error back to the LLM.
    
    Args:
        question: Original user question.
        schema_text: Database schema text.
        failed_sql: The SQL that failed.
        error_message: The error from MySQL.
        history: Conversation history.
        max_retries: Maximum correction attempts (default 3).
    
    Returns:
        tuple: (corrected_sql, columns, rows) on success, or (None, None, None) on failure.
    """
    from database.executor import execute_query
    from security.validator import validate_sql, UnsafeSQLError

    current_sql = failed_sql
    current_error = str(error_message)

    for attempt in range(1, max_retries + 1):
        print(f"\n Self-correction attempt {attempt}/{max_retries}...")

        correction_prompt = f"""The following SQL query failed with an error.

Failed SQL:
{current_sql}

Error:
{current_error}

Original question: {question}

Database Schema:
{schema_text}

Please generate a corrected SQL query.
Return ONLY the corrected SQL query.
Do not explain anything.
Do not wrap in markdown code blocks.
"""

        messages = [
            {"role": "system", "content": "You are an expert MySQL developer. Fix the SQL query based on the error. Return ONLY the corrected SQL."}
        ]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": correction_prompt})

        raw_response = ask_llm(messages)
        corrected_sql = clean_sql(raw_response)

        print(f"   Corrected SQL: {corrected_sql}")

        
        try:
            validate_sql(corrected_sql)
        except UnsafeSQLError as e:
            print(f"   [ERROR] Validation failed: {e}")
            current_error = str(e)
            current_sql = corrected_sql
            continue

        
        try:
            columns, rows = execute_query(corrected_sql)
            print(f"   [SUCCESS] Correction successful!")
            return corrected_sql, columns, rows
        except Exception as e:
            print(f"   [ERROR] Still failing: {e}")
            current_error = str(e)
            current_sql = corrected_sql

    print(f"\n[ERROR] All {max_retries} correction attempts failed.")
    return None, None, None
