from database import get_connection, DATABASE_URL

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                hashed_password TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                company TEXT,
                role TEXT,
                status TEXT,
                notes TEXT DEFAULT '',
                applied_date TEXT DEFAULT '',
                job_url TEXT DEFAULT '',
                user_id INTEGER REFERENCES users(id)
            )
            """
        )
    else:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                hashed_password TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                role TEXT,
                status TEXT,
                notes TEXT DEFAULT '',
                applied_date TEXT DEFAULT '',
                job_url TEXT DEFAULT '',
                user_id INTEGER
            )
            """
        )

    connection.commit()
    connection.close()