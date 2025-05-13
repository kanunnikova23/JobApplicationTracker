from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import job_crud
from app.db.database import SessionLocal
from app.schemas import job_schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/jobs/", response_model=job_schemas.JobApp)
def create_job(job: job_schemas.JobAppCreate, db: Session = Depends(get_db)):
    return job_crud.create_job_app(db=db, job=job)


@router.get("/jobs/", response_model=list[job_schemas.JobApp])
def read_jobs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return job_crud.get_job_apps(db, skip=skip, limit=limit)
