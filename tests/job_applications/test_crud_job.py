# unit tests for database logic
# CRUD Logic (No FastAPI involved)
import pytest
from app.crud import job_crud
from app.schemas import job_schemas
from app.exceptions import JobApplicationNotFoundException, ValidationError, AppBaseException


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
    job_id = 9999
    # Try to get a job application with an ID that doesn't exist
    with pytest.raises(JobApplicationNotFoundException) as exc_info:
        job_crud.get_job_app_by_id(db, job_id)
    assert exc_info.value.status_code == 404
    assert f'Job Application with id {job_id} was not found 💀' in exc_info.value.detail


def test_delete_nonexistent_job(db):
    job_id = 9999
    with pytest.raises(AppBaseException) as ex_info:
        job_crud.delete_job(db, job_id)
    assert ex_info.value.status_code == 500
    assert f'Unexpected error during deletion.' in str(ex_info.value.detail)


# integration test
def test_delete_nonexistent_job_endpoint(client):
    response = client.delete("/applications/999")
    assert response.status_code == 500
    assert response.json() == {'detail': 'Unexpected error during deletion.'}


def test_update_nonexistent_job(db):
    # Create a fake update payload
    update_info = job_schemas.JobAppUpdate(
        company="Ghost Corp",
        position="No code Engineer"
    )
    job_id = 9999
    # Act & Assert: expect JobApplicationNotFoundException with 404
    with pytest.raises(JobApplicationNotFoundException) as exc_info:
        job_crud.update_job(db, job_id, updated_data=update_info)

    assert exc_info.value.status_code == 404
    assert f'Job Application with id {job_id} was not found 💀' in str(exc_info.value.detail)


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
