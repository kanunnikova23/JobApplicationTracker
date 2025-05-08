# Starts the app. Registers routes.
from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import job_applications

# Creates all tables in the DB based on models if they don’t exist.
models.Base.metadata.create_all(bind=engine)

# initialize the FastAPI app instance.
app = FastAPI()

# register job_applications API router to the main app.
app.include_router(job_applications.router)


# decorator which defines the route for HTTP GET method at the root path
@app.get("/")
def read_root():
    return {"message": "Job Application Tracker is up and running 🚀"}
