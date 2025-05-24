import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

logger = logging.getLogger(__name__)  # Ensure logger is configured elsewhere


# Base Exception Class
class AppBaseException(Exception):
    status_code = 500
    detail = "Something went wrong"

    def __init__(self, status_code: int = None, detail: str = None):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = detail
        logger.error(f"🚨 {self.__class__.__name__}: {self.detail}")  # Consistent message


#  Domain-Specific Exceptions
class DuplicateUsernameException(AppBaseException):
    def __init__(self, username: str):
        super().__init__(
            status_code=400,
            detail=f"Username '{username}' is already taken 🚫"
        )


class DuplicateEmailException(AppBaseException):
    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            detail=f"Email '{email}' is already taken 🚫"
        )


class JobApplicationNotFoundException(AppBaseException):
    def __init__(self, application_id: int):
        super().__init__(
            status_code=404,
            detail=f"Job Application with id {application_id} was not found 💀"
        )


class UserNotFoundException(AppBaseException):
    def __init__(self, username: str):
        super().__init__(
            status_code=404,
            detail=f"User '{username}' not found 👻"
        )


# Add more here as needed later (e.g., AuthException, TokenExpiredException, etc.)

# Custom Exception Handlers
async def generic_app_exception_handler(request: Request, exc: AppBaseException):
    logger.error(f"🚨 [{request.method}] {request.url} → {exc.__class__.__name__}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"⚠️ HTTPException at [{request.method}] {request.url} → {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"🚫 IntegrityError at [{request.method}] {request.url} → {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Database integrity error. Possibly duplicate or invalid data."}
    )


async def no_result_found_handler(request: Request, exc: NoResultFound):
    logger.warning(f"🔍 NoResultFound at [{request.method}] {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": "Requested item not found in the database."}
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    logger.warning(f"⚠️ ValidationError at [{request.method}] {request.url} → {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


async def fallback_exception_handler(request: Request, exc: Exception):
    logger.exception(f"🔥 Unhandled exception at [{request.method}] {request.url} → {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected server error: {type(exc).__name__} - {str(exc)}"}
    )


async def duplicate_field_handler(request: Request, exc: AppBaseException):
    logger.error(f"Duplicate field error: {exc.detail}")
    return JSONResponse(status_code=409, content={"detail": exc.detail})
