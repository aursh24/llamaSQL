def build_prompt(schema_text, question, history=None):
    """
    Construct the full message list for Ollama chat.
    
    Args:
        schema_text: Auto-discovered database schema string.
        question: The user's natural language question.
        history: Optional list of previous message dicts [{"role": ..., "content": ...}].
    
    Returns:
        list: Messages list ready for ollama.chat().
    """
    system_content = f"""You are an expert MySQL developer.

Database Schema:
{schema_text}

Rules:
- Return ONLY valid MySQL queries.
- Do not explain anything.
- Do not wrap the SQL in markdown code blocks.
- Do not include any text before or after the SQL query.
- Always end the query with a semicolon.
"""

    messages = [{"role": "system", "content": system_content}]

    # Inject conversation history for context continuity
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": question})

    return messages
