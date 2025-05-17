# Route Testing with FastAPIs TestClient

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
