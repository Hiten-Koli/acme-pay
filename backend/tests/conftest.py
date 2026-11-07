"""Shared pytest configuration."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on asyncio only (the event loop used in production)."""
    return "asyncio"
