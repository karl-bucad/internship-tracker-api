from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from database import get_connection
from models import User
from security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/signup")
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

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (form_data.username,)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid email or password"
        )
    
    if not verify_password(form_data.password, row["hashed_password"]):
        raise HTTPException(
            status_code = 401,
            detail = "Invalid email or password"
        )

    access_token = create_access_token(
        data = {"user_id": row["id"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }