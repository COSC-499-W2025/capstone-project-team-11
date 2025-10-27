import sqlite3
import os

# Path to your database file (it will be created in the project root)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'file_data.db')

def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database using init_db.sql."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'init_db.sql')
    with get_connection() as conn:
        with open(sql_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    print("Database initialized successfully at", DB_PATH)

if __name__ == "__main__":
    init_db()
