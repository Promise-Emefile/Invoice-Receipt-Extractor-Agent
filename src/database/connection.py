from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./invoices.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Create database tables (call at startup)."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Yield a DB session (use in contexts)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()