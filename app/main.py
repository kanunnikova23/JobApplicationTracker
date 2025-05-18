# Starts the app. Registers routes.
from app.api.routes import job_routes
from app.db.database import engine
from app.models import job_models

from fastapi import FastAPI
from app.api.routes import job_routes

app = FastAPI()

# Creates all tables in the DB based on models if they don’t exist.
job_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Job Application Tracker is up and running 🚀"}


# Include the job routes under /applications
app.include_router(job_routes.router, prefix="/applications", tags=["Applications"])
