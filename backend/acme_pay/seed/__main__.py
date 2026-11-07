"""Seed the configured database: ``uv run python -m acme_pay.seed [--employees N]``."""

import argparse
import asyncio
import logging
import time

from acme_pay.core.database import get_engine
from acme_pay.seed.generator import DEFAULT_SEED, generate
from acme_pay.seed.loader import load

DEFAULT_EMPLOYEES = 10_000

logger = logging.getLogger("acme_pay.seed")


async def _seed(employees: int, seed: int) -> None:
    started = time.perf_counter()
    dataset = generate(employees, seed)
    async with get_engine().begin() as connection:
        await load(connection, dataset)
    logger.info(
        "Seeded %d employees and %d salary changes in %.1fs",
        len(dataset.employees),
        len(dataset.changes),
        time.perf_counter() - started,
    )


def main() -> None:
    """Parse arguments and replace the database contents with a generated dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--employees", type=int, default=DEFAULT_EMPLOYEES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(_seed(args.employees, args.seed))


if __name__ == "__main__":
    main()
