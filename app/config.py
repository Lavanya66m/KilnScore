from pathlib import Path

# Project root: bulk-certificate-generator/
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR / 'certificates.db'}"

CERTIFICATE_OUTPUT_DIR = BASE_DIR / "generated_certificates"

# Certificate IDs look like CERT-000001
CERTIFICATE_ID_PREFIX = "CERT"
CERTIFICATE_ID_WIDTH = 6
