"""HTTP endpoints for the AI pay analyst."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from acme_pay.assistant.gemini import GeminiProvider
from acme_pay.assistant.llm import LLMProvider, LLMUnavailableError
from acme_pay.assistant.service import Answer, AssistantService
from acme_pay.core.config import get_settings
from acme_pay.insights.router import Service as Insights

router = APIRouter(prefix="/assistant", tags=["assistant"])

MAX_QUESTION_LENGTH = 500


def get_llm_provider() -> LLMProvider | None:
    """The configured model provider, or ``None`` when no API key is set."""
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)


Provider = Annotated[LLMProvider | None, Depends(get_llm_provider)]


class AskRequest(BaseModel):
    """A pay question in plain language."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class Status(BaseModel):
    """Whether the assistant can be used (the UI hides it otherwise)."""

    enabled: bool


@router.get("/status")
async def status(provider: Provider) -> Status:
    """Report whether a model is configured."""
    return Status(enabled=provider is not None)


@router.post("/ask")
async def ask(request: AskRequest, provider: Provider, insights: Insights) -> Answer:
    """Answer a pay question, with the data it is based on.

    Raises:
        LLMUnavailableError: If no model is configured or the provider fails (HTTP 503).
    """
    if provider is None:
        raise LLMUnavailableError("The AI analyst is not configured")
    return await AssistantService(provider, insights).ask(request.question)
