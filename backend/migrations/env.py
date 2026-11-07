"""Alembic environment: runs migrations online over the async engine."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from acme_pay.core.config import get_settings
from acme_pay.core.database import Base, to_async_url
from acme_pay.models import register_models

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

register_models()
target_metadata = Base.metadata


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def _run_online() -> None:
    # Tests pass their own database via config.attributes; otherwise use DATABASE_URL.
    database_url = config.attributes.get("database_url") or get_settings().database_url
    url, connect_args = to_async_url(database_url)
    engine = create_async_engine(url, connect_args=connect_args, poolclass=NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(_run)
    await engine.dispose()


if context.is_offline_mode():
    raise SystemExit("Offline (SQL script) migrations are not supported; run against a database.")
asyncio.run(_run_online())
