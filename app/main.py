# Starts the app. Registers routes.
from fastapi import FastAPI

from app.api.routes import job_routes
from app.db import engine
from app.models import job_models

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


from app.exceptions import (
    AppBaseException, generic_app_exception_handler,
    http_exception_handler, integrity_error_handler,
    no_result_found_handler, validation_error_handler
)

app = FastAPI()

# Create all tables in the DB based on models if they don’t exist.
job_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Job Application Tracker is up and running 🚀"}


# Include the job routes under /applications
app.include_router(job_routes.router, prefix="/applications", tags=["Applications"])

# Register custom exception handlers
app.add_exception_handler(AppBaseException, generic_app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(NoResultFound, no_result_found_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
