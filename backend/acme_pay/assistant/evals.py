"""Golden-question evals for the AI analyst, run against the live model on demand.

Usage (needs GEMINI_API_KEY and a seeded database):
    uv run python -m acme_pay.assistant.evals

Each case checks that the model reaches for the right tool with the right arguments. This
measures tool choice, the part that decides whether answers are grounded. CI runs a
consistency check on the golden set itself; live runs cost API calls, so they are manual.
"""

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from typing import Any

from acme_pay.assistant.llm import ToolCall, ToolResult
from acme_pay.assistant.router import get_llm_provider
from acme_pay.assistant.service import SYSTEM_PROMPT
from acme_pay.assistant.tools import TOOLS
from acme_pay.core.database import get_session_factory
from acme_pay.insights.service import InsightsService

logger = logging.getLogger("acme_pay.evals")
MAX_ROUNDS = 3


@dataclass(frozen=True)
class GoldenCase:
    """A question and the tool call a correct analyst must make while answering it."""

    question: str
    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)


GOLDEN: list[GoldenCase] = [
    GoldenCase("What is our total annual payroll in USD?", "org_pay_summary"),
    GoldenCase("How many people are paid below their pay band?", "org_pay_summary"),
    GoldenCase("Which country has the most employees?", "org_pay_summary"),
    GoldenCase(
        "What's the median salary for Data Scientists in Germany vs the UK?",
        "role_pay_by_country",
        {"job_title": "Data Scientist"},
    ),
    GoldenCase(
        "Where do we pay software engineers the most?",
        "role_pay_by_country",
        {"job_title": "Software Engineer"},
    ),
    GoldenCase("How are salaries spread out in India?", "salary_distribution", {"country": "IN"}),
    GoldenCase(
        "Show me the pay distribution for the Sales department.",
        "salary_distribution",
        {"department": "Sales"},
    ),
]


def matches(case: GoldenCase, call: ToolCall) -> bool:
    """Whether ``call`` is the expected tool with (at least) the expected arguments."""
    return call.name == case.tool and all(
        str(call.arguments.get(key, "")).lower() == str(value).lower()
        for key, value in case.arguments.items()
    )


async def _run_case(case: GoldenCase, insights: InsightsService) -> bool:
    provider = get_llm_provider()
    if provider is None:
        raise SystemExit("Set GEMINI_API_KEY to run the live evals.")
    conversation = provider.start(system=SYSTEM_PROMPT, tools=[t.spec for t in TOOLS.values()])
    reply = await conversation.send(case.question)
    for _ in range(MAX_ROUNDS):
        if any(matches(case, call) for call in reply.calls):
            return True
        if not reply.calls:
            return False
        results = []
        for call in reply.calls:
            tool = TOOLS.get(call.name)
            content = await tool.execute(insights, call.arguments) if tool else {"error": "unknown"}
            results.append(ToolResult(call, content))
        reply = await conversation.send_results(results)
    return False


async def _main() -> int:
    passed = 0
    async with get_session_factory()() as session:
        insights = InsightsService(session)
        for case in GOLDEN:
            ok = await _run_case(case, insights)
            passed += ok
            logger.info("%s  %s", "PASS" if ok else "FAIL", case.question)
    logger.info("%d/%d golden questions passed", passed, len(GOLDEN))
    return 0 if passed == len(GOLDEN) else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(asyncio.run(_main()))
