# Bulk Certificate Generator

Backend API that accepts a list of recipients, creates a generation job, and produces PDF certificates in the background.

This project is intentionally small and easy to explain in an interview. It uses FastAPI, SQLite, SQLAlchemy, Pydantic, ReportLab, and Pytest. There are no queues, Docker, or extra services.

## Features

- Create one job for many recipients with `POST /jobs`
- Validate each recipient without failing the whole job
- Generate professional PDF certificates with ReportLab
- Track job progress with `GET /jobs/{job_id}`
- Download a PDF with `GET /certificates/{certificate_id}`
- Automatic Swagger docs at `/docs`
- Tests with a separate in-memory SQLite database

## Technologies used

- Python 3
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- ReportLab
- Pytest
- Uvicorn

## Project structure

```text
bulkcertificategenerator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app and startup
│   ├── config.py               # Paths and certificate ID settings
│   ├── database.py             # Engine, session, get_db dependency
│   ├── models.py               # SQLAlchemy Job and Certificate tables
│   ├── schemas.py              # Pydantic request/response models
│   ├── crud.py                 # Database create/read/update helpers
│   ├── validation.py           # Per-recipient validation rules
│   ├── services/
│   │   ├── __init__.py
│   │   └── certificate_service.py  # PDF generation and background job
│   └── routes/
│       ├── __init__.py
│       ├── jobs.py
│       └── certificates.py
├── generated_certificates/     # Saved PDF files
├── tests/
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   └── test_certificates.py
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

## Installation

### 1. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## How to run the application

From the project root:

```bash
uvicorn app.main:app --reload
```

Then open:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

SQLite creates `certificates.db` automatically on startup. PDF files are written to `generated_certificates/`.

## How to run tests

```bash
pytest
```

Tests use an in-memory SQLite database, not `certificates.db`.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Simple health message |
| POST | `/jobs` | Create a bulk generation job |
| GET | `/jobs/{job_id}` | Job status and per-certificate results |
| GET | `/certificates/{certificate_id}` | Download a generated PDF |
| GET | `/docs` | Swagger UI |

### Example: create a job

`POST /jobs`

```json
{
  "recipients": [
    {
      "name": "John Doe",
      "email": "john@example.com",
      "course": "Python Backend Development",
      "date": "2026-10-07"
    },
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "course": "Python Backend Development",
      "date": "2026-10-07"
    }
  ]
}
```

Response (`202 Accepted`):

```json
{
  "job_id": 1,
  "status": "processing",
  "message": "Certificate generation started"
}
```

### Example: get job status

`GET /jobs/1`

```json
{
  "job_id": 1,
  "status": "completed_with_errors",
  "total": 10,
  "successful": 8,
  "failed": 2,
  "certificates": [
    {
      "certificate_id": "CERT-000001",
      "name": "John Doe",
      "status": "completed"
    },
    {
      "certificate_id": null,
      "name": "Invalid User",
      "status": "failed",
      "error": "Invalid email"
    }
  ]
}
```

### How to retrieve certificates

After a certificate status is `completed`, download it:

```text
GET /certificates/CERT-000001
```

The API returns the PDF file. Invalid IDs return `404`.

## Important design decisions

**Per-recipient validation, not request-level required fields.**  
If `name` and `email` were required in Pydantic, one bad recipient would reject the whole `POST /jobs` request. The assignment needs valid recipients to continue, so the request only requires a non-empty `recipients` list. Each item is checked in `app/validation.py`. Invalid rows are stored as `failed`.

**Empty list is a request error.**  
`[]` cannot create a useful job, so FastAPI/Pydantic returns `422 Unprocessable Entity`.

**BackgroundTasks instead of Celery/Redis.**  
`POST /jobs` saves the job, schedules `process_job`, and returns quickly. FastAPI runs that function after sending the response. That is enough for a local assignment and is easy to explain.

**A new database session in the background task.**  
The request session is closed when the response is finished. `process_job` opens its own `SessionLocal()` session.

**One failure does not stop the batch.**  
PDF generation is wrapped in `try/except` per certificate. The error is stored in `error_message`, then the loop continues.

**Job status is derived from certificate rows.**  
After processing:

- all succeeded → `completed`
- mix of success and failure → `completed_with_errors`
- all failed → `failed`

**Certificate IDs.**  
Successful records get IDs like `CERT-000001` from the database primary key.

## Explanation of background processing

1. Client sends `POST /jobs` with many recipients.
2. The API validates that `recipients` is not empty.
3. A `jobs` row is created with status `processing`.
4. Each recipient becomes a `certificates` row (`pending` or `failed` if invalid).
5. The API returns `job_id` immediately (`202 Accepted`).
6. FastAPI `BackgroundTasks` calls `process_job(job_id)`.
7. For every `pending` certificate, ReportLab writes a PDF to `generated_certificates/`.
8. Each row is marked `completed` or `failed`.
9. Job counts and final status are updated.
10. The client polls `GET /jobs/{job_id}` and downloads PDFs with `GET /certificates/{certificate_id}`.
