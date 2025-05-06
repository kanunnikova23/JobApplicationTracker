from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/jobs/", response_model=schemas.JobApp)
def create_job(job: schemas.JobAppCreate, db: Session = Depends(get_db)):
    return crud.create_job_app(db=db, job=job)


@router.get("/jobs/", response_model=list[schemas.JobApp])
def read_jobs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_job_apps(db, skip=skip, limit=limit)
