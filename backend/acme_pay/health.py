"""Health endpoint for uptime checks and the post-deploy smoke test."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from acme_pay.core.database import database_is_reachable

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Service health summary."""

    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable"]


@router.get("/health")
async def health(
    response: Response,
    database_ok: Annotated[bool, Depends(database_is_reachable)],
) -> HealthStatus:
    """Report whether the API and its database are working."""
    if database_ok:
        return HealthStatus(status="ok", database="ok")
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthStatus(status="degraded", database="unavailable")
