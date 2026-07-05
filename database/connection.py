import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

ACTIVE_DATABASE = os.getenv("DB_NAME", "copilot_demo")


def get_connection():
    """Create and return a MySQL database connection."""
    config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    if ACTIVE_DATABASE:
        config["database"] = ACTIVE_DATABASE
        
    return mysql.connector.connect(**config)


def set_active_database(db_name):
    """Update the active database for future connections."""
    global ACTIVE_DATABASE
    ACTIVE_DATABASE = db_name
