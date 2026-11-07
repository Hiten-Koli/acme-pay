"""Application entry point: builds the FastAPI app."""

from fastapi import FastAPI

from acme_pay import health

API_PREFIX = "/api"


def create_app() -> FastAPI:
    """Create and configure the ACME Pay API application."""
    app = FastAPI(
        title="ACME Pay API",
        version="0.1.0",
        docs_url=f"{API_PREFIX}/docs",
        openapi_url=f"{API_PREFIX}/openapi.json",
    )
    app.include_router(health.router, prefix=API_PREFIX)
    return app


app = create_app()
