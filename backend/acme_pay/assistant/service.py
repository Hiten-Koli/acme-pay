"""The analyst loop: ask the model, run the tools it chooses, answer with evidence."""

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from acme_pay.assistant.llm import LLMProvider, ToolCall, ToolResult
from acme_pay.assistant.tools import TOOLS
from acme_pay.insights.service import InsightsService

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 4
GAVE_UP = "I could not complete that analysis. Try asking a narrower question."

SYSTEM_PROMPT = """\
You are ACME Pay's pay analyst. You help an HR manager understand how ACME pays its
active employees across countries.

Rules:
- Answer only from tool results. Never invent numbers; if the tools cannot answer, say so.
- Map the user's wording to exact countries, departments and job titles with
  available_filters before using them.
- Always name the currency. USD figures come from dated FX rates.
- "Below/above band" means a compa-ratio under 0.80 or over 1.20 against the median for
  the same job title in the same country.
- You cannot see individual employees; offer to point HR to the People page instead.
- Answer in 2-4 plain sentences for a non-technical reader. No tables or markdown.
"""


class Evidence(BaseModel):
    """One tool call the answer is based on, with the data it returned."""

    tool: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class Answer(BaseModel):
    """The analyst's answer and the evidence behind it."""

    answer: str
    evidence: list[Evidence]


class AssistantService:
    """Answers pay questions using only registered, aggregate-only tools."""

    def __init__(self, provider: LLMProvider, insights: InsightsService) -> None:
        self._provider = provider
        self._insights = insights

    async def ask(self, question: str) -> Answer:
        """Answer ``question``.

        Raises:
            LLMUnavailableError: If the model provider cannot be used.
        """
        conversation = self._provider.start(
            system=SYSTEM_PROMPT, tools=[tool.spec for tool in TOOLS.values()]
        )
        reply = await conversation.send(question)
        evidence: list[Evidence] = []
        for _ in range(MAX_TOOL_ROUNDS):
            if not reply.calls:
                return Answer(answer=reply.text.strip() or GAVE_UP, evidence=evidence)
            results = [await self._execute(call, evidence) for call in reply.calls]
            reply = await conversation.send_results(results)
        if reply.calls:
            logger.info("Assistant stopped after %d tool rounds", MAX_TOOL_ROUNDS)
            return Answer(answer=GAVE_UP, evidence=evidence)
        return Answer(answer=reply.text.strip() or GAVE_UP, evidence=evidence)

    async def _execute(self, call: ToolCall, evidence: list[Evidence]) -> ToolResult:
        tool = TOOLS.get(call.name)
        if tool is None:
            return ToolResult(call, {"error": f"Unknown tool {call.name!r}"})
        try:
            data = await tool.execute(self._insights, call.arguments)
        except ValidationError as error:
            return ToolResult(call, {"error": f"Invalid arguments: {error.errors()[0]['msg']}"})
        evidence.append(Evidence(tool=call.name, arguments=call.arguments, result=data))
        return ToolResult(call, data)
