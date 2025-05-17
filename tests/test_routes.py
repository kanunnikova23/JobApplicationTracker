# Route Testing with FastAPIs TestClient

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Application Tracker is up and running 🚀"}

# This test checks if the /applications/ endpoint returns a successful response
def test_read_applications_route(client):
    response = client.get("/applications/")
    assert response.status_code == 200
