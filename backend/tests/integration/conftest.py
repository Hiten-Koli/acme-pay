"""Integration-test harness: a real PostgreSQL test database, one rolled-back transaction per test.

The test database is the configured database name plus ``_test``. It is created if missing
and migrated once per run, so the tests also prove the migrations work.
"""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from anyio import to_thread
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from acme_pay.assistant.router import get_llm_provider
from acme_pay.core.config import get_settings
from acme_pay.core.database import get_session, to_async_url
from acme_pay.main import create_app

ALEMBIC_INI = Path(__file__).parents[2] / "alembic.ini"


def _test_database_url() -> str:
    url = make_url(get_settings().database_url)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


async def _create_database_if_missing(database_url: str) -> None:
    name = make_url(database_url).database
    admin_url, connect_args = to_async_url(
        make_url(database_url).set(database="postgres").render_as_string(hide_password=False)
    )
    admin = create_async_engine(admin_url, connect_args=connect_args, isolation_level="AUTOCOMMIT")
    async with admin.connect() as connection:
        exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": name}
        )
        if not exists:
            # Identifiers cannot be bound as parameters; the name comes from our own config.
            await connection.execute(text(f'CREATE DATABASE "{name}"'))
    await admin.dispose()


def _migrate(database_url: str) -> None:
    config = Config(str(ALEMBIC_INI))
    config.attributes["database_url"] = database_url
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    database_url = _test_database_url()
    await _create_database_if_missing(database_url)
    await to_thread.run_sync(_migrate, database_url)
    url, connect_args = to_async_url(database_url)
    engine = create_async_engine(url, connect_args=connect_args)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """A session whose commits become savepoints inside a transaction rolled back after the test."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    app = create_app()

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_session
    # Never call a real LLM from tests, whatever keys a developer has configured locally.
    app.dependency_overrides[get_llm_provider] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
