# Route Testing with FastAPIs TestClient
from app.models.job_models import JobApplication
import datetime


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Application Tracker is up and running 🚀"}


# This test checks if the /applications/ endpoint returns a successful response
def test_read_applications_route(client):
    response = client.get("/applications/")
    assert response.status_code == 200


# This test checks if fetching a specific job application by ID returns correct data
def test_read_applications_route_with_id(client, sample_applications):
    response = client.get("/applications/1/")
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "TestCompany"


# This test verifies that requesting a non-existent job application ID returns a 404 error
def test_access_non_existent_job_id(client):
    response = client.get("/applications/9999/")
    assert response.status_code == 404


# This test verifies the logic of updating job details by the ID
def test_update_job_application_by_id(client, db):
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
    db.add(job_app)
    db.commit()
    db.refresh(job_app)

    # Prepare the update payload
    update_data = {
        "status": "interviewing",
        "applied_date": "2025-05-02",  # Here send string in API, let Pydantic parse it
        "link": "http://updated.com",
        "notes": "waiting for reply"
    }

    # Send PUT or PATCH request to update the job app
    response = client.put(f"/applications/{job_app.id}/", json=update_data)
    assert response.status_code == 200

    # Verify the update was successful by fetching the updated object
    get_response = client.get(f"/applications/{job_app.id}/")
    data = get_response.json()
    assert data["status"] == "interviewing"
    assert data["notes"] == "waiting for reply"


# This test verifies the logic of updating job application by the ID
def test_delete_job_application_by_id(client, db):
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
    db.add(job_app)
    db.commit()
    db.refresh(job_app)

    # Send PUT or PATCH request to update the job app
    response = client.delete(f"/applications/{job_app.id}")

    assert response.status_code == 200

    # Check DB: job should not exist anymore
    deleted_job = db.query(JobApplication).filter(JobApplication.id == job_app.id).first()
    assert deleted_job is None
