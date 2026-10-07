from fastapi.testclient import TestClient

from app.schemas import RecipientInput
from app.validation import validate_recipient


def test_empty_recipient_list_is_rejected(client: TestClient) -> None:
    response = client.post("/jobs", json={"recipients": []})
    assert response.status_code == 422


def test_missing_name_fails_only_that_recipient(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "recipients": [
                {
                    "name": "",
                    "email": "bad@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
                {
                    "name": "Valid User",
                    "email": "valid@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
            ]
        },
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    status_body = client.get(f"/jobs/{job_id}").json()
    assert status_body["status"] == "completed_with_errors"
    assert status_body["successful"] == 1
    assert status_body["failed"] == 1

    failed = next(item for item in status_body["certificates"] if item["status"] == "failed")
    completed = next(item for item in status_body["certificates"] if item["status"] == "completed")
    assert failed["error"] == "Name is required"
    assert completed["name"] == "Valid User"


def test_invalid_email_does_not_stop_valid_recipients(client: TestClient) -> None:
    response = client.post(
        "/jobs",
        json={
            "recipients": [
                {
                    "name": "Invalid User",
                    "email": "not-an-email",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "course": "Python Backend Development",
                    "date": "2026-10-07",
                },
            ]
        },
    )
    job_id = response.json()["job_id"]
    body = client.get(f"/jobs/{job_id}").json()

    assert body["successful"] == 1
    assert body["failed"] == 1
    assert body["status"] == "completed_with_errors"

    failed = next(item for item in body["certificates"] if item["status"] == "failed")
    completed = next(item for item in body["certificates"] if item["status"] == "completed")
    assert failed["error"] == "Invalid email"
    assert completed["name"] == "John Doe"
    assert completed["certificate_id"] is not None


def test_validate_recipient_helper_messages() -> None:
    assert validate_recipient(RecipientInput(name="", email="a@b.com", course="C", date="2026-10-07")) == "Name is required"
    assert validate_recipient(RecipientInput(name="A", email="", course="C", date="2026-10-07")) == "Email is required"
    assert validate_recipient(RecipientInput(name="A", email="bad", course="C", date="2026-10-07")) == "Invalid email"
    assert validate_recipient(RecipientInput(name="A", email="a@b.com", course="", date="2026-10-07")) == "Course is required"
    assert validate_recipient(RecipientInput(name="A", email="a@b.com", course="C", date="")) == "Date is required"
    assert (
        validate_recipient(RecipientInput(name="A", email="a@b.com", course="C", date="07-10-2026"))
        == "Date must be in YYYY-MM-DD format"
    )
    assert validate_recipient(RecipientInput(name="A", email="a@b.com", course="C", date="2026-10-07")) is None
