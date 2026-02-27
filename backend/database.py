"""
database.py — SQLAlchemy engine, session factory, and declarative Base.
All models must inherit from Base.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/supermarket_crm")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Detect stale connections
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def check_db_connection():
    """Verify database connection and print status."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("database is connected to backend")
    except Exception:
        print("backend is not connected to database")


# Perform connection check on module load
check_db_connection()


def get_db():
    """FastAPI dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
