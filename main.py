from fastapi import FastAPI, HTTPException
from database import get_connection
from models import Application, User, LoginUser
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def root():
    return { 
        "message": "Internship Tracker API"
    }

@app.get("/about")
def about():
    return {
        "creator": "Karl Bucad",
        "project": "Internship Tracker API"
    }

@app.get("/applications")
def get_applications():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

@app.post("/applications")
def add_application(application: Application):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO applications (company, role, status)
        VALUES (?, ?, ?)
        """,
        (application.company, application.role, application.status)
    )

    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return {
        "id": new_id,
        "company": application.company,
        "role": application.role,
        "status": application.status
    }

@app.get("/applications/{id}")
def get_application(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM applications WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return dict(row)

@app.put("/applications/{id}")
def update_application(id: int, updated_application: Application):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE applications
        SET company = ?, role = ?, status = ?
        WHERE id = ?
        """,
        (
            updated_application.company,
            updated_application.role,
            updated_application.status,
            id
        )
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    connection.close()

    return {
        "id": id,
        "company": updated_application.company,
        "role": updated_application.role,
        "status": updated_application.status
    }

@app.delete("/applications/{id}")
def delete_application(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM applications
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(
            status_code = 404,
            detail = "Application not found"
        )

    connection.close()

    return {
        "message": "Application deleted successfully"
    }

@app.post("/signup")
def add_user(user: User):
    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (username, email, hashed_password)
        VALUES (?, ?, ?)
        """,
        (user.username, user.email, hashed_password)
    )

    connection.commit()
    new_user_id = cursor.lastrowid
    connection.close()

    return {
        "id": new_user_id,
        "username": user.username,
        "email": user.email
    }

@app.post("/login")
def login_user(user: LoginUser):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (user.email,)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid email or password"
        )
    
    if not verify_password(user.password, row["hashed_password"]):
        raise HTTPException(
            status_code = 401,
            detail = "Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"]
        }
    }