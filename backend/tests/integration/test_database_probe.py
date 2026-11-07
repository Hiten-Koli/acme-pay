"""Requires a running PostgreSQL (`docker compose up -d` locally; a service container in CI)."""

import pytest

from acme_pay.core.database import database_is_reachable

pytestmark = [pytest.mark.anyio, pytest.mark.integration]


async def test_probe_succeeds_against_real_database() -> None:
    assert await database_is_reachable()
