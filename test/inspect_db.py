# scripts/inspect_db.py
import os
import sys
import sqlite3

# Add src to import path so db.py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from db import DB_PATH  # use the repo's DB path constant

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("Tables:")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(" -", row['name'])

print("\nRecent scans:")
for row in cur.execute("SELECT id, scanned_at, project, notes FROM scans ORDER BY scanned_at DESC LIMIT 10"):
    print(dict(row))


print("\n20 most recently modified files:")
for row in cur.execute("SELECT id, file_name, file_path, file_extension, file_size, modified_at FROM files ORDER BY datetime(modified_at) DESC NULLS LAST LIMIT 20"):
     print(dict(row))

conn.close()