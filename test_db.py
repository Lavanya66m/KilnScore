from app.database import check_database

result = check_database()

print("Database connection successful!")
print("Result:", result)