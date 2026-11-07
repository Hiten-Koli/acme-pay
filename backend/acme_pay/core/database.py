"""Database engine, ORM base, request-scoped sessions and connectivity probe."""

import asyncio
import logging
from collections.abc import AsyncIterator
from enum import StrEnum
from functools import lru_cache
from typing import Any

from sqlalchemy import Enum, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from acme_pay.core.config import get_settings

logger = logging.getLogger(__name__)

PROBE_TIMEOUT_SECONDS = 3
# libpq-style query parameters (as in Neon's connection strings) that asyncpg rejects.
_LIBPQ_ONLY_PARAMS = ("sslmode", "channel_binding")


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def string_enum(enum_type: type[StrEnum], length: int) -> Enum:
    """Store a StrEnum as its plain string values (VARCHAR + CHECK), not a native PG enum.

    Native enums need a migration for every new value; strings plus a CHECK constraint
    keep the same integrity with simpler schema changes.
    """
    return Enum(
        enum_type,
        native_enum=False,
        length=length,
        values_callable=lambda members: [member.value for member in members],
    )


def to_async_url(database_url: str) -> tuple[str, dict[str, Any]]:
    """Adapt a standard PostgreSQL URL for SQLAlchemy's asyncpg driver.

    Args:
        database_url: Any `postgresql://` URL, e.g. copied from the Neon console.

    Returns:
        The asyncpg URL and the `connect_args` that carry its SSL mode.
    """
    url = make_url(database_url).set(drivername="postgresql+asyncpg")
    ssl_mode = url.query.get("sslmode")
    url = url.difference_update_query(_LIBPQ_ONLY_PARAMS)
    connect_args: dict[str, Any] = {"ssl": ssl_mode} if ssl_mode else {}
    return url.render_as_string(hide_password=False), connect_args


@lru_cache
def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, created on first use."""
    url, connect_args = to_async_url(get_settings().database_url)
    return create_async_engine(url, connect_args=connect_args, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the process-wide session factory."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one database session per request (FastAPI dependency)."""
    async with get_session_factory()() as session:
        yield session


async def database_is_reachable() -> bool:
    """Check that the database answers a trivial query within the timeout."""
    try:
        async with asyncio.timeout(PROBE_TIMEOUT_SECONDS), get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError, TimeoutError):
        logger.exception("Database health probe failed")
        return False
    return True
