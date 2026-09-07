from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# read database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dbadmin:password@localhost:5432/ailoganalyser"
)

# create database engine
engine = create_engine(DATABASE_URL)

# create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for all database models
Base = declarative_base()

# dependency function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()