# unit tests for database logic
# CRUD Logic (No FastAPI involved)
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.crud import job_crud
from app.schemas import job_schemas


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


def test_get_job_app_by_id_raises_404(db):
    # Try to get a job application with an ID that doesn't exist
    with pytest.raises(HTTPException) as exc_info:
        job_crud.get_job_app_by_id(db, id=999999)
    assert exc_info.value.status_code == 404
    assert "job wasn't found 💀" in exc_info.value.detail.lower()


def test_delete_nonexistent_job(db):
    with pytest.raises(HTTPException) as ex_info:
        job_crud.delete_job(db, job_id=99999)
    assert ex_info.value.status_code == 404
    assert "Job wasn't found 💀" in str(ex_info.value.detail)


#integration test
def test_delete_nonexistent_job_endpoint(client):
    response = client.delete("/applications/999")
    assert response.status_code == 404
    assert response.json() == {'detail': "Job wasn't found 💀"}


def test_update_nonexistent_job(db):
    # Create a fake update payload
    update_info = job_schemas.JobAppUpdate(
        company="Ghost Corp",
        position="No code Engineer"
    )

    # Act & Assert: expect HTTPException with 404
    with pytest.raises(HTTPException) as exc_info:
        job_crud.update_job(db, job_id=9999, updated_data=update_info)

    assert exc_info.value.status_code == 404
    assert "Job wasn't found 💀" in str(exc_info.value.detail)


def test_feed_schema_invalid_status(db):
    with pytest.raises(ValidationError) as ex_info:
        job_schemas.JobAppCreate(
            company="Google",
            position="Backend Engineer",
            status="ghosted",  # 🚫 invalid status
            applied_date="2025-05-10"
        )

    errors = ex_info.value.errors()
    assert errors[0]["loc"] == ("status",)
    assert "Input should be" in errors[0]["msg"]
