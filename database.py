"""
database.py
-----------
Single source of truth for the SQLAlchemy engine, session factory, declarative
base, and FastAPI session dependency.

All models must import Base from here and all routers must use get_db() as
their database dependency.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]
"""
Loaded strictly from the environment (or .env via python-dotenv).
Expected format: postgresql://user:password@host:port/dbname
Raises KeyError at startup if the variable is missing — intentional, so the
app never starts silently misconfigured.
"""

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    # Return connections to the pool after each transaction rather than
    # keeping them open indefinitely.
    pool_pre_ping=True,
)
"""
pool_pre_ping=True issues a lightweight SELECT 1 before handing a connection
back from the pool, ensuring stale connections (e.g. after a database restart)
are discarded rather than surfaced as errors inside a request.
"""

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
"""
autocommit=False  — every write must be explicitly committed; accidental writes
                    are never silently persisted.
autoflush=False   — SQLAlchemy will not emit SQL during attribute access;
                    flushes happen only at commit() or explicit flush() calls.
"""

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """
    All ORM models inherit from this class.

    Using the SQLAlchemy 2.x class-based DeclarativeBase rather than the
    legacy declarative_base() factory gives full typing support and is the
    recommended pattern going forward.
    """
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


def get_db():
    """
    Yields a SQLAlchemy Session for the duration of a single request.

    Usage in a router:
        from database import get_db
        from sqlalchemy.orm import Session
        from fastapi import Depends

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...

    The finally block guarantees the session is closed and its connection
    returned to the pool even if an unhandled exception occurs mid-request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
