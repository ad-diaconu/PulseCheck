# database.py
"""
Database Configuration and Session Management.

Sets up SQLAlchemy databse engine, session maker, and the declarative base model. Provides database seessions per request dependency.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# engine = connection pool - one per app process, not per request
# pool_pre_ping = checks if connections its still up before using it; if not it recreates it without breaking the app
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# each request gets its own session, then its closed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLAlchemy models inherit from base
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
