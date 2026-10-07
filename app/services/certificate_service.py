from datetime import datetime
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app import crud
from app.config import (
    CERTIFICATE_ID_PREFIX,
    CERTIFICATE_ID_WIDTH,
    CERTIFICATE_OUTPUT_DIR,
)
from app.database import SessionLocal
from app.models import Certificate, utc_now

NAVY = HexColor("#1B365D")
GOLD = HexColor("#C4A35A")
DARK_TEXT = HexColor("#2C2C2C")
MUTED_TEXT = HexColor("#5A5A5A")


def build_certificate_id(record_id: int) -> str:
    return f"{CERTIFICATE_ID_PREFIX}-{record_id:0{CERTIFICATE_ID_WIDTH}d}"


def format_display_date(date_value: str) -> str:
    """Convert YYYY-MM-DD to DD-MM-YYYY for the PDF."""
    parsed = datetime.strptime(date_value, "%Y-%m-%d")
    return parsed.strftime("%d-%m-%Y")


def generate_certificate_pdf(certificate: Certificate, certificate_id: str) -> str:
    """
    Draw one certificate PDF and return the saved file path.

    This uses a single predefined layout. There is no template editor.
    """
    CERTIFICATE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = CERTIFICATE_OUTPUT_DIR / f"{certificate_id}.pdf"

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(str(file_path), pagesize=landscape(A4))

    # Outer and inner borders
    pdf.setStrokeColor(NAVY)
    pdf.setLineWidth(4)
    pdf.rect(30, 30, page_width - 60, page_height - 60)

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1.5)
    pdf.rect(42, 42, page_width - 84, page_height - 84)

    # Title
    pdf.setFillColor(NAVY)
    pdf.setFont("Times-Bold", 32)
    pdf.drawCentredString(page_width / 2, page_height - 120, "CERTIFICATE OF COMPLETION")

    pdf.setStrokeColor(GOLD)
    pdf.setLineWidth(1)
    pdf.line(180, page_height - 135, page_width - 180, page_height - 135)

    pdf.setFillColor(MUTED_TEXT)
    pdf.setFont("Times-Italic", 16)
    pdf.drawCentredString(page_width / 2, page_height - 175, "This certificate is proudly presented to")

    pdf.setFillColor(NAVY)
    pdf.setFont("Times-Bold", 28)
    pdf.drawCentredString(page_width / 2, page_height - 220, certificate.name or "")

    pdf.setFillColor(MUTED_TEXT)
    pdf.setFont("Times-Italic", 16)
    pdf.drawCentredString(page_width / 2, page_height - 265, "for successfully completing")

    pdf.setFillColor(DARK_TEXT)
    pdf.setFont("Times-Bold", 20)
    pdf.drawCentredString(page_width / 2, page_height - 305, certificate.course or "")

    display_date = format_display_date(certificate.date or "")
    pdf.setFillColor(DARK_TEXT)
    pdf.setFont("Times-Roman", 14)
    pdf.drawCentredString(page_width / 2, 120, f"Date: {display_date}")
    pdf.drawCentredString(page_width / 2, 95, f"Certificate ID: {certificate_id}")

    pdf.save()
    return str(file_path)


def process_certificate(db: Session, certificate: Certificate) -> None:
    """Generate one PDF. Failures are stored on that row and do not raise."""
    try:
        crud.update_certificate_processing(db, certificate)
        certificate_id = build_certificate_id(certificate.id)
        file_path = generate_certificate_pdf(certificate, certificate_id)
        crud.mark_certificate_completed(db, certificate, certificate_id, file_path)
    except Exception as error:
        crud.mark_certificate_failed(db, certificate, f"PDF generation error: {error}")


def process_job(job_id: int) -> None:
    """
    Background worker for one job.

    A new database session is opened here because the request session
    is already closed after the API response is sent.
    """
    db = SessionLocal()
    try:
        job = crud.get_job(db, job_id)
        if job is None:
            return

        pending = crud.get_pending_certificates(db, job_id)
        for certificate in pending:
            process_certificate(db, certificate)

        # Expire cached rows so counts are read from the latest committed data.
        db.expire_all()
        job = crud.get_job(db, job_id)
        if job is not None:
            crud.refresh_job_progress(db, job)
    except Exception:
        job = crud.get_job(db, job_id)
        if job is not None:
            job.status = "failed"
            job.completed_at = utc_now()
            db.commit()
    finally:
        db.close()


def get_certificate_file(certificate: Certificate) -> Path | None:
    if certificate.status != "completed" or not certificate.file_path:
        return None

    path = Path(certificate.file_path)
    if not path.is_file():
        return None
    return path
