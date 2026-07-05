import json
import os
from datetime import datetime


class ConversationHistory:

    def __init__(self, max_turns=10):
        self.messages = []
        self.max_turns = max_turns

    def add_user(self, content):
        """Record a user message."""
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant(self, content):
        """Record an assistant (SQL) response."""
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def get_messages(self):
        """Return conversation history as a list of message dicts."""
        return self.messages.copy()

    def clear(self):
        """Clear all conversation history."""
        self.messages = []
        print(" Conversation history cleared.")

    def _trim(self):
        """Keep only the last N turns (each turn = 1 user + 1 assistant message)."""
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]


class QueryLogger:
    """
    Logs every query execution to a JSON file for history tracking.
    
    Stores: timestamp, user question, generated SQL, execution time,
    row count, and success status.
    """

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "history.json")

    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        if not os.path.exists(self.LOG_FILE):
            with open(self.LOG_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def log(self, question, sql, execution_time_ms, row_count, success):
        """
        Log a query execution.
        
        Args:
            question: User's natural language question.
            sql: Generated SQL query.
            execution_time_ms: Execution time in milliseconds.
            row_count: Number of rows returned.
            success: Whether execution succeeded.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "sql": sql,
            "execution_time_ms": round(execution_time_ms, 2),
            "row_count": row_count,
            "success": success
        }

        try:
            with open(self.LOG_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []

        history.append(entry)

        with open(self.LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
