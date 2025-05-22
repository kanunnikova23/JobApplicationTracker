# Starts the app. Registers routes.
from fastapi import FastAPI

from app.api.routes import job_routes, user_routes
from app.db import engine
from app.models import job_models

from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from app.exceptions import (
    AppBaseException, generic_app_exception_handler,
    http_exception_handler, integrity_error_handler,
    validation_error_handler,
    fallback_exception_handler, DuplicateUsernameException,
    DuplicateEmailException, UserNotFoundException,
    JobApplicationNotFoundException, duplicate_field_handler,
    NoResultFound, no_result_found_handler,
)

app = FastAPI()

# Create all tables in the DB based on models if they don’t exist.
job_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Job Application Tracker is up and running 🚀"}


# Include the job routes under /applications and under /users
app.include_router(job_routes.router, prefix="/applications", tags=["Applications"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])

# Register custom exception handlers — order matters: specific first
# duplicate data
app.add_exception_handler(DuplicateEmailException, duplicate_field_handler)
app.add_exception_handler(DuplicateUsernameException, duplicate_field_handler)
# no result found
app.add_exception_handler(UserNotFoundException, no_result_found_handler)
app.add_exception_handler(JobApplicationNotFoundException, no_result_found_handler)

# Base custom exception handler for others inheriting from AppBaseException
app.add_exception_handler(AppBaseException, generic_app_exception_handler)

# Built-in and SQLAlchemy exceptions
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(NoResultFound, no_result_found_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

# Catch-all fallback
app.add_exception_handler(Exception, fallback_exception_handler)
