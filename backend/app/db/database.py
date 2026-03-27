import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./et_money_mentor.db")

# PostgreSQL (Supabase) needs different connect_args than SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    # Try connecting to the configured DATABASE_URL
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    # Test the connection immediately
    with engine.connect() as conn:
        pass 
except Exception:
    # Silent fallback
    DATABASE_URL = "sqlite:///./et_money_mentor.db"
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
