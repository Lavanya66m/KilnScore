from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.services.certificate_service import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=schemas.JobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_job(
    payload: schemas.JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> schemas.JobCreatedResponse:
    """
    Create a generation job and start PDF creation in the background.

    The HTTP response is returned immediately. FastAPI BackgroundTasks
    runs process_job after the response is sent.
    """
    try:
        job = crud.create_job_with_certificates(db, payload.recipients)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating job: {error}",
        ) from error

    background_tasks.add_task(process_job, job.id)

    return schemas.JobCreatedResponse(
        job_id=job.id,
        status=job.status,
        message="Certificate generation started",
    )


@router.get("", response_model=list[schemas.JobStatusResponse])
def list_jobs(limit: int = 50, db: Session = Depends(get_db)) -> list[schemas.JobStatusResponse]:
    """Retrieve recent certificate generation jobs."""
    jobs = crud.get_all_jobs(db, limit=limit)
    response = []
    for job in jobs:
        certificates = [
            schemas.CertificateStatusItem(
                certificate_id=item.certificate_id,
                name=item.name,
                status=item.status,
                error=item.error_message,
            )
            for item in job.certificates
        ]
        response.append(
            schemas.JobStatusResponse(
                job_id=job.id,
                status=job.status,
                total=job.total,
                successful=job.successful,
                failed=job.failed,
                created_at=job.created_at,
                completed_at=job.completed_at,
                certificates=certificates,
            )
        )
    return response


@router.get("/{job_id}", response_model=schemas.JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)) -> schemas.JobStatusResponse:
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} was not found",
        )

    certificates = [
        schemas.CertificateStatusItem(
            certificate_id=item.certificate_id,
            name=item.name,
            status=item.status,
            error=item.error_message,
        )
        for item in job.certificates
    ]

    return schemas.JobStatusResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        successful=job.successful,
        failed=job.failed,
        created_at=job.created_at,
        completed_at=job.completed_at,
        certificates=certificates,
    )
