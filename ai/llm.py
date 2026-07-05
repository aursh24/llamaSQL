import os
import ollama
from dotenv import load_dotenv
from ai.prompt import build_prompt
from ai.cleaner import clean_sql

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def generate_sql(question, schema_text, history=None):
    """
    Generate a SQL query from a natural language question.
    
    Args:
        question: The user's natural language question.
        schema_text: Auto-discovered database schema string.
        history: Optional conversation history for context.
    
    Returns:
        str: Clean, executable SQL query.
    """
    messages = build_prompt(schema_text, question, history)

    response = ollama.chat(
        model=MODEL,
        messages=messages
    )

    raw_sql = response["message"]["content"]
    return clean_sql(raw_sql)


def ask_llm(messages):
    """
    Low-level Ollama chat call. Used by corrector and explainer.
    
    Args:
        messages: List of message dicts.
    
    Returns:
        str: Raw LLM response content.
    """
    response = ollama.chat(
        model=MODEL,
        messages=messages
    )
    return response["message"]["content"]
