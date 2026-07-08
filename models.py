from pydantic import BaseModel

class Application(BaseModel):
    company: str
    role: str
    status: str
    notes: str = ""
    applied_date: str = ""
    job_url: str = ""

class User(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str