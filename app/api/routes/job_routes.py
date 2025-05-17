from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import job_crud
from app.api.deps import get_db
from app.schemas import job_schemas

router = APIRouter()


@router.post("/", response_model=job_schemas.JobApp)
def create_application(job: job_schemas.JobAppCreate, db: Session = Depends(get_db)):
    return job_crud.create_job_app(db=db, job=job)


@router.get("/", response_model=list[job_schemas.JobApp])
def read_applications(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return job_crud.get_job_apps(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=job_schemas.JobApp)
def read_jobs_by_id(id: int, db: Session = Depends(get_db)):
    job_app = job_crud.get_job_app_by_id(db, id)
    return job_app


@router.put("/{id}", response_model=job_schemas.JobApp)
def update_jobs_by_id(
        id: int,
        db: Session = Depends(get_db),
        updated_data=job_schemas.JobAppUpdate):
    return job_crud.update_job(db, id, updated_data)


@router.delete("/{id}", response_model=job_schemas.JobApp)
def delete_jobs_by_id(id: int, db: Session = Depends(get_db)):
    job_crud.delete_job(db, id)
    return {"detail": f"Successfully deleted job ID {id} 💀"}
