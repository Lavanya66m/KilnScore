import re
from datetime import datetime

from app.schemas import RecipientInput

# Simple email pattern. This keeps the project easy to explain without
# extra email-validation libraries.
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_FORMAT = "%Y-%m-%d"


def validate_recipient(recipient: RecipientInput) -> str | None:
    """
    Return an error message if the recipient is invalid, otherwise None.

    Validation is done here (not only in Pydantic) so one bad recipient
    does not reject the whole job.
    """
    name = (recipient.name or "").strip()
    email = (recipient.email or "").strip()
    course = (recipient.course or "").strip()
    date = (recipient.date or "").strip()

    if not name:
        return "Name is required"
    if not email:
        return "Email is required"
    if not EMAIL_PATTERN.match(email):
        return "Invalid email"
    if not course:
        return "Course is required"
    if not date:
        return "Date is required"
    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        return "Date must be in YYYY-MM-DD format"

    return None
