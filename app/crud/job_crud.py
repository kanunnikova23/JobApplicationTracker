# Contains DB logic.

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import app.models.job_models as models
import app.schemas.job_schemas as schemas
from app.core.logger import logger
from app.exceptions import JobApplicationNotFoundException, AppBaseException


# Handle creating a new row in the job_applications table.
async def create_job_app(db: AsyncSession, job: schemas.JobAppCreate):
    try:
        job_data_dict = job.model_dump()

        if "link" in job_data_dict and job_data_dict["link"] is not None:
            job_data_dict["link"] = str(job_data_dict["link"])

        db_job = models.JobApplication(**job_data_dict)
        db.add(db_job)
        await db.commit()
        await db.refresh(db_job)
        logger.info(f"✅ Created job application: {db_job.id} at {db_job.company}")
        return db_job
    except IntegrityError:
        await db.rollback()
        raise AppBaseException(status_code=409, detail="Database integrity error: Duplicate or invalid data.")
    except Exception:
        await db.rollback()
        raise AppBaseException(status_code=500, detail="Unexpected error during creation.")


# List jobs with pagination
async def get_job_apps(db: AsyncSession, skip: int = 0, limit: int = 100):
    try:
        result = await db.execute(
            select(models.JobApplication).offset(skip).limit(limit)
        )
        logger.info(f"📄 Fetched jobs: skip={skip}, limit={limit}")
        return result.scalars().all()
    except Exception:
        raise AppBaseException(status_code=500, detail="Internal server error while fetching job applications.")


# Delete a job by ID
async def delete_job(db: AsyncSession, job_id: int):
    try:
        job = await fetch_one(db, select(models.JobApplication).where(models.JobApplication.id == job_id))
        if not job:
            raise JobApplicationNotFoundException(job_id)
        await db.delete(job)
        await db.commit()
        logger.info(f"🗑️ Deleted job ID {job_id}")
        return job
    except Exception:
        await db.rollback()
        raise AppBaseException(status_code=500, detail="Unexpected error during deletion.")


# Accepts a DB session, job ID, and partial update data using a Pydantic schema
async def update_job(db: AsyncSession, job_id: int, updated_data: schemas.JobAppUpdate):
    try:
        #  Fetch the job entry from the database
        job = await get_job_app_by_id(db, job_id)

        update_fields = updated_data.model_dump(exclude_unset=True)

        #  Update only the fields that were actually passed in the request
        for key, value in update_fields.items():
            setattr(job, key, value)
        #  Save and refresh the changes in the DB
        await db.commit()
        await db.refresh(job)
        #  Log what got updated
        logger.info(
            f"✏️ Updated job ID {job_id} with fields: {list(update_fields.keys())}")
        #  Return the fully updated model
        return job

    except JobApplicationNotFoundException as e:
        raise e

    except IntegrityError:
        await db.rollback()
        raise AppBaseException(status_code=409, detail="Database integrity error during update.")

    except Exception:
        await db.rollback()
        raise AppBaseException(status_code=500, detail="Unexpected error during update.")


async def get_job_app_by_id(db: AsyncSession, job_id: int):
    job = await fetch_one(db, select(models.JobApplication).where(models.JobApplication.id == job_id))
    logger.info(f"🔎 Fetched job ID: {job_id}")
    if not job:
        raise JobApplicationNotFoundException(job_id)
    return job


async def fetch_one(db: AsyncSession, stmt) -> models.JobApplication | None:
    """
        Executes the provided SQLAlchemy select() statement and returns a single ORM object or None.
    """
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
