import time
import sys
import io
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.connection import get_connection
from database.schema import get_schema_text
from database.executor import execute_query
from ai.llm import generate_sql
from ai.corrector import auto_correct
from security.validator import validate_sql, UnsafeSQLError
from formatter.table import format_table
from formatter.exporter import export_csv, export_excel
from memory.history import ConversationHistory, QueryLogger

load_dotenv()


def print_banner():
    """Display the application banner."""
    print("\n" + "=" * 60)
    print("    AI SQL Assistant")
    print("  Natural Language → SQL → Results")
    print("=" * 60)


def print_help():
    """Display available commands."""
    print("""
╔══════════════════════════════════════════════╗
║  Commands:                                   ║
║    • Type a question to query the database   ║
║    • 'clear'   — Clear conversation history  ║
║    • 'schema'  — Show database schema        ║
║    • 'history' — Show query history           ║
║    • 'help'    — Show this help message      ║
║    • 'exit'    — Exit the assistant           ║
╚══════════════════════════════════════════════╝
""")


def handle_export(columns, rows):
    """Prompt user for export option after displaying results."""
    choice = input("\n Export results? (csv / excel / n): ").strip().lower()

    if choice == "csv":
        path = export_csv(columns, rows)
        print(f"   [SUCCESS] Exported to: {path}")
    elif choice == "excel":
        path = export_excel(columns, rows)
        print(f"   [SUCCESS] Exported to: {path}")
    elif choice not in ("no", "n"):
        pass  


def main():
    """Main REPL loop."""
    print_banner()

    
    print("\n Discovering database schema...")
    try:
        conn = get_connection()
        schema_text = get_schema_text(conn)
        conn.close()
        print("[SUCCESS] Schema loaded successfully!\n")
        print(schema_text)
        print()
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        print("   Check your .env file and MySQL connection.")
        return

    
    conversation = ConversationHistory(max_turns=10)
    logger = QueryLogger()

    print_help()

    
    while True:
        try:
            question = input("\n Ask your database: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n Goodbye!")
            break

        if not question:
            continue

        
        if question.lower() == "exit":
            print("\n Goodbye!")
            break
        elif question.lower() == "clear":
            conversation.clear()
            continue
        elif question.lower() == "schema":
            print(f"\n Database Schema:\n{schema_text}")
            continue
        elif question.lower() == "help":
            print_help()
            continue
        elif question.lower() == "history":
            try:
                import json
                with open("logs/history.json", "r", encoding="utf-8") as f:
                    hist = json.load(f)
                if not hist:
                    print(" No query history yet.")
                else:
                    print(f"\n Last 10 queries:")
                    for entry in hist[-10:]:
                        status = "[SUCCESS]" if entry["success"] else "[ERROR]"
                        print(f"  {status} [{entry['timestamp'][:19]}] {entry['question']}")
                        print(f"     SQL: {entry['sql'][:80]}...")
                        print(f"     Rows: {entry['row_count']} | Time: {entry['execution_time_ms']}ms")
                        print()
            except FileNotFoundError:
                print(" No query history yet.")
            continue

        
        print("\n Generating SQL...")
        start_time = time.time()

        try:
            sql = generate_sql(
                question=question,
                schema_text=schema_text,
                history=conversation.get_messages()
            )
        except Exception as e:
            print(f"[ERROR] LLM error: {e}")
            continue

        print(f"\n Generated SQL:\n   {sql}")

        
        try:
            validate_sql(sql)
        except UnsafeSQLError as e:
            print(f"\n{e}")
            logger.log(question, sql, 0, 0, success=False)
            continue

        
        print("\n Executing query...")
        columns = None
        rows = None

        try:
            columns, rows = execute_query(sql)
        except Exception as e:
            print(f"\n[ERROR] SQL Error: {e}")
            print(" Attempting self-correction...")

            corrected_sql, columns, rows = auto_correct(
                question=question,
                schema_text=schema_text,
                failed_sql=sql,
                error_message=str(e),
                history=conversation.get_messages()
            )

            if corrected_sql is not None:
                sql = corrected_sql
            else:
                elapsed = (time.time() - start_time) * 1000
                logger.log(question, sql, elapsed, 0, success=False)
                continue

        elapsed = (time.time() - start_time) * 1000

        
        print(f"\n Results ({len(rows)} row{'s' if len(rows) != 1 else ''} in {elapsed:.0f}ms):\n")
        print(format_table(columns, rows))

        
        logger.log(question, sql, elapsed, len(rows), success=True)

        
        conversation.add_user(question)
        conversation.add_assistant(sql)

        
        if rows:
            handle_export(columns, rows)


if __name__ == "__main__":
    main()