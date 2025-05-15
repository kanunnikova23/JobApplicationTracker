# Route Testing with FastAPIs TestClient

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Application Tracker is up and running 🚀"}