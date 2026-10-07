from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import CERTIFICATE_OUTPUT_DIR
from app.database import Base, engine
from app.routes.certificates import router as certificates_router
from app.routes.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create SQLite tables and the PDF output folder when the app starts.
    Base.metadata.create_all(bind=engine)
    CERTIFICATE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Bulk Certificate Generator",
    description=(
        "Create a job with many recipients, generate PDF certificates "
        "in the background, and download each file by certificate ID."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(jobs_router)
app.include_router(certificates_router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": "Bulk Certificate Generator API. Open /docs for Swagger UI."}
