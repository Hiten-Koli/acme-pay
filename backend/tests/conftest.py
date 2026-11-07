"""Shared pytest configuration."""

import pytest
from hypothesis import settings

# Property tests explore inputs deterministically, so every run checks the same cases.
settings.register_profile("deterministic", derandomize=True)
settings.load_profile("deterministic")


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests on asyncio only (the event loop used in production)."""
    return "asyncio"
