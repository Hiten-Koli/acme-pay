"""The analyst loop, tested with a scripted model so behavior is deterministic and free."""

from typing import Any

import pytest

from acme_pay.assistant.llm import ModelReply, ToolCall, ToolResult, ToolSpec
from acme_pay.assistant.service import AssistantService

pytestmark = pytest.mark.anyio


class ScriptedConversation:
    """Plays back model replies in order and records what it was sent."""

    def __init__(self, replies: list[ModelReply]) -> None:
        self.replies = replies
        self.questions: list[str] = []
        self.results: list[list[ToolResult]] = []

    async def send(self, question: str) -> ModelReply:
        self.questions.append(question)
        return self.replies.pop(0)

    async def send_results(self, results: list[ToolResult]) -> ModelReply:
        self.results.append(results)
        return self.replies.pop(0)


class ScriptedProvider:
    def __init__(self, *replies: ModelReply) -> None:
        self.conversation = ScriptedConversation(list(replies))
        self.tools: list[ToolSpec] = []

    def start(self, *, system: str, tools: list[ToolSpec]) -> ScriptedConversation:
        assert "Never invent" in system
        self.tools = tools
        return self.conversation


class FakeInsights:
    """Stands in for InsightsService; returns fixed aggregates."""

    async def benchmarks(self, job_title: str) -> Any:
        from acme_pay.insights.schemas import Benchmarks

        return Benchmarks(job_title=job_title, countries=[])


def call(name: str, **arguments: Any) -> ToolCall:
    return ToolCall(id=f"call-{name}", name=name, arguments=arguments)


async def test_answers_directly_when_no_data_is_needed() -> None:
    provider = ScriptedProvider(ModelReply(text="Hello! Ask me about pay.", calls=[]))

    answer = await AssistantService(provider, FakeInsights()).ask("hi")  # type: ignore[arg-type]

    assert answer.answer == "Hello! Ask me about pay."
    assert answer.evidence == []


async def test_runs_requested_tools_and_returns_their_results_as_evidence() -> None:
    provider = ScriptedProvider(
        ModelReply(text="", calls=[call("role_pay_by_country", job_title="Data Scientist")]),
        ModelReply(text="Data Scientists are paid most in the US.", calls=[]),
    )

    answer = await AssistantService(provider, FakeInsights()).ask("Where are DS paid most?")  # type: ignore[arg-type]

    assert answer.answer == "Data Scientists are paid most in the US."
    [evidence] = answer.evidence
    assert evidence.tool == "role_pay_by_country"
    assert evidence.arguments == {"job_title": "Data Scientist"}
    assert evidence.result["job_title"] == "Data Scientist"
    [[sent]] = provider.conversation.results
    assert sent.call.id == "call-role_pay_by_country"


async def test_offers_the_model_only_the_registered_tools() -> None:
    provider = ScriptedProvider(ModelReply(text="ok", calls=[]))

    await AssistantService(provider, FakeInsights()).ask("q")  # type: ignore[arg-type]

    assert {tool.name for tool in provider.tools} == {
        "org_pay_summary",
        "role_pay_by_country",
        "salary_distribution",
        "available_filters",
    }


@pytest.mark.parametrize(
    "bad_call",
    [call("drop_table"), call("role_pay_by_country"), call("role_pay_by_country", job_title="")],
)
async def test_reports_bad_tool_calls_back_to_the_model_instead_of_failing(
    bad_call: ToolCall,
) -> None:
    provider = ScriptedProvider(
        ModelReply(text="", calls=[bad_call]),
        ModelReply(text="Sorry, I could not look that up.", calls=[]),
    )

    answer = await AssistantService(provider, FakeInsights()).ask("q")  # type: ignore[arg-type]

    [[result]] = provider.conversation.results
    assert "error" in result.content
    assert answer.evidence == []
    assert answer.answer == "Sorry, I could not look that up."


async def test_stops_after_a_bounded_number_of_tool_rounds() -> None:
    looping = ModelReply(text="", calls=[call("role_pay_by_country", job_title="QA Engineer")])
    provider = ScriptedProvider(*[looping] * 10)

    answer = await AssistantService(provider, FakeInsights()).ask("q")  # type: ignore[arg-type]

    assert len(provider.conversation.results) <= 4
    assert "could not" in answer.answer.lower()
