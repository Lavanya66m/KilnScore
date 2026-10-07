from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RecipientInput(BaseModel):
    """
    Fields are optional at the request level on purpose.

    If one recipient is invalid, we still accept the job and mark that
    recipient as failed. Strict required fields here would reject the
    entire request.
    """

    name: str | None = None
    email: str | None = None
    course: str | None = None
    date: str | None = None


class JobCreate(BaseModel):
    recipients: list[RecipientInput] = Field(..., min_length=1)

    @field_validator("recipients")
    @classmethod
    def recipients_must_not_be_empty(cls, value: list[RecipientInput]) -> list[RecipientInput]:
        if not value:
            raise ValueError("recipients must not be empty")
        return value


class JobCreatedResponse(BaseModel):
    job_id: int
    status: str
    message: str


class CertificateStatusItem(BaseModel):
    certificate_id: str | None
    name: str | None
    status: str
    error: str | None = None


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    total: int
    successful: int
    failed: int
    created_at: datetime
    completed_at: datetime | None
    certificates: list[CertificateStatusItem]
