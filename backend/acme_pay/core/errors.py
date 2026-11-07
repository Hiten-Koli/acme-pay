"""Application errors and their translation into RFC 9457 Problem Details responses."""

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from acme_pay.domain.employment import BusinessRuleViolation

PROBLEM_JSON = "application/problem+json"


class NotFoundError(Exception):
    """The requested resource does not exist."""


class ConflictError(Exception):
    """The request conflicts with existing data, e.g. a duplicate unique value."""


def problem(status: int, detail: str, **extensions: Any) -> JSONResponse:
    """Build a Problem Details response (RFC 9457)."""
    body = {
        "type": "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "detail": detail,
        **extensions,
    }
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON)


def register_error_handlers(app: FastAPI) -> None:
    """Return every error from ``app`` as problem+json."""

    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return problem(HTTPStatus.NOT_FOUND, str(exc))

    @app.exception_handler(ConflictError)
    async def conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return problem(HTTPStatus.CONFLICT, str(exc))

    @app.exception_handler(BusinessRuleViolation)
    async def rule_violation(_: Request, exc: BusinessRuleViolation) -> JSONResponse:
        return problem(HTTPStatus.UNPROCESSABLE_ENTITY, str(exc))

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            {"field": ".".join(str(part) for part in error["loc"][1:]), "message": error["msg"]}
            for error in exc.errors()
        ]
        return problem(HTTPStatus.UNPROCESSABLE_ENTITY, "The request is invalid", errors=errors)

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        return problem(exc.status_code, str(exc.detail))
