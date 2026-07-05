import sqlite3

DATABASE_NAME = "internship_tracker.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection