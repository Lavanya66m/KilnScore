from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.services.certificate_service import get_certificate_file

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/{certificate_id}")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)) -> FileResponse:
    certificate = crud.get_certificate_by_public_id(db, certificate_id)
    if certificate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate {certificate_id} was not found",
        )

    file_path = get_certificate_file(certificate)
    if file_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF for certificate {certificate_id} is not available",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf",
    )
