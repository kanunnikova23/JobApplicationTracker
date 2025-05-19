import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound

logger = logging.getLogger(__name__)  # Ensure logger is configured elsewhere


# Base exception for the app
class AppBaseException(Exception):
    status_code = 500
    detail = "Something went wrong"

    def __init__(self, status_code: int = None, detail: str = None):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = detail
        logger.error(f"🚨 {self.__class__.__name__}: {self.detail}")  # Consistent message


#  Generic handler for any custom job exception
async def generic_app_exception_handler(request: Request, exc: AppBaseException):
    logger.error(f"🚨 [{request.method}] {request.url} → {exc.__class__.__name__}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


#  Specific custom exception — for missing job application
class JobApplicationNotFoundException(AppBaseException):
    def __init__(self, application_id: int):
        msg = f"Job Application with id {application_id} was not found 💀"
        self.application_id = application_id
        super().__init__(status_code=404, detail=msg)
        # No need to log here — already logged in base class


#  Built-in compatible handlers
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
