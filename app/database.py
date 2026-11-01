
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://kilnuser:kilnpassword@localhost:5432/kilnscore",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def check_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()
