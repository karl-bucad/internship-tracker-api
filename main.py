from fastapi import FastAPI, HTTPException, Depends
from database import get_connection
from models import Application, User, LoginUser
from fastapi.security import OAuth2PasswordRequestForm
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id
)
from routers.applications import router as applications_router
from routers.auth import router as auth_router

app = FastAPI()
app.include_router(applications_router)
app.include_router(auth_router)

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