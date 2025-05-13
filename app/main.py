# Starts the app. Registers routes.
from app import app
from fastapi import FastAPI
from app.api.routes import job_routes
from app.db.database import engine
from app.models import job_models


# Creates all tables in the DB based on models if they don’t exist.
job_models.Base.metadata.create_all(bind=engine)

# register job_applications API router to the main app.
app.include_router(job_routes.router)


# decorator which defines the route for HTTP GET method at the root path
@app.get("/")
def read_root():
    return {"message": "Job Application Tracker is up and running 🚀"}
