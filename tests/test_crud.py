# unit tests for database logic
# CRUD Logic (No FastAPI involved)
from app.schemas import job_schemas
from app.crud import job_crud


def test_create_job_app(db):
    job = job_schemas.JobAppCreate(
        company="OpenAI",
        position="Backend Engineer",
        status="applied",
        applied_date="2024-01-01"
    )
    result = job_crud.create_job_app(db, job)
    assert result.company == "OpenAI"
    assert result.status == "applied"


def test_get_job_apps_empty(db):
    apps = job_crud.get_job_apps(db)
    assert apps == []


def test_delete_nonexistent_job(db):
    result = job_crud.delete_job(db, job_id=999)
    assert result is None
