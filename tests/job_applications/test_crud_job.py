# unit tests for database logic
# CRUD Logic (No FastAPI involved)
import pytest
from sqlalchemy import delete

from app.crud import job_crud
from app.models import job_models
from app.schemas import job_schemas
from app.exceptions import JobApplicationNotFoundException, ValidationError, AppBaseException


@pytest.mark.anyio
async def test_create_job_app(db_session):
    job = job_schemas.JobAppCreate(
        company="OpenAI",
        position="Backend Engineer",
        status="applied",
        applied_date="2024-01-01"
    )
    result = await job_crud.create_job_app(db_session, job)
    assert result.company == "OpenAI"
    assert result.status == "applied"


@pytest.mark.anyio
async def test_get_job_apps_empty(db_session):
    apps = await job_crud.get_job_apps(db_session)
    assert apps == []


@pytest.mark.anyio
async def test_get_job_app_by_id_raises_404(db_session):
    job_id = 9999
    # Try to get a job application with an ID that doesn't exist
    with pytest.raises(JobApplicationNotFoundException) as exc_info:
        await job_crud.get_job_app_by_id(db_session, job_id)
    assert exc_info.value.status_code == 404
    assert f'Job Application with id {job_id} was not found 💀' in exc_info.value.detail


@pytest.mark.anyio
async def test_delete_nonexistent_job(db_session):
    job_id = 9999
    with pytest.raises(AppBaseException) as ex_info:
        await job_crud.delete_job(db_session, job_id)
    assert ex_info.value.status_code == 500
    assert f'Unexpected error during deletion.' in str(ex_info.value.detail)


# integration test
@pytest.mark.anyio
async def test_delete_nonexistent_job_endpoint(async_client):
    response = await async_client.delete("/applications/999")
    assert response.status_code == 500
    assert response.json() == {'detail': 'Unexpected error during deletion.'}


@pytest.mark.anyio
async def test_update_nonexistent_job(db_session):
    # Create a fake update payload
    update_info = job_schemas.JobAppUpdate(
        company="Ghost Corp",
        position="No code Engineer"
    )
    job_id = 9999
    # Act & Assert: expect JobApplicationNotFoundException with 404
    with pytest.raises(JobApplicationNotFoundException) as exc_info:
        await job_crud.update_job(db_session, job_id, updated_data=update_info)

    assert exc_info.value.status_code == 404
    assert f'Job Application with id {job_id} was not found 💀' in str(exc_info.value.detail)


@pytest.mark.anyio
async def test_feed_schema_invalid_status(db_session):
    with pytest.raises(ValidationError) as ex_info:
        job_schemas.JobAppCreate(
            company="Google",
            position="Backend Engineer",
            status="ghosted",  # invalid status
            applied_date="2025-05-10"
        )

    errors = ex_info.value.errors()
    assert errors[0]["loc"] == ("status",)
    assert "Input should be" in errors[0]["msg"]
