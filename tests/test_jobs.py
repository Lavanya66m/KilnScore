from fastapi.testclient import TestClient


def test_create_generation_job(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "recipients": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
            ]
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["job_id"] == 1
    assert body["status"] == "processing"
    assert body["message"] == "Certificate generation started"


def test_job_status_and_progress(client: TestClient) -> None:
    create_response = client.post(
        "/jobs",
        json={
            "recipients": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                }
            ]
        },
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200

    body = status_response.json()
    assert body["job_id"] == job_id
    assert body["total"] == 1
    assert body["successful"] == 1
    assert body["failed"] == 0
    assert body["status"] == "completed"
    assert body["certificates"][0]["status"] == "completed"
    assert body["certificates"][0]["certificate_id"] == "CERT-000001"


def test_invalid_job_id_returns_404(client: TestClient) -> None:
    response = client.get("/jobs/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
