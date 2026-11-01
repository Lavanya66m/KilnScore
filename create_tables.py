from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

print("Usage records table created successfully!")