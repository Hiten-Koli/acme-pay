"""Provider-neutral port for tool-calling language models.

Adapters (e.g. Gemini) implement ``LLMProvider``; the assistant service only depends on
these types, so switching vendors is a configuration change.
"""

from dataclasses import dataclass
from typing import Any, Protocol

from acme_pay.core.errors import ServiceUnavailableError


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """A function the model may call: name, purpose and JSON-schema parameters."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCall:
    """The model asking to run a tool."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolResult:
    """What running a tool produced (or an ``{"error": ...}`` explanation)."""

    call: ToolCall
    content: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ModelReply:
    """One model turn: text, tool calls, or both."""

    text: str
    calls: list[ToolCall]


class LLMUnavailableError(ServiceUnavailableError):
    """The model provider could not be reached or refused the request (e.g. rate limit)."""


class Conversation(Protocol):
    """A multi-turn exchange with the model; the adapter owns the wire-level history."""

    async def send(self, question: str) -> ModelReply:
        """Send the user's question and return the model's reply."""
        ...

    async def send_results(self, results: list[ToolResult]) -> ModelReply:
        """Return tool results for the model's last calls and get its next reply."""
        ...


class LLMProvider(Protocol):
    """Starts conversations with a tool-calling model."""

    def start(self, *, system: str, tools: list[ToolSpec]) -> Conversation:
        """Begin a conversation with a system instruction and the tools on offer."""
        ...
