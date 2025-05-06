# Starts the app. Registers routes.
from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import job_applications

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(job_applications.router)
