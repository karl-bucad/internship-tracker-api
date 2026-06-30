from fastapi import FastAPI

app = FastAPI()
applications = [
    {
        "id" : 1,
        "company" : "Google",
        "role" : "Software Engineering Intern",
        "status" : "Applied"
    },
    {
        "id" : 2,
        "company" : "Microsoft",
        "role" : "Software Engineering Intern",
        "status" : "Interview"
    }
]

@app.get("/")
def root():
    return { 
        "message" : "Internship Tracker API"
    }

@app.get("/about")
def about():
    return {
        "creator" : "Karl Bucad",
        "project" : "Internship Tracker API"
    }

@app.get("/applications")
def get_applications():
    return applications