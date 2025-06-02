# Route Testing with FastAPIs TestClient
import pytest

from app.models.job_models import JobApplication
import datetime
from sqlalchemy import select


@pytest.mark.anyio
async def test_read_root(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Application Tracker is up and running 🚀"}


# This test checks if the /applications/ endpoint returns a successful response
@pytest.mark.anyio
async def test_read_applications_route(async_client):
    response = await async_client.get("/applications/")
    assert response.status_code == 200


# This test checks if fetching a specific job application by ID returns correct data
@pytest.mark.anyio
async def test_read_applications_route_with_id(async_client, sample_applications):
    response = await async_client.get("/applications/1")
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "TestCompany"


# This test verifies that requesting a non-existent job application ID returns a 404 error
@pytest.mark.anyio
async def test_access_non_existent_job_id(async_client):
    response = await async_client.get("/applications/9999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_job_application(async_client):
    new_job = {
        "company": "OpenAI",
        "position": "Prompt Engineer",
        "status": "applied",
        "applied_date": "2024-05-18",
        "link": "https://openai.com/careers",
        "notes": "Excited about LLMs!"
    }

    response = await async_client.post("/applications/", json=new_job)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["company"] == new_job["company"]
    assert data["position"] == new_job["position"]
    assert data["status"] == new_job["status"]
    assert data["applied_date"] == new_job["applied_date"]
    assert isinstance(data["id"], int)


# This test verifies the logic of updating job details by the ID
@pytest.mark.anyio
async def test_update_job_application_by_id(async_client, db_session):
    # Create the original job app in the DB
    job_app = JobApplication(
        company="OriginalCo",
        position="Backend Engineer",
        location="NYC",
        status="applied",
        applied_date=datetime.date(2025, 5, 1),
        link="http://original.com",
        notes="initial notes"
    )
    db_session.add(job_app)
    await db_session.commit()
    await db_session.refresh(job_app)

    # Prepare the update payload
    update_data = {
        "status": "interviewing",
        "applied_date": "2025-05-02",  # Here send string in API, let Pydantic parse it
        "link": "http://updated.com",
        "notes": "waiting for reply"
    }

    # Send PUT or PATCH request to update the job app
    response = await async_client.put(f"/applications/{job_app.id}", json=update_data)
    assert response.status_code == 200

    # Verify the update was successful by fetching the updated object
    get_response = await async_client.get(f"/applications/{job_app.id}")
    data = get_response.json()
    assert data["status"] == "interviewing"
    assert data["notes"] == "waiting for reply"


# This test verifies the logic of updating job application by the ID
@pytest.mark.anyio
async def test_delete_job_application_by_id(async_client, db_session):
    # Create the original job app in the DB
    job_app = JobApplication(
        company="OriginalCo",
        position="Backend Engineer",
        location="NYC",
        status="applied",
        applied_date=datetime.date(2025, 5, 1),
        link="http://original.com",
        notes="initial notes"
    )
    db_session.add(job_app)
    await db_session.commit()
    await db_session.refresh(job_app)

    # Send PUT or PATCH request to update the job app
    response = await async_client.delete(f"/applications/{job_app.id}")

    assert response.status_code == 204

    # Check DB: job should not exist anymore
    result = await db_session.execute(
        select(JobApplication).where(JobApplication.id == job_app.id)
    )
    deleted_job = result.scalar_one_or_none()
    assert deleted_job is None
