import sqlite3
from PyQt5.QtWidgets import QMessageBox

class Database:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            self.create_table()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", str(e))

    def create_table(self):
        """Create the 'books' table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            genre TEXT,
            year INTEGER
        );
        """
        self.execute_query(create_table_query)

    def execute_query(self, query, parameters=None):
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", str(e))

    def fetch_all(self, query, parameters=None):
        """Fetch all results from a SELECT query."""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Database Error", str(e))
            return []

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
