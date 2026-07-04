from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from models import Application
from security import get_current_user_id

router = APIRouter()

@router.get("/applications")
def get_applications(current_user_id: int = Depends(get_current_user_id)):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM applications WHERE user_id = ?",
        (current_user_id,)
    )
    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

@router.post("/applications")
def add_application(
    application: Application,
    current_user_id: int = Depends(get_current_user_id)):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO applications (company, role, status, user_id)
        VALUES (?, ?, ?, ?)
        """,
        (application.company, application.role, application.status, current_user_id)
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

@router.get("/applications/{id}")
def get_application(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
    ):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (id, current_user_id)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail = "Application not found"
        )

    return dict(row)

@router.put("/applications/{id}")
def update_application(
    id: int, 
    updated_application: Application,
    current_user_id: int = Depends(get_current_user_id)
    ):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE applications
        SET company = ?, role = ?, status = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            updated_application.company,
            updated_application.role,
            updated_application.status,
            id,
            current_user_id
        )
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
        "id": id,
        "company": updated_application.company,
        "role": updated_application.role,
        "status": updated_application.status
    }

@router.delete("/applications/{id}")
def delete_application(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
    ):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM applications
        WHERE id = ? AND user_id = ?
        """,
        (id, current_user_id)
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