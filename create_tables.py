from sqlalchemy import text

from app.database import engine
from app.models import Base

# Enable pgvector extension before creating tables
with engine.begin() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

# Create database tables
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")