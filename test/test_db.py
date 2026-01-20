import json
import os
import sys
import tempfile
import unittest

import pytest

# Add the 'src' folder to import db.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from db import get_connection, save_portfolio, delete_portfolio, init_db

def print_table_data(table_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns_info = cursor.fetchall()
        columns = [col['name'] for col in columns_info]
        print(f"\nTable: {table_name}")
        print("Columns:", ", ".join(columns))
        print("-" * 100)
        
        # Get all rows
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                row_str = " | ".join(
                    f"{col}: {row[col] if col != 'metadata_json' else json.dumps(json.loads(row[col]), indent=0) if row[col] else '{}'}"
                    for col in columns
                )
                print(row_str)
                print("-" * 100)
        else:
            print("No rows found.")
            print("-" * 100)

def main():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Insert one dummy scan
        cursor.execute("INSERT INTO scans (project, notes) VALUES (?, ?)", 
                       ("DemoProject", "Dummy scan for testing"))
        scan_id = cursor.lastrowid

        # Insert two dummy files for that scan
        dummy_files = [
            {
                "file_name": "example1.txt",
                "file_path": "C:/Users/tyler/example1.txt",
                "file_extension": ".txt",
                "file_size": 1024,
                "created_at": "2025-10-26 12:00:00",
                "modified_at": "2025-10-26 12:30:00",
                "owner": "Tyler",
                "metadata_json": json.dumps({"encoding": "utf-8", "lines": 100})
            },
            {
                "file_name": "example2.pdf",
                "file_path": "C:/Users/tyler/docs/example2.pdf",
                "file_extension": ".pdf",
                "file_size": 2048,
                "created_at": "2025-10-25 10:00:00",
                "modified_at": "2025-10-25 11:00:00",
                "owner": "Tyler",
                "metadata_json": json.dumps({"pages": 12, "author": "Tyler Cummings"})
            }
        ]

        for file in dummy_files:
            cursor.execute("""
                INSERT INTO files
                (scan_id, file_name, file_path, file_extension, file_size, created_at, modified_at, owner, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (scan_id, file["file_name"], file["file_path"], file["file_extension"], file["file_size"],
                  file["created_at"], file["modified_at"], file["owner"], file["metadata_json"]))
        conn.commit()

        # Print both tables neatly
        for table_name in ["scans", "files"]:
            print_table_data(table_name)

# Test suite for portfolio database functions
class TestPortfolioDB(unittest.TestCase):
    
    # Set up a temporary database for testing
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.environ['FILE_DATA_DB_PATH'] = self.db_path
        init_db()

    # Clean up the temporary database after tests
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        if 'FILE_DATA_DB_PATH' in os.environ:
            del os.environ['FILE_DATA_DB_PATH']

    # Tests that saving and deleting of a portfolio works correctly
    def test_save_and_delete_portfolio(self):
        metadata = {'project_count': 3, 'confidence_level': 'high'}
        portfolio_id = save_portfolio('testuser', '/path/to/portfolio.md', metadata, '2026-01-12 10:00:00Z')

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM portfolios WHERE id = ?", (portfolio_id,))
            row = cur.fetchone()
            self.assertEqual(row['username'], 'testuser')
            self.assertEqual(json.loads(row['metadata_json'])['project_count'], 3)

        self.assertTrue(delete_portfolio(portfolio_id))
        self.assertFalse(delete_portfolio(99999))

    # Tests that save_portfolio() validates required fields before saving
    def test_save_portfolio_validation(self):
        with self.assertRaises(ValueError):
            save_portfolio('', '/path/to/portfolio.md')
        with self.assertRaises(ValueError):
            save_portfolio('testuser', '')
        with self.assertRaises(ValueError):
            delete_portfolio(None)

if __name__ == "__main__":
    main()
