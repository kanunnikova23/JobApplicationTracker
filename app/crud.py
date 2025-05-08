# Contains DB logic.

from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from fastapi import HTTPException


# Handle creating a new row in the job_applications table.
def create_job_app(db: Session, job: schemas.JobAppCreate):
    db_job = models.JobApplication(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


# List jobs with pagination
def get_job_apps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JobApplication).offset(skip).limit(limit).all()


# Delete a job by ID
def delete_job(db: Session, job_id: int):
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job wasn't found 💀")
    db.delete(job)
    db.commit()

    return job


# Do partial updates
def update_job(db: Session, job_id: int, updated_data: schemas.JobAppUpdate):
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job wasn't found 💀")
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job
