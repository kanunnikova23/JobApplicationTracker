# Route Testing with FastAPIs TestClient

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Job Application Tracker is up and running 🚀"}


def test_create_and_get_job(client):
    job_data = {
        "company": "Netflix",
        "position": "Data Engineer",
        "status": "applied",
        "applied_date": "2024-01-01"
    }
    res = client.post("/jobs/", json=job_data)
    assert res.status_code == 200
    assert res.json()["company"] == "Netflix"

    res = client.get("/jobs/")
    assert res.status_code == 200
    assert len(res.json()) == 1
