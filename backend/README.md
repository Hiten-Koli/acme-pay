# ACME Pay: backend

FastAPI service for ACME Pay. See the [root README](../README.md) for the full picture and [ADR 0002](../docs/adr/0002-backend-fastapi-sqlalchemy.md) for the architecture.

## Commands
Run from `backend/`:

```bash
uv sync                    # install dependencies into .venv
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy                # strict type check
uv run pytest              # tests
```
