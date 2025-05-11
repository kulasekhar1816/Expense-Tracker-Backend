import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read the DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Use create_engine for sync database engine
engine = create_engine(DATABASE_URL, echo=True)

# ✅ Synchronous sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ✅ Base class for models
Base = declarative_base()

# Dependency to get DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
