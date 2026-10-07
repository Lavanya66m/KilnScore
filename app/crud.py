from sqlalchemy.orm import Session, joinedload

from app.models import Certificate, Job, utc_now
from app.schemas import RecipientInput
from app.validation import validate_recipient


def create_job_with_certificates(db: Session, recipients: list[RecipientInput]) -> Job:
    """Create a job and one certificate row for each recipient."""
    job = Job(
        status="processing",
        total=len(recipients),
        successful=0,
        failed=0,
    )
    db.add(job)
    db.flush()  # Get job.id before inserting certificates.

    for recipient in recipients:
        error = validate_recipient(recipient)
        certificate = Certificate(
            job_id=job.id,
            name=(recipient.name or "").strip() or None,
            email=(recipient.email or "").strip() or None,
            course=(recipient.course or "").strip() or None,
            date=(recipient.date or "").strip() or None,
        )
        if error:
            certificate.status = "failed"
            certificate.error_message = error
        else:
            certificate.status = "pending"

        db.add(certificate)

    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: int) -> Job | None:
    return (
        db.query(Job)
        .options(joinedload(Job.certificates))
        .filter(Job.id == job_id)
        .first()
    )


def get_all_jobs(db: Session, limit: int = 50) -> list[Job]:
    return (
        db.query(Job)
        .options(joinedload(Job.certificates))
        .order_by(Job.id.desc())
        .limit(limit)
        .all()
    )


def get_pending_certificates(db: Session, job_id: int) -> list[Certificate]:
    return (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id, Certificate.status == "pending")
        .all()
    )


def get_certificate_by_public_id(db: Session, certificate_id: str) -> Certificate | None:
    return (
        db.query(Certificate)
        .filter(Certificate.certificate_id == certificate_id)
        .first()
    )


def update_certificate_processing(db: Session, certificate: Certificate) -> None:
    certificate.status = "processing"
    db.commit()


def mark_certificate_completed(
    db: Session,
    certificate: Certificate,
    certificate_id: str,
    file_path: str,
) -> None:
    certificate.status = "completed"
    certificate.certificate_id = certificate_id
    certificate.file_path = file_path
    certificate.error_message = None
    db.commit()


def mark_certificate_failed(db: Session, certificate: Certificate, error_message: str) -> None:
    certificate.status = "failed"
    certificate.error_message = error_message
    db.commit()


def refresh_job_progress(db: Session, job: Job) -> Job:
    """Recalculate counts from certificate rows and set the final job status if done."""
    certificates = job.certificates
    successful = sum(1 for item in certificates if item.status == "completed")
    failed = sum(1 for item in certificates if item.status == "failed")
    still_running = any(item.status in ("pending", "processing") for item in certificates)

    job.successful = successful
    job.failed = failed
    job.total = len(certificates)

    if not still_running:
        job.completed_at = utc_now()
        if failed == 0:
            job.status = "completed"
        elif successful == 0:
            job.status = "failed"
        else:
            job.status = "completed_with_errors"

    db.commit()
    db.refresh(job)
    return job
