from typing import Optional

from fastapi import APIRouter, Depends, Body, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import job_crud
from app.api.deps import get_async_db
from app.schemas import job_schemas

router = APIRouter(
    tags=["Applications"]
)


@router.post("/", response_model=job_schemas.JobAppOut, status_code=201)
async def create_application(job: job_schemas.JobAppCreate, db: AsyncSession = Depends(get_async_db)):
    return await job_crud.create_job_app(db=db, job=job)


@router.get("/", response_model=list[job_schemas.JobAppOut])
async def read_applications(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_db)):
    return await job_crud.get_job_apps(db, skip=skip, limit=limit)


@router.get("/filter", response_model=list[job_schemas.JobAppOut])
async def filter_job_apps(
        company: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
        sort_by: str = Query("applied_date", regex="^(applied_date|updated_at|status)$"),
        order: str = Query("desc", regex="^(asc|desc)$"),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_async_db),
        search_query: Optional[str] = Query(None, alias="q")
):
    return await job_crud.filter_job_apps(
        db=db,
        company=company,
        status=status,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
        search_query=search_query
    )


@router.get("/{id}", response_model=job_schemas.JobAppOut)
async def read_jobs_by_id(id: int, db: AsyncSession = Depends(get_async_db)):
    job_app = await job_crud.get_job_app_by_id(db, id)
    return job_app


@router.put("/{id}", response_model=job_schemas.JobAppOut, status_code=200)
async def update_jobs_by_id(
        id: int,
        # This injects a SQLAlchemy database session using FastAPIs dependency injection system.
        db: AsyncSession = Depends(get_async_db),
        # This is the body of the request, expected to be JSON.
        # FastAPI will parse it using the JobAppUpdate Pydantic schema.
        # = Body(...) means this field is required, and will come from the body of the PUT request.
        updated_data: job_schemas.JobAppUpdate = Body(...),
):
    return await job_crud.update_job(db, id, updated_data)


@router.delete("/{id}", response_model=None, status_code=204)
async def delete_jobs_by_id(id: int, db: AsyncSession = Depends(get_async_db)):
    await job_crud.delete_job(db, id)
    return
