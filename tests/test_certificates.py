from pathlib import Path

from fastapi.testclient import TestClient

from app.models import Certificate
from app.services.certificate_service import generate_certificate_pdf


def test_certificate_pdf_generation(tmp_path: Path, monkeypatch) -> None:
    from app.services import certificate_service

    monkeypatch.setattr(certificate_service, "CERTIFICATE_OUTPUT_DIR", tmp_path)

    certificate = Certificate(
        id=1,
        job_id=1,
        name="John Doe",
        email="john@example.com",
        course="Python Backend Development",
        date="2026-10-07",
        status="processing",
    )

    file_path = generate_certificate_pdf(certificate, "CERT-000001")
    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0
    assert path.read_bytes().startswith(b"%PDF")


def test_download_generated_certificate(client: TestClient) -> None:
    client.post(
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

    download = client.get("/certificates/CERT-000001")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF")


def test_invalid_certificate_id_returns_404(client: TestClient) -> None:
    response = client.get("/certificates/CERT-999999")
    assert response.status_code == 404


def test_bulk_job_creates_multiple_pdfs(client: TestClient) -> None:
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
    job_id = response.json()["job_id"]
    body = client.get(f"/jobs/{job_id}").json()

    assert body["total"] == 2
    assert body["successful"] == 2
    ids = {item["certificate_id"] for item in body["certificates"]}
    assert ids == {"CERT-000001", "CERT-000002"}

    for certificate_id in ids:
        download = client.get(f"/certificates/{certificate_id}")
        assert download.status_code == 200
        assert download.content.startswith(b"%PDF")
