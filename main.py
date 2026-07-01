from fastapi import FastAPI, HTTPException
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

@app.get("/applications/{id}")
def get_application(id: int):
    for application in applications:
        if application["id"] == id:
            return application
    
    raise HTTPException(
        status_code = 404,
        detail = "Application not found"
    )

@app.put("/applications/{id}")
def update_application(id: int, updated_application: Application):
    for application in applications:
        if application["id"] == id:
            application["company"] = updated_application.company
            application["role"] = updated_application.role
            application["status"] = updated_application.status
            return application
    
    raise HTTPException(
        status_code = 404,
        detail = "Application not found"
    )

@app.delete("/applications/{id}")
def delete_application(id: int):
    for application in applications:
        if application["id"] == id:
            applications.remove(application)
            return {"message" : "Application deleted successfully"}
    
    raise HTTPException(
        status_code = 404,
        detail = "Application not found"
    )