"""
Database connection and session management.
"""

import logging
import time
from contextvars import ContextVar, Token
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from api.config import get_settings

settings = get_settings()
logger = logging.getLogger("api.database")

_request_db_metrics: ContextVar[dict | None] = ContextVar("request_db_metrics", default=None)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_use_lifo=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def start_request_db_metrics() -> Token:
    """Initialize per-request DB metrics context."""
    return _request_db_metrics.set({"query_count": 0, "query_time_ms": 0.0})


def get_request_db_metrics() -> dict:
    """Return current request DB metrics, if initialized."""
    metrics = _request_db_metrics.get()
    if metrics is None:
        return {"query_count": 0, "query_time_ms": 0.0}
    return metrics


def reset_request_db_metrics(token: Token) -> None:
    """Reset request DB metrics context to previous state."""
    _request_db_metrics.reset(token)


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time for metrics."""
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Accumulate query execution duration into request metrics."""
    start_times = conn.info.get("query_start_time", [])
    if not start_times:
        return

    start_time = start_times.pop()
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    metrics = _request_db_metrics.get()
    if metrics is not None:
        metrics["query_count"] += 1
        metrics["query_time_ms"] += elapsed_ms


@event.listens_for(Engine, "handle_error")
def handle_engine_error(exception_context):
    """Log disconnection events so they are visible in Docker logs."""
    if exception_context.is_disconnect:
        logger.warning("Database disconnect detected. The connection will be recycled.")

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database session error")
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Error while closing database session")
