from fastapi import FastAPI
from pydantic import BaseModel

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
    return applications

@app.post("/applications")
def add_application(application: Application):
    new_id = applications[-1]["id"] + 1

    new_application = {
     "id": new_id,
     "company": application.company,
     "role": application.role,
     "status": application.status
    }

    applications.append(new_application)

    return new_application