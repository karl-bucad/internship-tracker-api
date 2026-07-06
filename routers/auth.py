import sqlite3
import psycopg2
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import get_connection, DATABASE_URL
from models import User
from security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/signup")
def add_user(user: User):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(user.password)

        if DATABASE_URL:
            cursor.execute(
                """
                INSERT INTO users (username, email, hashed_password)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user.username, user.email, hashed_password)
            )
            new_user_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                """
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
                """,
                (user.username, user.email, hashed_password)
            )
            new_user_id = cursor.lastrowid

        connection.commit()

        return {
            "id": new_user_id,
            "username": user.username,
            "email": user.email
        }

    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    finally:
        connection.close()


@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = get_connection()
    cursor = connection.cursor()

    if DATABASE_URL:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (form_data.username,)
        )
    else:
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (form_data.username,)
        )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if DATABASE_URL:
        hashed_password = row[3]
        user_id = row[0]
    else:
        hashed_password = row["hashed_password"]
        user_id = row["id"]

    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"user_id": user_id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }