from fastapi import FastAPI

app = FastAPI()

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
def applications():
    return []