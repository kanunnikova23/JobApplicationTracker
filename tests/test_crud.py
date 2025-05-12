# unit tests for database logic
# CRUD Logic (No FastAPI involved)
from app import schemas
from app.crud import job_crud


def test_create_job_app(db):
    job = schemas.JobAppCreate(
        company="OpenAI",
        position="Backend Engineer",
        status="applied",
        applied_date="2024-01-01"
    )
    result = crud.create_job_app(db, job)
    assert result.company == "OpenAI"
    assert result.status == "applied"


def test_get_job_apps_empty(db):
    apps = crud.get_job_apps(db)
    assert apps == []


def test_delete_nonexistent_job(db):
    result = crud.delete_job(db, job_id=999)
    assert result is None
