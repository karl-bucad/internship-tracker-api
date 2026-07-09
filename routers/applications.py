from fastapi import APIRouter, HTTPException, Depends
from database import get_connection, DATABASE_URL
from models import Application
from security import get_current_user_id

router = APIRouter()

APPLICATION_COLUMNS = """
id, company, role, status, notes, applied_date, job_url, user_id
"""


def application_row_to_dict(row):
    if DATABASE_URL:
        return {
            "id": row[0],
            "company": row[1],
            "role": row[2],
            "status": row[3],
            "notes": row[4],
            "applied_date": row[5],
            "job_url": row[6],
            "user_id": row[7],
        }

    return dict(row)


@router.get("/applications")
def get_applications(current_user_id: int = Depends(get_current_user_id)):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            f"""
            SELECT {APPLICATION_COLUMNS}
            FROM applications
            WHERE user_id = %s
            """,
            (current_user_id,)
        )
    else:
        cursor.execute(
            f"""
            SELECT {APPLICATION_COLUMNS}
            FROM applications
            WHERE user_id = ?
            """,
            (current_user_id,)
        )

    rows = cursor.fetchall()
    connection.close()

    return [application_row_to_dict(row) for row in rows]


@router.post("/applications")
def add_application(
    application: Application,
    current_user_id: int = Depends(get_current_user_id)
):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            INSERT INTO applications (company, role, status, notes, applied_date, job_url, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                application.company,
                application.role,
                application.status,
                application.notes,
                application.applied_date,
                application.job_url,
                current_user_id
            )
        )
        new_id = cursor.fetchone()[0]
    else:
        cursor.execute(
            """
            INSERT INTO applications (company, role, status, notes, applied_date, job_url, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                application.company,
                application.role,
                application.status,
                application.notes,
                application.applied_date,
                application.job_url,
                current_user_id
            )
        )
        new_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "id": new_id,
        "company": application.company,
        "role": application.role,
        "status": application.status,
        "notes": application.notes,
        "applied_date": application.applied_date,
        "job_url": application.job_url
    }


@router.get("/applications/{id}")
def get_application(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            f"""
            SELECT {APPLICATION_COLUMNS}
            FROM applications
            WHERE id = %s AND user_id = %s
            """,
            (id, current_user_id)
        )
    else:
        cursor.execute(
            f"""
            SELECT {APPLICATION_COLUMNS}
            FROM applications
            WHERE id = ? AND user_id = ?
            """,
            (id, current_user_id)
        )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application_row_to_dict(row)


@router.put("/applications/{id}")
def update_application(
    id: int,
    updated_application: Application,
    current_user_id: int = Depends(get_current_user_id)
):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            UPDATE applications
            SET company = %s, role = %s, status = %s, notes = %s, applied_date = %s, job_url = %s
            WHERE id = %s AND user_id = %s
            """,
            (
                updated_application.company,
                updated_application.role,
                updated_application.status,
                updated_application.notes,
                updated_application.applied_date,
                updated_application.job_url,
                id,
                current_user_id
            )
        )
    else:
        cursor.execute(
            """
            UPDATE applications
            SET company = ?, role = ?, status = ?, notes = ?, applied_date = ?, job_url = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                updated_application.company,
                updated_application.role,
                updated_application.status,
                updated_application.notes,
                updated_application.applied_date,
                updated_application.job_url,
                id,
                current_user_id
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
        "status": updated_application.status,
        "notes": updated_application.notes,
        "applied_date": updated_application.applied_date,
        "job_url": updated_application.job_url
    }


@router.delete("/applications/{id}")
def delete_application(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            """
            DELETE FROM applications
            WHERE id = %s AND user_id = %s
            """,
            (id, current_user_id)
        )
    else:
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
            status_code=404,
            detail="Application not found"
        )

    connection.close()

    return {
        "message": "Application deleted successfully"
    }