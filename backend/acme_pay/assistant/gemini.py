"""Gemini adapter (generateContent REST API with function calling)."""

import logging
from typing import Any

import httpx

from acme_pay.assistant.llm import (
    LLMUnavailableError,
    ModelReply,
    ToolCall,
    ToolResult,
    ToolSpec,
)

logger = logging.getLogger(__name__)

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
REQUEST_TIMEOUT_SECONDS = 30


class GeminiConversation:
    """Keeps the wire-format history of one conversation.

    Model turns are stored exactly as received, because Gemini requires thought
    signatures to be returned unchanged in the part they came in.
    """

    def __init__(self, provider: "GeminiProvider", system: str, tools: list[ToolSpec]) -> None:
        self._provider = provider
        self._system = system
        self._tools = tools
        self._contents: list[dict[str, Any]] = []

    async def send(self, question: str) -> ModelReply:
        """Send the user's question."""
        self._contents.append({"role": "user", "parts": [{"text": question}]})
        return await self._generate()

    async def send_results(self, results: list[ToolResult]) -> ModelReply:
        """Answer all of the model's calls from its last turn, in one user turn."""
        parts = [
            {
                "functionResponse": {
                    "id": result.call.id,
                    "name": result.call.name,
                    "response": result.content,
                }
            }
            for result in results
        ]
        self._contents.append({"role": "user", "parts": parts})
        return await self._generate()

    async def _generate(self) -> ModelReply:
        body = {
            "systemInstruction": {"parts": [{"text": self._system}]},
            "contents": self._contents,
            "tools": [
                {
                    "functionDeclarations": [
                        {"name": t.name, "description": t.description, "parameters": t.parameters}
                        for t in self._tools
                    ]
                }
            ],
        }
        content = await self._provider.generate(body)
        self._contents.append(content)
        return _parse(content)


def _parse(content: dict[str, Any]) -> ModelReply:
    texts: list[str] = []
    calls: list[ToolCall] = []
    for index, part in enumerate(content.get("parts", [])):
        if "text" in part and not part.get("thought"):
            texts.append(part["text"])
        if call := part.get("functionCall"):
            calls.append(
                ToolCall(
                    id=call.get("id") or f"call-{index}",
                    name=call["name"],
                    arguments=call.get("args") or {},
                )
            )
    return ModelReply(text="".join(texts), calls=calls)


class GeminiProvider:
    """Talks to the Gemini API with an API key."""

    def __init__(self, *, api_key: str, model: str, client: httpx.AsyncClient | None = None):
        self._api_key = api_key
        self._model = model
        self._client = client or httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)

    def start(self, *, system: str, tools: list[ToolSpec]) -> GeminiConversation:
        """Begin a conversation."""
        return GeminiConversation(self, system, tools)

    async def generate(self, body: dict[str, Any]) -> dict[str, Any]:
        """Call generateContent and return the first candidate's content.

        Raises:
            LLMUnavailableError: On network errors, non-success statuses or empty replies.
        """
        url = f"{API_BASE}/models/{self._model}:generateContent"
        try:
            response = await self._client.post(
                url, json=body, headers={"x-goog-api-key": self._api_key}
            )
            response.raise_for_status()
            content: dict[str, Any] = response.json()["candidates"][0]["content"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as error:
            # Never log the request: it may contain the API key header.
            logger.warning("Gemini request failed: %s", type(error).__name__)
            raise LLMUnavailableError("The AI model is unavailable right now") from error
        return content
