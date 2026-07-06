import os
import sqlite3
import psycopg2
import psycopg2.extras

DATABASE_NAME = "internship_tracker.db"
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        connection = psycopg2.connect(DATABASE_URL)
        return connection

    connection = sqlite3.connect(DATABASE_NAME, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def rows_to_dicts(rows):
    return [dict(row) for row in rows]