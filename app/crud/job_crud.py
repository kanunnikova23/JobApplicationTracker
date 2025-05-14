# Contains DB logic.

from sqlalchemy.orm import Session
import app.models.job_models as models
import app.schemas.job_schemas as schemas
from fastapi import HTTPException
import logging

# logging important CRUD events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Handle creating a new row in the job_applications table.
def create_job_app(db: Session, job: schemas.JobAppCreate):
    job_data_dict = job.dict()
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
        raise HTTPException(status_code=404, detail="Job wasn't found 💀")
    db.delete(job)
    db.commit()
    logger.info(f"🗑️ Deleted job ID {job_id}")
    return job


# Do partial updates
def update_job(db: Session, job_id: int, updated_data: schemas.JobAppUpdate):
    job = db.query(models.JobApplication).filter(models.JobApplication.id == job_id).first()
    if not job:
        logger.warning(f"⚠️ Tried to update missing job ID {job_id}")
        raise HTTPException(status_code=404, detail="Job wasn't found 💀")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    logger.info(f"✏️ Updated job ID {job_id} with fields: {list(updated_data.dict(exclude_unset=True).keys())}")
    return job
