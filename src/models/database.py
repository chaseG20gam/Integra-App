from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base

# default SQLite path; can be overridden via configuration.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"

_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def get_engine(url: str | None = None) -> Engine:
    # create (or return cached) SQLAlchemy engine
    global _engine
    if _engine is None:
        database_url = url or f"sqlite:///{DEFAULT_DB_PATH}"
        if database_url.startswith("sqlite"):
            DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(database_url, echo=False, future=True)
    return _engine


def init_database(url: str | None = None) -> None:
    # initialize database by creating all tables
    engine = get_engine(url=url)
    Base.metadata.create_all(engine)


def get_session_factory(url: str | None = None) -> sessionmaker[Session]:
    # return a session factory bound to the engine
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine(url=url)
        _SessionFactory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return _SessionFactory


@contextmanager
def session_scope(url: str | None = None) -> Iterator[Session]:
    # provide a transactional scope around a series of operations
    session_factory = get_session_factory(url=url)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
