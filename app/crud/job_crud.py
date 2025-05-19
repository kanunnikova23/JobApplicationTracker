# Contains DB logic.

from sqlalchemy.orm import Session

import app.models.job_models as models
import app.schemas.job_schemas as schemas
from app.core.logger import logger
from app.exceptions import JobApplicationNotFoundException


# Handle creating a new row in the job_applications table.
def create_job_app(db: Session, job: schemas.JobAppCreate):
    job_data_dict = job.model_dump()
    if job_data_dict["link"] is not None:
        job_data_dict["link"] = str(job_data_dict["link"])

    db_job = models.JobApplication(**job_data_dict)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    logger.info(f"✅ Created job application: {db_job.id} at {db_job.company}")
    return db_job


# List jobs with pagination
def get_job_apps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JobApplication).offset(skip).limit(limit).all()


# Delete a job by ID
def delete_job(db: Session, job_id: int):
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()
    if not job:
        logger.warning(f"❌ Tried to delete non-existent job ID {job_id}")
        raise JobApplicationNotFoundException(job_id)
    db.delete(job)
    db.commit()
    logger.info(f"🗑️ Deleted job ID {job_id}")
    return job


# Accepts a DB session, job ID, and partial update data using a Pydantic schema
def update_job(db: Session, job_id: int, updated_data: schemas.JobAppUpdate):
    #  Fetch the job entry from the database
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()

    #  If it doesn't exist, raise 404
    if not job:
        logger.warning(f"⚠️ Tried to update missing job ID {job_id}")
        raise JobApplicationNotFoundException(job_id)

    #  Update only the fields that were actually passed in the request
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(job, key, value)

    #  Save and refresh the changes in the DB
    db.commit()
    db.refresh(job)

    #  Log what got updated
    logger.info(f"✏️ Updated job ID {job_id} with fields: {list(updated_data.model_dump(exclude_unset=True).keys())}")

    #  Return the fully updated model
    return job


def get_job_app_by_id(db: Session, job_id: int):
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()
    if not job:
        raise JobApplicationNotFoundException(job_id)
    return job
