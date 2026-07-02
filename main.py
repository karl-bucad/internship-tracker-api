from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection

app = FastAPI()

class Application(BaseModel):
    company: str
    role: str
    status: str

applications = [
    {
        "id": 1,
        "company": "Google",
        "role": "Software Engineering Intern",
        "status": "Applied"
    },
    {
        "id": 2,
        "company": "Microsoft",
        "role": "Software Engineering Intern",
        "status": "Interview"
    }
]

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