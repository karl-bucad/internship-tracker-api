from fastapi import FastAPI, HTTPException
from database import get_connection
from models import Application, User, LoginUser
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

SECRET_KEY = "temporary-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code = 401,
                detail = "Invalid token"
            )
        
        return user_id
    
    except JWTError:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )

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
def get_applications(current_user_id: int = Depends(get_current_user_id)):
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

    access_token = create_access_token(
        data = {"user_id": row["id"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }